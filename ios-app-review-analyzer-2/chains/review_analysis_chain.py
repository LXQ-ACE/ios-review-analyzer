from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from config.settings import settings
from chains.output_schema import BatchAnalysisOutput

llm = ChatOpenAI(
    base_url=settings.llm_base_url,
    api_key=settings.llm_api_key,
    model=settings.llm_model_name,
    temperature=0.1
)

parser = PydanticOutputParser(pydantic_object=BatchAnalysisOutput)

prompt = ChatPromptTemplate.from_messages([
    ("system", """
你是专业的App评论分析师，需要分析一批iOS用户评论。
任务：
1、逐条解析每一条评论：情感、问题分类、修复优先级、证据片段
2、输出整体分析总结
3、提取排名前三的高频问题

{format_instructions}
"""),
    ("human","待分析的评论列表：\n{review_text_list}")
])

analysis_chain = prompt.partial(format_instructions=parser.get_format_instructions()) | llm | parser
