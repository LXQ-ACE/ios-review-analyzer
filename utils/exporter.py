"""
导出工具模块
支持将分析结果、PRD、测试用例导出为标准格式文件
"""
import pandas as pd
from io import BytesIO, StringIO
from core.schemas import ReviewAnalysisResult, PRDResult, TestCaseResult


def df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    """DataFrame 导出为 CSV 字节流"""
    output = BytesIO()
    df.to_csv(output, index=False, encoding="utf-8-sig")
    output.seek(0)
    return output.getvalue()


def analysis_to_markdown(result: ReviewAnalysisResult) -> str:
    """语义分析结果导出为 Markdown 报告"""
    md = "# AI 评论语义分析报告\n\n"
    
    md += "## 一、整体评论总结\n\n"
    md += f"{result.overall_summary}\n\n"
    
    md += "## 二、核心痛点 Top5\n\n"
    for i, point in enumerate(result.core_pain_points, 1):
        md += f"{i}. {point}\n"
    md += "\n"
    
    md += "## 三、核心好评 Top5\n\n"
    for i, point in enumerate(result.core_praise_points, 1):
        md += f"{i}. {point}\n"
    md += "\n"
    
    if result.contradiction_points:
        md += "## 四、矛盾反馈识别\n\n"
        for i, point in enumerate(result.contradiction_points, 1):
            md += f"{i}. {point}\n"
        md += "\n"
    
    md += "## 五、分类主题详情\n\n"
    for cat in result.categories:
        md += f"### {cat.category_name}（{cat.priority}优先级）\n\n"
        md += f"**说明**：{cat.category_desc}\n\n"
        md += f"共 {cat.issue_count} 个问题点：\n\n"
        for idx, issue in enumerate(cat.issues, 1):
            md += f"{idx}. **{issue.issue_summary}**\n"
            md += f"   - 情感倾向：{issue.sentiment}\n"
            md += f"   - 证据等级：{issue.evidence_level}（{issue.evidence_count}条提及）\n"
            if issue.is_contradictory and issue.contradictory_note:
                md += f"   - 矛盾说明：{issue.contradictory_note}\n"
            md += "\n"
    
    return md


def prd_to_markdown(result: PRDResult) -> str:
    """PRD 导出为 Markdown 文档"""
    md = "# 产品需求文档 (PRD)\n\n"
    
    md += "## 一、产品背景与问题分析\n\n"
    md += f"{result.product_background}\n\n"
    
    md += "## 二、分版本需求规划\n\n"
    for plan in result.version_plans:
        md += f"### {plan.version_name}\n\n"
        md += f"**核心目标**：{plan.version_goal}\n\n"
        md += "| 优先级 | 需求名称 | 需求描述 | 用户价值 |\n"
        md += "| ------ | -------- | -------- | -------- |\n"
        for req in plan.requirements:
            title = req.req_title.replace("|", "｜")
            desc = req.req_desc.replace("|", "｜")
            value = req.user_value.replace("|", "｜")
            md += f"| {req.priority} | {title} | {desc} | {value} |\n"
        md += "\n"
        
        for req in plan.requirements:
            md += f"#### {req.req_title}（{req.priority}）\n\n"
            md += f"- **需求描述**：{req.req_desc}\n"
            md += f"- **用户价值**：{req.user_value}\n"
            md += f"- **对应问题**：{req.related_issue}\n"
            md += "\n"
    
    return md


def testcase_to_markdown(result: TestCaseResult) -> str:
    """测试用例导出为 Markdown 文档"""
    md = "# 测试用例集\n\n"
    md += f"共 {result.total_count} 条测试用例\n\n"
    
    for i, case in enumerate(result.test_cases, 1):
        md += f"## 用例 {i}：{case.case_title}（{case.case_level}级别）\n\n"
        md += f"- **前置条件**：{case.precondition}\n"
        md += f"- **对应需求**：{case.related_requirement}\n\n"
        md += "**测试步骤**：\n"
        for step in case.test_steps:
            md += f"{step}\n"
        md += "\n"
        md += f"**预期结果**：{case.expected_result}\n\n"
        md += "---\n\n"
    
    return md


def full_report_markdown(analysis: ReviewAnalysisResult, 
                          prd: PRDResult, 
                          test: TestCaseResult) -> str:
    """生成完整的全流程分析报告"""
    report = "# iOS App 评论全链路分析报告\n\n"
    report += "---\n\n"
    report += analysis_to_markdown(analysis)
    report += "\n---\n\n"
    report += prd_to_markdown(prd)
    report += "\n---\n\n"
    report += testcase_to_markdown(test)
    return report


def string_to_bytes(text: str) -> bytes:
    """字符串转字节流，用于下载"""
    return text.encode("utf-8")
