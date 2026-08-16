"""
主程序入口
负责页面UI渲染、业务流程调度
"""
import streamlit as st
import pandas as pd
from config.settings import ThemeConfig, PROJECT_NAME, PROJECT_VERSION, PROJECT_DESCRIPTION
from core.data_fetcher import fetch_app_reviews
from core.data_cleaner import clean_review_data


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    字段自动标准化：将常见的中英文列名映射为项目标准字段
    兼容不同来源的CSV/JSON文件
    """
    # 列名映射表：常见别名 -> 标准字段名
    column_mapping = {
        # 评论ID
        "id": "review_id",
        "评论ID": "review_id",
        "review_id": "review_id",
        "reviewId": "review_id",
        
        # 评分
        "rating": "rating",
        "评分": "rating",
        "星级": "rating",
        "score": "rating",
        "star": "rating",
        
        # 标题
        "title": "title",
        "标题": "title",
        "评论标题": "title",
        
        # 评论内容
        "content": "content",
        "评论内容": "content",
        "review": "content",
        "body": "content",
        "text": "content",
        "内容": "content",
        
        # 用户
        "author": "author",
        "用户": "author",
        "用户名": "author",
        "user": "author",
        "userName": "author",
        
        # 版本号
        "version": "version",
        "版本": "version",
        "应用版本": "version",
        "app_version": "version",
        
        # 发布时间
        "publish_time": "publish_time",
        "发布时间": "publish_time",
        "时间": "publish_time",
        "date": "publish_time",
        "updated": "publish_time",
        "created_at": "publish_time"
    }
    
    # 列名转小写后匹配，不区分大小写
    rename_dict = {}
    for col in df.columns:
        col_lower = col.strip().lower()
        for alias, standard in column_mapping.items():
            if col_lower == alias.lower():
                rename_dict[col] = standard
                break
    
    if rename_dict:
        df = df.rename(columns=rename_dict)
    
    # 核心字段缺失兜底：如果没有review_id，用索引生成
    if "review_id" not in df.columns:
        df["review_id"] = [f"local_{i}" for i in range(len(df))]
    
    # 确保内容字段存在
    if "content" not in df.columns:
        raise ValueError("CSV文件中未找到评论内容字段，请确保包含 content / 评论内容 / review 等列")
    
    return df


def apply_theme(is_dark: bool):
    """
    彻底版主题样式：覆盖所有原生组件，无死角染色
    """
    if is_dark:
        bg_color = ThemeConfig.DARK_BG
        card_bg = ThemeConfig.DARK_CARD_BG
        text_color = "#E8E8F0"
        subtext_color = "#A0A0B8"
        border_color = ThemeConfig.DARK_BORDER
        input_bg = "#252539"
        sidebar_bg = "#252539"
        header_bg = "#1E1E2E"
    else:
        bg_color = ThemeConfig.LIGHT_BG
        card_bg = ThemeConfig.LIGHT_CARD_BG
        text_color = ThemeConfig.LIGHT_TEXT
        subtext_color = ThemeConfig.LIGHT_SUBTEXT
        border_color = ThemeConfig.LIGHT_BORDER
        input_bg = "#FFFFFF"
        sidebar_bg = "#FBFBFF"
        header_bg = "#FFFFFF"

    custom_css = f"""
    <style>
        /* 最底层：整个页面背景 */
        .stApp {{
            background-color: {bg_color};
            color: {text_color};
        }}
        
        /* 顶部工具栏、header 白条兜底 */
        header[data-testid="stHeader"] {{
            background-color: {header_bg};
            border-bottom: 1px solid {border_color};
        }}
        #MainMenu, header, footer {{
            background-color: {header_bg};
            color: {text_color};
        }}
        
        /* 文字全量兜底 */
        html, body, [class*="css"]  {{
            color: {text_color} !important;
        }}
        
        p, span, label, div, li, ul, ol {{
            color: {text_color};
        }}
        
        .subtext, small, .stCaption {{
            color: {subtext_color} !important;
            font-size: 0.85rem;
        }}
        
        /* 标题层级 */
        h1, h2, h3, h4, h5, h6 {{
            color: {ThemeConfig.PRIMARY_COLOR} !important;
            font-weight: 600;
            letter-spacing: 0.3px;
        }}
        
        /* 侧边栏 */
        section[data-testid="stSidebar"] {{
            background-color: {sidebar_bg} !important;
            border-right: 1px solid {border_color};
            width: 280px !important;
        }}
        section[data-testid="stSidebar"] * {{
            color: {text_color} !important;
        }}
        
        /* 输入框、下拉框 */
        .stTextInput input,
        .stTextArea textarea,
        .stNumberInput input,
        .stSelectbox div[data-baseweb="select"] > div {{
            background-color: {input_bg} !important;
            color: {text_color} !important;
            border: 1px solid {border_color} !important;
            border-radius: 8px !important;
        }}
        
        /* 滑块 */
        .stSlider [data-testid="stTickBar"] {{
            background: {border_color};
        }}
        .stSlider [data-testid="stThumbValue"] {{
            color: {ThemeConfig.PRIMARY_COLOR} !important;
        }}
        
        /* 主按钮 */
        .stButton>button[data-testid="baseButton-primary"] {{
            background: linear-gradient(135deg, {ThemeConfig.PRIMARY_COLOR} 0%, {ThemeConfig.SECONDARY_COLOR} 100%);
            color: white !important;
            border: none;
            border-radius: 10px;
            padding: 0.6rem 1.8rem;
            font-weight: 500;
            box-shadow: 0 4px 14px rgba(108, 92, 231, 0.25);
            transition: all 0.3s ease;
        }}
        .stButton>button[data-testid="baseButton-primary"]:hover {{
            transform: translateY(-1px);
            box-shadow: 0 6px 20px rgba(108, 92, 231, 0.35);
        }}
        
        /* 次按钮 */
        .stButton>button {{
            background-color: {card_bg};
            color: {text_color} !important;
            border: 1px solid {border_color};
            border-radius: 8px;
            transition: all 0.2s ease;
        }}
        .stButton>button:hover {{
            border-color: {ThemeConfig.PRIMARY_COLOR};
            color: {ThemeConfig.PRIMARY_COLOR} !important;
        }}
        
        /* 分割线 */
        hr {{
            border-color: {border_color};
            opacity: 0.6;
            margin: 1rem 0;
        }}
        
        /* 提示框 */
        .stAlert {{
            border-radius: 10px;
            border: none;
            background-color: {card_bg} !important;
        }}
        .stAlert * {{
            color: {text_color} !important;
        }}
        
        /* 功能卡片 */
        .feature-card {{
            background-color: {card_bg};
            border: 1px solid {border_color};
            border-radius: 12px;
            padding: 1.2rem;
            height: 100%;
            transition: all 0.3s ease;
        }}
        .feature-card:hover {{
            border-color: {ThemeConfig.SECONDARY_COLOR};
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(108, 92, 231, 0.1);
        }}
        .feature-card h4 {{
            margin-bottom: 0.5rem;
            color: {ThemeConfig.PRIMARY_COLOR};
        }}
        .feature-card p {{
            color: {subtext_color};
            font-size: 0.9rem;
            margin: 0;
            line-height: 1.6;
        }}
        
        /* 数据统计卡片 */
        .stat-card {{
            background: linear-gradient(135deg, {card_bg} 0%, {input_bg} 100%);
            border: 1px solid {border_color};
            border-radius: 12px;
            padding: 1rem 1.2rem;
            text-align: center;
        }}
        .stat-card .stat-value {{
            font-size: 1.8rem;
            font-weight: 700;
            color: {ThemeConfig.PRIMARY_COLOR};
            margin: 0.3rem 0;
        }}
        .stat-card .stat-label {{
            font-size: 0.85rem;
            color: {subtext_color};
        }}
        
        /* 布局优化 */
        .block-container {{
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1200px;
        }}
        
        /* 文件上传 */
        [data-testid="stFileUploader"] {{
            background-color: {card_bg};
            border: 1px dashed {border_color};
            border-radius: 10px;
        }}
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


