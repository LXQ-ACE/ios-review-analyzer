from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from config.settings import settings
from chains.output_schema import AnalysisResult

llm=ChatOpenAI(
    base_url=settings.llm_base_url,
    api_key=settings.llm_api_key,
    model=settings.llm_model_name,
    temperature=0.1
)
parser=PydanticOutputParser(pydantic_object=AnalysisResult)
prompt=ChatPromptTemplate.from_messages([
    ("system","""
你是专业iOS产品分析师，逐条解析用户评论
输出情感、问题分类、优先级、原文证据，整体总结，Top3高频问题
{format_instructions}
"""),
    ("human","评论列表:\n{reviews}")
])
chain=prompt.partial(format_instructions=parser.get_format_instructions())|llm|parser
analysis_chain=chain
