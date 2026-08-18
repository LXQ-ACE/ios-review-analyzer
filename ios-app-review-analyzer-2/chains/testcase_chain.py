from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from config.settings import settings
from chains.output_schema import TestCaseResult

llm=ChatOpenAI(
    base_url=settings.llm_base_url,
    api_key=settings.llm_api_key,
    model=settings.llm_model_name,
    temperature=0.2
)
parser=PydanticOutputParser(pydantic_object=TestCaseResult)
prompt=ChatPromptTemplate.from_messages([
    ("system","""
根据PRD需求文档，生成完整可执行的测试用例
包含用例标题、前置条件、操作步骤、预期结果
{format_instructions}
"""),
    ("human","PRD需求：\n{prd_content}")
])
testcase_chain=prompt.partial(format_instructions=parser.get_format_instructions())|llm|parser
