import streamlit as st
import pandas as pd
from chains.review_analysis_chain import analysis_chain
from utils.data_loader import load_csv_data,df_to_review_list

st.set_page_config(page_title="V2‑LangChain评论分析",layout="wide")
st.title("📱 iOS App评论分析系统 V2 (LangChain版)")

upload_file = st.file_uploader("上传评论CSV文件",type=["csv"])
use_sample = st.checkbox("使用内置英文样例数据集")

df = None
if upload_file:
    df = load_csv_data(upload_file)
elif use_sample:
    df = load_csv_data("./data/sample_en.csv")

if df is not None:
    st.subheader("原始数据预览")
    st.dataframe(df.head(10))

    if st.button("🚀 LangChain一键开始AI分析"):
        with st.spinner("大模型正在分析，请稍候..."):
            review_list = df_to_review_list(df)
            result = analysis_chain.invoke({"review_text_list":review_list})

        st.success("分析完成")
        st.subheader("📊整体分析总结")
        st.info(result.summary)

        st.subheader("🔥Top3高频问题")
        for item in result.top_problems:
            st.markdown(f"- {item}")

        st.subheader("逐条解析详情")
        res_df = pd.DataFrame([i.model_dump() for i in result.analysis_list])
        st.dataframe(res_df)
