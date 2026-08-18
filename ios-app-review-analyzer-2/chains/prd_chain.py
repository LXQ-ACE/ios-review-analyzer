from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from config.settings import settings
from chains.output_schema import PRDResult

llm=ChatOpenAI(
    base_url=settings.llm_base_url,
    api_key=settings.llm_api_key,
    model=settings.llm_model_name,
    temperature=0.2
)
parser=PydanticOutputParser(pydantic_object=PRDResult)
prompt=ChatPromptTemplate.from_messages([
    ("system","""
基于用户评论分析报告，生成一份标准产品需求PRD
包含需求标题、需求背景、功能描述、优先级、验收标准
{format_instructions}
"""),
    ("human","分析报告内容：\n{summary_text}")
])
prd_chain=prompt.partial(format_instructions=parser.get_format_instructions())|llm|parser
