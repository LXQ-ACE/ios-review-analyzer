"""
AI 语义分析模块
基于大模型对评论进行分类、痛点识别、矛盾检测
"""
import pandas as pd
from core.schemas import ReviewAnalysisResult
from core.llm_client import get_llm_client
from utils.cache import get_cache, set_cache, build_cache_key


def analyze_reviews(df: pd.DataFrame, max_samples: int = 100) -> ReviewAnalysisResult:
    """
    评论语义分析主入口
    
    Args:
        df: 标准化后的评论数据
        max_samples: 最多送入模型的评论数量，控制成本
        
    Returns:
        结构化的分析结果
    """
    if df.empty:
        raise ValueError("评论数据为空，无法进行分析")
    
    # 数据采样：取最新的N条，避免token过长
    sample_df = df.head(max_samples).copy()
    
    # 构建缓存键：基于评论内容哈希
    content_str = "".join(sample_df["content"].astype(str).tolist())
    cache_key = build_cache_key("analysis", content_str[:500])
    
    # 尝试读取缓存
    cached = get_cache(cache_key)
    if cached:
        print("命中分析缓存，直接返回")
        return ReviewAnalysisResult.model_validate_json(cached)
    
    # 格式化评论数据为文本
    review_texts = []
    for idx, row in sample_df.iterrows():
        rid = row.get("review_id", f"r{idx}")
        rating = row.get("rating", 0)
        content = str(row.get("content", "")).strip()
        if content:
            review_texts.append(f"[评论ID:{rid}] [评分:{rating}] {content}")
    
    reviews_input = "\n".join(review_texts)
    
    system_prompt = """
你是一名专业的用户体验分析师，擅长从用户评论中提炼产品问题、识别痛点、发现矛盾反馈。
请基于给定的App Store用户评论，进行深度语义分析。

【分析要求】
1. 动态生成分类主题，不要使用固定分类，根据评论内容自动归纳
2. 每个分类下提炼具体的问题点，标注提及数量和证据等级
3. 识别用户的核心痛点和核心好评点
4. 检测是否存在矛盾反馈（如同一功能有人夸有人骂）
5. 所有结论必须基于评论内容，不得凭空臆造
6. 严格按照指定的 JSON 结构输出
"""
    
    user_prompt = f"""
以下是某健身类App的用户评论数据，请进行深度语义分析：

{reviews_input}

请输出完整的分析结果，包括整体总结、核心痛点、核心好评、动态分类、矛盾反馈点。
"""
    
    # 调用大模型结构化输出
    llm = get_llm_client()
    result = llm.structured_completion(
        system_prompt,
        user_prompt,
        output_schema=ReviewAnalysisResult
    )
    
    # 写入缓存
    set_cache(cache_key, result.model_dump_json())
    return result
