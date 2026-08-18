import streamlit as st
import pandas as pd
from utils.crawler import fetch_appstore_reviews
from utils.data_helper import load_csv,export_csv,load_sample
from chains.analysis_chain import analysis_chain
from chains.prd_chain import prd_chain
from chains.testcase_chain import testcase_chain

st.set_page_config(page_title="iOS‑Review‑Analyzer V2(LangChain)",layout="wide")

# 美式简约自定义CSS
custom_css = """
<style>
:root {
    --primary:#6B5B95;
    --bg‑light:#f7f9fc;
    --bg‑dark:#1e222b;
    --card‑light:#ffffff;
    --card‑dark:#272c38;
}
.block-container{padding-top:2rem;max-width:1200px}
div[data-testid="stVerticalBlock"]>div{
    background-color:var(--card-bg);
    padding:24px;
    border-radius:12px;
    margin-bottom:20px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}
h1,h2,h3{font-family:'Helvetica',sans-serif;font-weight:500}
</style>
"""
st.markdown(custom_css,unsafe_allow_html=True)

#日间/夜间切换
theme=st.radio("Theme / 显示模式",["Light Mode","Dark Mode"],horizontal=True)
if theme=="Dark Mode":
    st.markdown("""<style>
    .stApp{background-color:#1e222b;color:#eeeeee}
    </style>""",unsafe_allow_html=True)

st.title("📱 iOS App Review Analyzer · V2 LangChain")
st.markdown("##### American‑style UI | Crawl‑Analyze‑Generate PRD & TestCase")

tab1,tab2=st.tabs(["📥 获取评论数据","🧠 AI智能分析&文档生成"])
df=None
with tab1:
    sub_tab1,sub_tab2,sub_tab3=st.tabs(["App Store抓取","上传CSV","内置样例"])
    with sub_tab1:
        aid=st.text_input("App ID")
        cty=st.text_input("国家代码",value="us")
        limit=st.number_input("获取条数",min_value=5,max_value=200,value=30)
        if st.button("开始抓取"):
            with st.spinner("Fetching reviews..."):
                df=fetch_appstore_reviews(aid,cty,limit)
    with sub_tab2:
        file=st.file_uploader("上传CSV，字段必须包含review,rating",type=["csv"])
        if file:
            df=load_csv(file)
    with sub_tab3:
        if st.button("Load Sample Dataset"):
            df=load_sample()
    if df is not None:
        st.subheader("Data Preview")
        st.dataframe(df,use_container_width=True)
        csv_file=export_csv(df)
        st.download_button("📤 导出原始CSV",csv_file,file_name="raw_reviews.csv",mime="text/csv")

with tab2:
    if df is None:
        st.info("⚠️ 请先在上方标签页导入评论数据")
    else:
        if st.button("🚀 Run LangChain AI Analysis"):
            with st.spinner("AI analyzing reviews..."):
                review_list=df["review"].tolist()
                ana_result=analysis_chain.invoke({"reviews":review_list})
                st.session_state.ana=ana_result
        if "ana" in st.session_state:
            res=st.session_state.ana
            st.subheader("📊 Analysis Summary")
            st.info(res.global_summary)
            st.subheader("🔥 Top 3 Issues")
            for p in res.top3_problems:
                st.markdown(f"- {p}")
            st.subheader("Detail Result")
            detail_df=pd.DataFrame([x.model_dump() for x in res.item_list])
            st.dataframe(detail_df,use_container_width=True)

            #PRD生成
            if st.button("📄 Generate PRD需求文档"):
                with st.spinner("Generating PRD..."):
                    prd_res=prd_chain.invoke({"summary_text":res.global_summary})
                    st.session_state.prd=prd_res
            if "prd" in st.session_state:
                prd=st.session_state.prd
                st.subheader("PRD 产品需求")
                st.write(f"**需求标题**：{prd.requirement_title}")
                st.write(f"**优先级**：{prd.priority}")
                st.markdown(f">背景：{prd.background}")
                st.markdown(f">功能说明：{prd.function_desc}")
                st.markdown("验收标准：")
                for cr in prd.acceptance_criteria:
                    st.markdown(f"- {cr}")

                #测试用例
                if st.button("🧪 Generate TestCase 测试用例"):
                    with st.spinner("生成测试用例..."):
                        tc_res=testcase_chain.invoke({"prd_content":prd.model_dump_json()})
                        st.session_state.tc=tc_res
                if "tc" in st.session_state:
                    tc=st.session_state.tc
                    st.subheader("自动生成测试用例")
                    st.write(f"用例名称：{tc.case_title}")
                    st.write(f"前置条件：{tc.precondition}")
                    st.markdown("操作步骤：")
                    for step in tc.operation_step:
                        st.markdown(f"- {step}")
                    st.write(f"预期结果：{tc.expect_result}")
