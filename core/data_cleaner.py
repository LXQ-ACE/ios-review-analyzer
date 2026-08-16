"""
数据清洗模块
负责评论数据的质量校验与清洗，输出标准化数据集与统计指标
清洗流程：ID去重 → 空内容过滤 → 短文本剔除 → 相似度去重
"""
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from config.settings import DataConfig


def clean_review_data(raw_df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    执行完整的数据清洗流水线
    
    Args:
        raw_df: 原始评论数据
        
    Returns:
        (清洗后DataFrame, 清洗统计信息字典)
    """
    if raw_df.empty:
        return raw_df, {}
    
    df = raw_df.copy()
    # 初始化统计指标
    stats = {
        "raw_count": len(df),
        "duplicate_removed": 0,
        "empty_removed": 0,
        "short_removed": 0,
        "similar_removed": 0,
        "final_count": 0
    }
    
    # ---------- 第1层：按评论ID去重 ----------
    before = len(df)
    df = df.drop_duplicates(subset=["review_id"], keep="first")
    stats["duplicate_removed"] = before - len(df)
    
    # ---------- 第2层：剔除空内容评论 ----------
    before = len(df)
    df = df[df["content"].notna() & (df["content"].str.strip() != "")]
    stats["empty_removed"] = before - len(df)
    
    # ---------- 第3层：剔除过短的无效水评论 ----------
    before = len(df)
    df = df[df["content"].str.len() >= DataConfig.MIN_CONTENT_LENGTH]
    stats["short_removed"] = before - len(df)
    
    # ---------- 第4层：基于文本相似度去重 ----------
    before = len(df)
    df = _similarity_dedup(df)
    stats["similar_removed"] = before - len(df)
    
    # 重置索引并输出最终数量
    df = df.reset_index(drop=True)
    stats["final_count"] = len(df)
    
    return df, stats


def _similarity_dedup(df: pd.DataFrame) -> pd.DataFrame:
    """
    基于 TF-IDF + 余弦相似度 的文本去重
    去除高度雷同的重复评论，避免干扰AI分析结论
    """
    if len(df) < 2:
        return df
    
    contents = df["content"].tolist()
    
    try:
        # 向量化
        vectorizer = TfidfVectorizer(max_features=1000, stop_words="english")
        tfidf_matrix = vectorizer.fit_transform(contents)
        # 计算余弦相似度矩阵
        sim_matrix = cosine_similarity(tfidf_matrix)
    except Exception:
        # 向量化失败直接返回原数据，不中断流程
        return df
    
    # 标记需要删除的重复项（保留第一条，删除后续重复项）
    to_remove = set()
    for i in range(len(contents)):
        if i in to_remove:
            continue
        for j in range(i + 1, len(contents)):
            if j in to_remove:
                continue
            if sim_matrix[i][j] >= DataConfig.SIMILARITY_THRESHOLD:
                to_remove.add(j)
    
    # 过滤保留项
    keep_indices = [i for i in range(len(df)) if i not in to_remove]
    return df.iloc[keep_indices]


def get_rating_distribution(df: pd.DataFrame) -> dict:
    """
    计算评分分布统计（1-5星数量与占比、平均分）
    """
    if df.empty:
        return {}
    
    rating_counts = df["rating"].value_counts().sort_index()
    total = len(df)
    
    distribution = {}
    for star in range(1, 6):
        count = int(rating_counts.get(star, 0))
        distribution[f"{star}星"] = {
            "count": count,
            "ratio": round(count / total * 100, 1) if total > 0 else 0
        }
    
    distribution["平均评分"] = round(df["rating"].mean(), 2) if total > 0 else 0
    return distribution
