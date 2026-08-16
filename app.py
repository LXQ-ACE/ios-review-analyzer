"""
主程序入口
负责页面UI渲染、全流程业务调度
"""
import streamlit as st
import pandas as pd
import os
from config.settings import ThemeConfig, PROJECT_NAME, PROJECT_VERSION, PROJECT_DESCRIPTION
from core.data_fetcher import fetch_app_reviews
from core.data_cleaner import clean_review_data
from core.analyzer import analyze_reviews, generate_prd, generate_test_cases
from utils.exporter import (
    df_to_csv_bytes,
    analysis_to_markdown,
    prd_to_markdown,
    testcase_to_markdown,
    full_report_markdown,
    string_to_bytes
)


def load_sample_data() -> pd.DataFrame:
    """加载内置示例数据集"""
    sample_path = os.path.join("data", "sample_reviews.csv")
    if os.path.exists(sample_path):
        return pd.read_csv(sample_path)
    return pd.DataFrame()


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """字段自动标准化，兼容不同来源CSV"""
    column_mapping = {
        "id": "review_id", "评论ID": "review_id", "review_id": "review_id", "reviewId": "review_id",
        "rating": "rating", "评分": "rating", "星级": "rating", "score": "rating", "star": "rating",
        "title": "title", "标题": "title", "评论标题": "title",
        "content": "content", "评论内容": "content", "review": "content", "body": "content", "text": "content", "内容": "content",
        "author": "author", "用户": "author", "用户名": "author", "user": "author", "userName": "author",
        "version": "version", "版本": "version", "应用版本": "version", "app_version": "version",
        "publish_time": "publish_time", "发布时间": "publish_time", "时间": "publish_time", "date": "publish_time", "updated": "publish_time", "created_at": "publish_time"
    }

    rename_dict = {}
    for col in df.columns:
        col_lower = col.strip().lower()
        for alias, standard in column_mapping.items():
            if col_lower == alias.lower():
                rename_dict[col] = standard
                break

    if rename_dict:
        df = df.rename(columns=rename_dict)

    if "review_id" not in df.columns:
        df["review_id"] = [f"local_{i}" for i in range(len(df))]

    if "content" not in df.columns:
        raise ValueError("CSV文件中未找到评论内容字段，请确保包含 content / 评论内容 等列")

    return df


