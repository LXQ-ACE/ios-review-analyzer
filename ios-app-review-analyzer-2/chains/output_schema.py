from pydantic import BaseModel, Field
from typing import List

class SingleReviewResult(BaseModel):
    sentiment: str = Field(description="情感分类：正面 / 负面 / 中性")
    problem_type: str = Field(description="问题类型，例如闪退、UI卡顿、功能缺失、体验问题等")
    priority: str = Field(description="优先级：高 / 中 / 低")
    evidence: str = Field(description="从原评论提取出对应的证据原文片段")


class BatchAnalysisOutput(BaseModel):
    analysis_list: List[SingleReviewResult]
    summary: str = Field(description="全部评论的整体总结")
    top_problems: List[str] = Field(description="排名前3高频问题")
