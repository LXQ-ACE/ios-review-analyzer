from pydantic import BaseModel,Field
from typing import List

class SingleReviewItem(BaseModel):
    sentiment:str=Field(description="情感：正面/负面/中性")
    problem_category:str=Field(description="问题分类，如闪退、加载慢、功能缺失、UI问题")
    priority:str=Field(description="优先级 高/中/低")
    evidence:str=Field(description="从原评论截取证据片段")

class AnalysisResult(BaseModel):
    item_list:List[SingleReviewItem]
    global_summary:str
    top3_problems:List[str]

class PRDResult(BaseModel):
    requirement_title:str
    background:str
    function_desc:str
    priority:str
    acceptance_criteria:List[str]

class TestCaseResult(BaseModel):
    case_title:str
    precondition:str
    operation_step:List[str]
    expect_result:str