def init_page():
    """初始化页面配置与会话状态"""
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
        "categories": None,
        "prd_versions": None,
        "test_cases": None,
        "analysis_step": 0
    }
    for key, value in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_sidebar():
    """渲染侧边栏配置区"""
    with st.sidebar:
        st.markdown("### ⚙️ 配置中心")
        st.divider()

        # 夜间模式：直接判断状态变化 + 强制刷新，点一次就生效
        st.markdown("#### 🎨 显示设置")
        new_dark = st.toggle(
            "夜间模式",
            value=st.session_state.dark_mode
        )
        if new_dark != st.session_state.dark_mode:
            st.session_state.dark_mode = new_dark
            st.rerun()

        st.divider()

        # 数据源选择
        st.markdown("#### 📥 数据源")
        data_source = st.radio(
            "数据来源",
            ["在线抓取", "本地文件导入"],
            index=0,
            label_visibility="collapsed"
        )

        st.divider()

        # AI功能开关
        st.markdown("#### 🤖 AI分析配置")
        enable_ai = st.checkbox("启用AI语义分析", value=True)
        generate_prd = st.checkbox("自动生成PRD", value=True)
        generate_test = st.checkbox("自动生成测试用例", value=True)

        st.divider()

        # 快速示例
        st.markdown("#### ⚡ 快速体验")
        example_apps = {
            "健身应用": "https://apps.apple.com/us/app/workout-for-women-home-gym/id839285684",
            "笔记应用": "https://apps.apple.com/us/app/notability/id360593530",
            "摄影应用": "https://apps.apple.com/us/app/vsco-photo-video-editor/id588013838"
        }
        selected_example = st.selectbox(
            "选择示例App",
            options=list(example_apps.keys()),
            label_visibility="collapsed"
        )

        st.divider()
        st.caption(f"v{PROJECT_VERSION}")
        st.caption(PROJECT_DESCRIPTION)

        return data_source, enable_ai, generate_prd, generate_test, example_apps[selected_example]


