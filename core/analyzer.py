"""
AI 分析核心模块
包含评论语义分析、PRD生成、测试用例生成三大核心能力
"""
import pandas as pd
from core.schemas import ReviewAnalysisResult, PRDResult, TestCaseResult
from core.llm_client import get_llm_client
from utils.cache import get_cache, set_cache, build_cache_key


def analyze_reviews(df: pd.DataFrame, max_samples: int = 100) -> ReviewAnalysisResult:
    """
    评论语义分析主入口
    """
    if df.empty:
        raise ValueError("评论数据为空，无法进行分析")
    
    sample_df = df.head(max_samples).copy()
    
    # 构建缓存键
    content_str = "".join(sample_df["content"].astype(str).tolist())
    cache_key = build_cache_key("analysis", content_str[:500])
    
    # 读取缓存
    cached = get_cache(cache_key)
    if cached:
        print("命中分析缓存，直接返回")
        return ReviewAnalysisResult.model_validate_json(cached)
    
    # 格式化评论数据
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
4. 检测是否存在矛盾反馈
5. 所有结论必须基于评论内容，不得凭空臆造
6. 严格按照指定的 JSON 结构输出
"""
    
    user_prompt = f"""
以下是用户评论数据，请进行深度语义分析：

{reviews_input}

请输出完整的分析结果，包括整体总结、核心痛点、核心好评、动态分类、矛盾反馈点。
"""
    
    # 调用大模型
    llm = get_llm_client()
    result = llm.structured_completion(
        system_prompt,
        user_prompt,
        output_schema=ReviewAnalysisResult
    )
    
    # 写入缓存
    set_cache(cache_key, result.model_dump_json())
    return result


def generate_prd(analysis_result: ReviewAnalysisResult) -> PRDResult:
    """
    基于语义分析结果，生成产品需求文档（PRD）
    """
    # 缓存键
    cache_key = build_cache_key("prd", analysis_result.overall_summary)
    
    cached = get_cache(cache_key)
    if cached:
        print("命中PRD缓存，直接返回")
        return PRDResult.model_validate_json(cached)
    
    analysis_json = analysis_result.model_dump_json(indent=2)
    
    system_prompt = """
你是一名资深产品经理，擅长基于用户反馈输出产品需求规划。
请基于用户评论分析结果，输出分版本的产品需求规划方案。

【输出要求】
1. 先输出产品背景与问题分析
2. 规划2-3个迭代版本，每个版本有明确的核心目标
3. 每个版本下输出具体需求，包含需求标题、描述、优先级、用户价值
4. 优先级分为 P0（必须做）、P1（重要）、P2（一般）、P3（可选）
5. 每条需求必须关联原始问题点和来源评论ID，保证可追溯
6. 严格按照指定的 JSON 结构输出
"""
    
    user_prompt = f"""
以下是用户评论分析结果，请基于此生成产品需求规划方案：

{analysis_json}

请输出分版本的需求规划，覆盖核心痛点优化和体验提升。
"""
    
    llm = get_llm_client()
    result = llm.structured_completion(
        system_prompt,
        user_prompt,
        output_schema=PRDResult
    )
    
    set_cache(cache_key, result.model_dump_json())
    return result


def generate_test_cases(prd_result: PRDResult) -> TestCaseResult:
    """
    基于PRD需求，生成对应的测试用例
    """
    cache_key = build_cache_key("testcase", prd_result.product_background[:200])
    
    cached = get_cache(cache_key)
    if cached:
        print("命中测试用例缓存，直接返回")
        return TestCaseResult.model_validate_json(cached)
    
    # 提取所有需求点
    all_reqs = []
    for plan in prd_result.version_plans:
        for req in plan.requirements:
            all_reqs.append({
                "title": req.req_title,
                "desc": req.req_desc,
                "priority": req.priority
            })
    
    reqs_text = "\n".join([f"[{r['priority']}] {r['title']}: {r['desc']}" for r in all_reqs])
    
    system_prompt = """
你是一名资深测试工程师，擅长根据产品需求设计功能测试用例。
请基于给定的产品需求列表，输出完整的测试用例集。

【输出要求】
1. 每条需求对应至少1条测试用例
2. 每条用例包含：用例标题、前置条件、测试步骤、预期结果、用例级别
3. 用例级别分为：高（核心功能）、中（重要功能）、低（边缘功能）
4. 测试步骤要清晰可执行，预期结果要明确可验证
5. 严格按照指定的 JSON 结构输出
"""
    
    user_prompt = f"""
以下是产品需求列表，请为每条需求设计对应的测试用例：

{reqs_text}

请输出完整的测试用例集合。
"""
    
    llm = get_llm_client()
    result = llm.structured_completion(
        system_prompt,
        user_prompt,
        output_schema=TestCaseResult
    )
    
    set_cache(cache_key, result.model_dump_json())
    return result