def apply_theme(is_dark: bool):
    """完整主题样式"""
    if is_dark:
        bg_color = ThemeConfig.DARK_BG
        card_bg = ThemeConfig.DARK_CARD_BG
        text_color = "#FFFFFF"
        subtext_color = "#D8D8E8"
        border_color = "#555577"
        input_bg = "#3A3A5A"
        sidebar_bg = "#252539"
        header_bg = "#1E1E2E"
        collapse_btn_bg = "#3A3A5A"
        collapse_btn_color = "#FFFFFF"
    else:
        bg_color = ThemeConfig.LIGHT_BG
        card_bg = ThemeConfig.LIGHT_CARD_BG
        text_color = ThemeConfig.LIGHT_TEXT
        subtext_color = ThemeConfig.LIGHT_SUBTEXT
        border_color = ThemeConfig.LIGHT_BORDER
        input_bg = "#FFFFFF"
        sidebar_bg = "#FBFBFF"
        header_bg = "#FFFFFF"
        collapse_btn_bg = "#F0F2F6"
        collapse_btn_color = "#2D3436"

    custom_css = f"""
    <style>
        .stApp {{ background-color: {bg_color}; color: {text_color}; }}
        header[data-testid="stHeader"] {{ background-color: {header_bg}; border-bottom: 1px solid {border_color}; }}
        #MainMenu, header, footer {{ background-color: {header_bg}; color: {text_color}; }}
        html, body, [class*="css"]  {{ color: {text_color} !important; }}
        p, span, label, div, li, ul, ol {{ color: {text_color}; }}
        .subtext, small, .stCaption {{ color: {subtext_color} !important; font-size: 0.85rem; }}
        h1, h2, h3, h4, h5, h6 {{ color: {ThemeConfig.PRIMARY_COLOR} !important; font-weight: 600; letter-spacing: 0.3px; }}

        /* 侧边栏 */
        section[data-testid="stSidebar"] {{ background-color: {sidebar_bg} !important; border-right: 1px solid {border_color}; width: 280px !important; }}
        section[data-testid="stSidebar"] * {{ color: {text_color} !important; }}
        button[data-testid="stSidebarCollapseButton"] {{ background-color: {collapse_btn_bg} !important; color: {collapse_btn_color} !important; border: 1px solid {border_color} !important; border-radius: 8px !important; }}
        button[data-testid="stSidebarCollapseButton"]:hover {{ background-color: {ThemeConfig.PRIMARY_COLOR} !important; color: #FFFFFF !important; }}

        /* 输入组件 */
        section[data-testid="stSidebar"] .stTextInput input,
        section[data-testid="stSidebar"] .stTextArea textarea,
        section[data-testid="stSidebar"] .stNumberInput input {{
            background-color: {input_bg} !important;
            color: {text_color} !important;
            border: 1px solid {border_color} !important;
            border-radius: 8px !important;
        }}

        .stRadio > div {{ gap: 0.6rem; }}
        .stRadio label {{ color: {subtext_color} !important; }}
        .stSlider [data-testid="stTickBar"] {{ background: {border_color}; }}
        .stSlider [data-testid="stThumbValue"] {{ color: {ThemeConfig.PRIMARY_COLOR} !important; }}

        /* 按钮 */
        .stButton>button[data-testid="baseButton-primary"] {{
            background: linear-gradient(135deg, {ThemeConfig.PRIMARY_COLOR} 0%, {ThemeConfig.SECONDARY_COLOR} 100%);
            color: white !important; border: none; border-radius: 10px; padding: 0.6rem 1.8rem;
            font-weight: 500; box-shadow: 0 4px 14px rgba(108, 92, 231, 0.25); transition: all 0.3s ease;
        }}
        .stButton>button[data-testid="baseButton-primary"]:hover {{ transform: translateY(-1px); box-shadow: 0 6px 20px rgba(108, 92, 231, 0.35); }}
        .stButton>button {{ background-color: {card_bg}; color: {text_color} !important; border: 1px solid {border_color}; border-radius: 8px; transition: all 0.2s ease; }}
        .stButton>button:hover {{ border-color: {ThemeConfig.PRIMARY_COLOR}; color: {ThemeConfig.PRIMARY_COLOR} !important; }}

        hr {{ border-color: {border_color}; opacity: 0.6; margin: 1rem 0; }}
        .stAlert {{ border-radius: 10px; border: none; background-color: {card_bg} !important; }}
        .stAlert * {{ color: {text_color} !important; }}

        /* 卡片通用样式 */
        .feature-card, .analysis-card, .prd-card {{
            background-color: {card_bg}; border: 1px solid {border_color}; border-radius: 12px;
            padding: 1.2rem; transition: all 0.3s ease;
        }}
        .feature-card:hover, .prd-card:hover {{ border-color: {ThemeConfig.SECONDARY_COLOR}; transform: translateY(-2px); box-shadow: 0 8px 24px rgba(108, 92, 231, 0.1); }}
        .feature-card h4, .analysis-card h4, .prd-card h4 {{ margin-bottom: 0.5rem; color: {ThemeConfig.PRIMARY_COLOR}; }}
        .feature-card p, .analysis-card p, .prd-card p {{ color: {subtext_color}; font-size: 0.9rem; margin: 0; line-height: 1.6; }}

        /* 统计卡片 */
        .stat-card {{
            background: linear-gradient(135deg, {card_bg} 0%, {input_bg} 100%);
            border: 1px solid {border_color}; border-radius: 12px; padding: 1rem 1.2rem; text-align: center;
        }}
        .stat-card .stat-value {{ font-size: 1.8rem; font-weight: 700; color: {ThemeConfig.PRIMARY_COLOR}; margin: 0.3rem 0; }}
        .stat-card .stat-label {{ font-size: 0.85rem; color: {subtext_color}; }}

        .block-container {{ padding-top: 2rem; padding-bottom: 2rem; max-width: 1200px; }}
        [data-testid="stFileUploader"] {{ background-color: {card_bg}; border: 1px dashed {border_color}; border-radius: 10px; }}

        /* Tab 标签 */
        .stTabs [data-baseweb="tab-list"] {{ gap: 2rem; }}
        .stTabs [data-baseweb="tab"] {{ color: {subtext_color}; }}
        .stTabs [aria-selected="true"] {{ color: {ThemeConfig.PRIMARY_COLOR} !important; border-bottom: 2px solid {ThemeConfig.PRIMARY_COLOR}; }}

        /* 优先级徽章 */
        .badge {{ display: inline-block; padding: 0.2rem 0.6rem; border-radius: 12px; font-size: 0.75rem; font-weight: 500; margin-right: 0.5rem; }}
        .badge-p0 {{ background-color: rgba(225, 112, 85, 0.15); color: #E17055; }}
        .badge-p1 {{ background-color: rgba(253, 203, 110, 0.15); color: #FDCB6E; }}
        .badge-p2 {{ background-color: rgba(116, 185, 255, 0.15); color: #74B9FF; }}
        .badge-p3 {{ background-color: rgba(189, 195, 199, 0.15); color: #BDC3C7; }}
        .badge-high {{ background-color: rgba(225, 112, 85, 0.15); color: #E17055; }}
        .badge-mid {{ background-color: rgba(253, 203, 110, 0.15); color: #FDCB6E; }}
        .badge-low {{ background-color: rgba(0, 184, 148, 0.15); color: #00B894; }}
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


def init_page():
    """初始化页面状态"""
    st.set_page_config(
        page_title=f"{PROJECT_NAME} v{PROJECT_VERSION}",
        page_icon="📱",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    default_states = {
        "dark_mode": False,
        "reviews_df": None,
        "clean_df": None,
        "clean_stats": None,
        "analysis_result": None,
        "prd_result": None,
        "test_case_result": None
    }
    for key, value in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_sidebar():
    """渲染侧边栏"""
    with st.sidebar:
        st.markdown("### ⚙️ 配置中心")
        st.divider()

        st.markdown("#### 🎨 显示设置")
        new_dark = st.toggle("夜间模式", value=st.session_state.dark_mode)
        if new_dark != st.session_state.dark_mode:
            st.session_state.dark_mode = new_dark
            st.rerun()

        st.divider()
        st.markdown("#### 📥 数据源")
        data_source = st.radio("数据来源", ["在线抓取", "本地文件导入", "内置示例数据"], index=2, label_visibility="collapsed")

        st.divider()
        st.markdown("#### 🤖 AI分析配置")
        enable_ai = st.checkbox("启用AI语义分析", value=True)
        generate_prd_flag = st.checkbox("自动生成PRD", value=True)
        generate_test = st.checkbox("自动生成测试用例", value=True)

        st.divider()
        st.markdown("#### ⚡ 快速体验")
        example_apps = {
            "健身应用": "https://apps.apple.com/us/app/workout-for-women-home-gym/id839285684",
            "笔记应用": "https://apps.apple.com/us/app/notability/id360593530",
            "摄影应用": "https://apps.apple.com/us/app/vsco-photo-video-editor/id588013838"
        }
        selected_name = st.radio("选择示例App", options=list(example_apps.keys()), index=0, label_visibility="collapsed")

        st.divider()
        st.caption(f"v{PROJECT_VERSION}")
        st.caption(PROJECT_DESCRIPTION)

        return data_source, enable_ai, generate_prd_flag, generate_test, example_apps[selected_name]


def render_header():
    st.title(f"📱 {PROJECT_NAME}")
    st.caption(PROJECT_DESCRIPTION)
    st.divider()


def render_feature_overview():
    st.subheader("✨ 核心能力")
    st.markdown("")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="feature-card">
            <h4>📊 官方数据抓取</h4>
            <p>基于苹果官方iTunes RSS接口，稳定合规获取美国区用户评论，支持多页批量拉取。</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h4>🤖 AI语义分类</h4>
            <p>大模型驱动的动态主题聚类，无硬编码分类，自动识别用户反馈核心痛点与矛盾点。</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h4>📋 智能PRD生成</h4>
            <p>基于问题自动输出结构化产品需求，按优先级拆分版本规划，每条需求可追溯原始评论。</p>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class="feature-card">
            <h4>🧪 测试用例产出</h4>
            <p>自动生成标准化测试用例，覆盖场景、前置条件、操作步骤与预期结果，形成完整闭环。</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")
    st.divider()


def render_data_input(data_source: str, example_url: str):
    st.subheader("📥 数据输入")
    st.markdown("")
    if data_source == "在线抓取":
        col1, col2 = st.columns([3, 1])
        with col1:
            app_url = st.text_input("App Store 应用链接", value=example_url, placeholder="https://apps.apple.com/us/app/xxx/idxxxxxxxxx")
        with col2:
            max_pages = st.slider("抓取页数", min_value=1, max_value=10, value=5, help="每页约50条评论")
        return app_url, max_pages, None
    elif data_source == "本地文件导入":
        uploaded_file = st.file_uploader("上传评论数据集", type=["csv", "json"], help="支持 CSV / JSON 格式")
        return "", 0, uploaded_file
    else:
        st.info("💡 使用内置示例数据集，可直接体验完整功能")
        return "", 0, "sample"


def render_data_overview(raw_df, clean_df, stats):
    st.subheader("📊 数据概览")
    st.markdown("")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f'<div class="stat-card"><div class="stat-value">{stats["raw_count"]}</div><div class="stat-label">原始评论数</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="stat-card"><div class="stat-value">{stats["final_count"]}</div><div class="stat-label">有效评论数</div></div>', unsafe_allow_html=True)
    with col3:
        removed = stats["raw_count"] - stats["final_count"]
        st.markdown(f'<div class="stat-card"><div class="stat-value">{removed}</div><div class="stat-label">清洗剔除</div></div>', unsafe_allow_html=True)
    with col4:
        avg_rating = round(clean_df["rating"].mean(), 2) if not clean_df.empty else 0
        st.markdown(f'<div class="stat-card"><div class="stat-value">{avg_rating}</div><div class="stat-label">平均评分</div></div>', unsafe_allow_html=True)

    st.markdown("")


def render_review_table(df, title="评论数据"):
    st.subheader(f"📋 {title}")
    if df.empty:
        st.warning("暂无数据")
        return
    show_cols = [col for col in ["rating", "title", "content", "author", "version"] if col in df.columns]
    display_df = df[show_cols].copy()
    display_df.columns = ["评分", "标题", "内容", "用户", "版本"][:len(show_cols)]
    st.dataframe(display_df, use_container_width=True, height=420)


def render_analysis_result(result):
    """渲染AI语义分析结果"""
    st.subheader("🤖 AI 语义分析")
    st.markdown("")

    # 整体总结
    st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
    st.markdown("#### 📝 整体评论总结")
    st.write(result.overall_summary)
    st.markdown('</div>', unsafe_allow_html=True)

    # 核心痛点 & 好评
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
        st.markdown("#### 🔴 核心痛点 Top5")
        for i, point in enumerate(result.core_pain_points, 1):
            st.write(f"{i}. {point}")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
        st.markdown("#### 🟢 核心好评 Top5")
        for i, point in enumerate(result.core_praise_points, 1):
            st.write(f"{i}. {point}")
        st.markdown('</div>', unsafe_allow_html=True)

    # 矛盾反馈
    if result.contradiction_points:
        st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
        st.markdown("#### ⚠️ 矛盾反馈识别")
        for i, point in enumerate(result.contradiction_points, 1):
            st.write(f"{i}. {point}")
        st.markdown('</div>', unsafe_allow_html=True)

    # 分类详情
    st.markdown("#### 📂 分类主题详情")
    for cat in result.categories:
        with st.expander(f"{cat.category_name} · {cat.priority}优先级 · {cat.issue_count}个问题点", expanded=False):
            st.write(f"**说明**：{cat.category_desc}")
            st.markdown("---")
            for issue in cat.issues:
                level_class = "badge-high" if issue.evidence_level == "充足" else "badge-mid" if issue.evidence_level == "样本有限" else "badge-low"
                st.markdown(f"""
                <span class="badge {level_class}">{issue.evidence_level}</span>
                <span class="badge badge-mid">{issue.sentiment}</span>
                **{issue.issue_summary}**
                """, unsafe_allow_html=True)
                st.caption(f"提及样本数：{issue.evidence_count} 条")
                if issue.is_contradictory and issue.contradictory_note:
                    st.caption(f"⚠️ 矛盾说明：{issue.contradictory_note}")
                st.markdown("")


def render_prd_result(prd_result):
    """渲染PRD生成结果"""
    st.subheader("📋 产品需求规划 (PRD)")
    st.markdown("")

    # 产品背景
    st.markdown('<div class="prd-card">', unsafe_allow_html=True)
    st.markdown("#### 🎯 产品背景与问题分析")
    st.write(prd_result.product_background)
    st.markdown('</div>', unsafe_allow_html=True)

    # 分版本规划
    st.markdown("#### 📅 分版本需求规划")
    for plan in prd_result.version_plans:
        with st.expander(f"{plan.version_name} — {plan.version_goal}", expanded=False):
            for req in plan.requirements:
                prio_class = f"badge-{req.priority.lower()}"
                st.markdown(f"""
                <span class="badge {prio_class}">{req.priority}</span>
                **{req.req_title}**
                """, unsafe_allow_html=True)
                st.write(req.req_desc)
                st.caption(f"用户价值：{req.user_value}")
                st.caption(f"对应问题：{req.related_issue}")
                st.markdown("")


def render_test_case_result(test_result):
    """渲染测试用例结果"""
    st.subheader("🧪 测试用例集")
    st.markdown("")

    st.markdown(f"共生成 **{test_result.total_count}** 条测试用例")
    st.markdown("")

    for i, case in enumerate(test_result.test_cases, 1):
        with st.expander(f"用例 {i}: {case.case_title} · {case.case_level}级别", expanded=False):
            st.write(f"**前置条件**：{case.precondition}")
            st.write("**测试步骤**：")
            for step in case.test_steps:
                st.write(f"- {step}")
            st.write(f"**预期结果**：{case.expected_result}")
            st.caption(f"对应需求：{case.related_requirement}")


def render_export_section():
    """渲染导出区域"""
    st.subheader("📤 结果导出")
    st.markdown("")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # 导出评论数据 CSV
        csv_bytes = df_to_csv_bytes(st.session_state.clean_df)
        st.download_button(
            label="📊 导出评论数据",
            data=csv_bytes,
            file_name="评论数据.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col2:
        # 导出分析报告
        if st.session_state.analysis_result:
            md_text = analysis_to_markdown(st.session_state.analysis_result)
            st.download_button(
                label="🤖 导出分析报告",
                data=string_to_bytes(md_text),
                file_name="AI语义分析报告.md",
                mime="text/markdown",
                use_container_width=True
            )

    with col3:
        # 导出 PRD
        if st.session_state.prd_result:
            md_text = prd_to_markdown(st.session_state.prd_result)
            st.download_button(
                label="📋 导出PRD文档",
                data=string_to_bytes(md_text),
                file_name="产品需求文档.md",
                mime="text/markdown",
                use_container_width=True
            )

    with col4:
        # 导出完整报告
        if st.session_state.test_case_result:
            full_md = full_report_markdown(
                st.session_state.analysis_result,
                st.session_state.prd_result,
                st.session_state.test_case_result
            )
            st.download_button(
                label="📑 导出完整报告",
                data=string_to_bytes(full_md),
                file_name="全链路分析报告.md",
                mime="text/markdown",
                use_container_width=True
            )


def render_data_limit_note():
    st.info("""
    **📌 数据说明与局限性**
    - 在线抓取数据源为苹果官方 iTunes RSS Feed，仅返回美国区最新评论
    - 官方接口单应用最多返回约500条评论，无法获取全量历史数据
    - 分析结论仅基于样本数据推导，不代表全部用户观点
    - 所有原始数据仅在本地处理，不会上传至第三方服务器
    """)


def main():
    """主程序入口"""
    init_page()
    apply_theme(st.session_state.dark_mode)

    # 侧边栏配置
    data_source, enable_ai, gen_prd, gen_test, example_url = render_sidebar()

    # 页面头部
    render_header()
    render_feature_overview()

    # 数据输入
    app_url, max_pages, uploaded_file = render_data_input(data_source, example_url)

    # 分析按钮
    st.markdown("")
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        start_btn = st.button("🚀 开始全流程分析", use_container_width=True, type="primary")

    # 执行全流程
    if start_btn:
        try:
            # 1. 获取数据
            with st.spinner("正在获取并清洗数据..."):
                if data_source == "在线抓取":
                    raw_df = fetch_app_reviews(app_url=app_url, max_pages=max_pages)
                elif data_source == "本地文件导入":
                    if uploaded_file is None:
                        st.warning("请先上传数据文件")
                        st.stop()
                    if uploaded_file.name.endswith(".csv"):
                        raw_df = pd.read_csv(uploaded_file)
                    else:
                        raw_df = pd.read_json(uploaded_file)
                    raw_df = standardize_columns(raw_df)
                else:
                    # 内置示例数据
                    raw_df = load_sample_data()
                    raw_df = standardize_columns(raw_df)

                if raw_df.empty:
                    st.error("未获取到任何评论数据")
                    st.stop()

                clean_df, clean_stats = clean_review_data(raw_df)
                st.session_state.reviews_df = raw_df
                st.session_state.clean_df = clean_df
                st.session_state.clean_stats = clean_stats
                st.success(f"✅ 数据处理完成，原始 {len(raw_df)} 条，有效 {len(clean_df)} 条")

            # 2. AI语义分析
            if enable_ai:
                with st.spinner("AI 正在分析评论内容，请稍候..."):
                    analysis_result = analyze_reviews(clean_df)
                    st.session_state.analysis_result = analysis_result
                st.success("✅ AI 语义分析完成")

            # 3. 生成PRD
            if gen_prd and st.session_state.analysis_result:
                with st.spinner("正在生成产品需求规划..."):
                    prd_result = generate_prd(st.session_state.analysis_result)
                    st.session_state.prd_result = prd_result
                st.success("✅ PRD 需求规划生成完成")

            # 4. 生成测试用例
            if gen_test and st.session_state.prd_result:
                with st.spinner("正在生成测试用例..."):
                    test_result = generate_test_cases(st.session_state.prd_result)
                    st.session_state.test_case_result = test_result
                st.success("✅ 测试用例生成完成")

        except Exception as e:
            st.error(f"处理失败：{str(e)}")
            import traceback
            traceback.print_exc()
            st.stop()

    # 数据结果展示
    if st.session_state.clean_df is not None:
        st.divider()
        render_data_overview(st.session_state.reviews_df, st.session_state.clean_df, st.session_state.clean_stats)

        tab1, tab2 = st.tabs(["有效评论数据", "原始评论数据"])
        with tab1:
            render_review_table(st.session_state.clean_df, "有效评论")
        with tab2:
            render_review_table(st.session_state.reviews_df, "原始评论")

        # AI分析结果
        if st.session_state.analysis_result is not None:
            st.divider()
            render_analysis_result(st.session_state.analysis_result)

        # PRD结果
        if st.session_state.prd_result is not None:
            st.divider()
            render_prd_result(st.session_state.prd_result)

        # 测试用例结果
        if st.session_state.test_case_result is not None:
            st.divider()
            render_test_case_result(st.session_state.test_case_result)

        # 导出区域
        st.divider()
        render_export_section()

    st.divider()
    render_data_limit_note()


if __name__ == "__main__":
    main()