def render_header():
    """渲染页面顶部标题区"""
    st.title(f"📱 {PROJECT_NAME}")
    st.caption(PROJECT_DESCRIPTION)
    st.divider()


def render_feature_overview():
    """渲染核心能力概览卡片，填充首页空白"""
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
    """渲染数据输入区"""
    st.subheader("📥 数据输入")
    st.markdown("")

    if data_source == "在线抓取":
        col1, col2 = st.columns([3, 1])
        with col1:
            app_url = st.text_input(
                "App Store 应用链接",
                value=example_url,
                placeholder="https://apps.apple.com/us/app/xxx/idxxxxxxxxx"
            )
        with col2:
            max_pages = st.slider(
                "抓取页数",
                min_value=1,
                max_value=10,
                value=5,
                help="每页约50条评论"
            )
        return app_url, max_pages, None
    else:
        uploaded_file = st.file_uploader(
            "上传评论数据集",
            type=["csv", "json"],
            help="支持 CSV / JSON 格式，需包含评论内容、评分等核心字段"
        )
        return "", 0, uploaded_file


def render_data_overview(raw_df, clean_df, stats):
    """渲染数据概览统计卡片"""
    st.subheader("📊 数据概览")
    st.markdown("")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{stats['raw_count']}</div>
            <div class="stat-label">原始评论数</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{stats['final_count']}</div>
            <div class="stat-label">有效评论数</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        removed = stats['raw_count'] - stats['final_count']
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{removed}</div>
            <div class="stat-label">清洗剔除</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        avg_rating = round(clean_df["rating"].mean(), 2) if not clean_df.empty else 0
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{avg_rating}</div>
            <div class="stat-label">平均评分</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")


def render_review_table(df, title="评论数据"):
    """渲染评论数据表格"""
    st.subheader(f"📋 {title}")
    if df.empty:
        st.warning("暂无数据")
        return
    
    # 只展示核心字段
    show_cols = [col for col in ["rating", "title", "content", "author", "version", "publish_time"] if col in df.columns]
    display_df = df[show_cols].copy()
    display_df.columns = ["评分", "标题", "内容", "用户", "版本", "发布时间"][:len(show_cols)]
    st.dataframe(display_df, use_container_width=True, height=420)


def render_data_limit_note():
    """渲染数据局限性说明"""
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

    # 侧边栏
    data_source, enable_ai, generate_prd, generate_test, example_url = render_sidebar()

    # 顶部与概览
    render_header()
    render_feature_overview()

    # 数据输入
    app_url, max_pages, uploaded_file = render_data_input(data_source, example_url)

    # 分析按钮
    st.markdown("")
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        start_btn = st.button(
            "🚀 开始全流程分析",
            use_container_width=True,
            type="primary"
        )

    # 执行分析流程
    if start_btn:
        with st.spinner("正在处理数据..."):
            try:
                # 1. 获取原始数据
                if data_source == "在线抓取":
                    raw_df = fetch_app_reviews(app_url=app_url, max_pages=max_pages)
                else:
                    if uploaded_file is None:
                        st.warning("请先上传数据文件")
                        st.stop()
                    # 读取文件
                    if uploaded_file.name.endswith(".csv"):
                        raw_df = pd.read_csv(uploaded_file)
                    else:
                        raw_df = pd.read_json(uploaded_file)
                    
                    # 字段自动标准化
                    raw_df = standardize_columns(raw_df)
                
                if raw_df.empty:
                    st.error("未获取到任何评论数据，请检查输入内容")
                    st.stop()
                
                # 2. 数据清洗
                clean_df, clean_stats = clean_review_data(raw_df)
                
                # 3. 存入会话状态
                st.session_state.reviews_df = raw_df
                st.session_state.clean_df = clean_df
                st.session_state.clean_stats = clean_stats
                
                st.success(f"✅ 数据处理完成，原始 {len(raw_df)} 条，有效 {len(clean_df)} 条")
                
            except Exception as e:
                # 显示完整错误信息，方便排查
                st.error(f"处理失败：{str(e)}")
                st.stop()

    # 数据结果展示
    if st.session_state.clean_df is not None:
        st.divider()
        
        render_data_overview(
            st.session_state.reviews_df,
            st.session_state.clean_df,
            st.session_state.clean_stats
        )
        
        tab1, tab2 = st.tabs(["有效评论数据", "原始评论数据"])
        with tab1:
            render_review_table(st.session_state.clean_df, "有效评论")
        with tab2:
            render_review_table(st.session_state.reviews_df, "原始评论")

    # 底部说明
    st.divider()
    render_data_limit_note()


if __name__ == "__main__":
    main()
