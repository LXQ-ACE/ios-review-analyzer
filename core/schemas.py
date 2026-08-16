"""
数据结构定义模块
使用 Pydantic 严格定义所有AI输出的数据结构，保证格式稳定可解析
"""
from pydantic import BaseModel, Field
from typing import List, Optional


# ==============================================
# 语义分类相关结构
# ==============================================
class IssueItem(BaseModel):
    """单条问题点"""
    issue_summary: str = Field(description="问题点摘要，一句话概括")
    evidence_count: int = Field(description="提及该问题的评论数量，即证据样本数")
    evidence_level: str = Field(description="证据等级：充足/样本有限/个别提及")
    sentiment: str = Field(description="情感倾向：负面/中性/正面")
    review_ids: List[str] = Field(description="关联的评论ID列表，用于追溯")
    is_contradictory: bool = Field(default=False, description="是否存在矛盾反馈")
    contradictory_note: Optional[str] = Field(default=None, description="矛盾点说明")


class CategoryResult(BaseModel):
    """单个分类主题"""
    category_name: str = Field(description="分类主题名称，动态生成")
    category_desc: str = Field(description="该分类的简要说明")
    priority: str = Field(description="优先级：高/中/低")
    issue_count: int = Field(description="该分类下的问题点总数")
    issues: List[IssueItem] = Field(description="具体问题点列表")


class ReviewAnalysisResult(BaseModel):
    """评论语义分析完整结果"""
    overall_summary: str = Field(description="整体评论总结，200字以内")
    core_pain_points: List[str] = Field(description="Top5核心痛点")
    core_praise_points: List[str] = Field(description="Top5核心好评点")
    categories: List[CategoryResult] = Field(description="动态生成的分类主题列表")
    contradiction_points: List[str] = Field(description="识别出的矛盾反馈点")


# ==============================================
# PRD 相关结构
# ==============================================
class RequirementItem(BaseModel):
    """单条产品需求"""
    req_title: str = Field(description="需求标题")
    req_desc: str = Field(description="需求详细描述")
    priority: str = Field(description="优先级：P0/P1/P2/P3")
    user_value: str = Field(description="用户价值说明")
    related_issue: str = Field(description="对应原始问题点")
    source_review_ids: List[str] = Field(description="来源评论ID列表")


class VersionPlan(BaseModel):
    """单个版本规划"""
    version_name: str = Field(description="版本名称，如 V1.1 体验优化版")
    version_goal: str = Field(description="本版本核心目标")
    requirements: List[RequirementItem] = Field(description="本版本包含的需求列表")


class PRDResult(BaseModel):
    """PRD生成结果"""
    product_background: str = Field(description="产品背景与问题分析")
    version_plans: List[VersionPlan] = Field(description="分版本需求规划")


# ==============================================
# 测试用例相关结构
# ==============================================
class TestCaseItem(BaseModel):
    """单条测试用例"""
    case_title: str = Field(description="用例标题")
    precondition: str = Field(description="前置条件")
    test_steps: List[str] = Field(description="测试步骤")
    expected_result: str = Field(description="预期结果")
    case_level: str = Field(description="用例级别：高/中/低")
    related_requirement: str = Field(description="对应需求点")


class TestCaseResult(BaseModel):
    """测试用例集合"""
    total_count: int = Field(description="用例总数")
    test_cases: List[TestCaseItem] = Field(description="测试用例列表")
