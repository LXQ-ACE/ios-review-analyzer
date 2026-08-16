"""
主程序入口
负责页面UI渲染、业务流程调度
"""
import streamlit as st
from config.settings import ThemeConfig, PROJECT_NAME, PROJECT_VERSION, PROJECT_DESCRIPTION


def apply_theme(is_dark: bool):
    """
    彻底版主题样式：覆盖所有原生组件，无死角染色
    """
    if is_dark:
        bg_color = ThemeConfig.DARK_BG
        card_bg = ThemeConfig.DARK_CARD_BG
        text_color = "#E8E8F0"       # 提高亮度，确保夜间看得清
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
        /* ========== 最底层：整个页面背景 ========== */
        .stApp {{
            background-color: {bg_color};
            color: {text_color};
        }}
        
        /* 强制覆盖顶部工具栏、header 白条 */
        header[data-testid="stHeader"] {{
            background-color: {header_bg};
            border-bottom: 1px solid {border_color};
        }}
        #MainMenu, header, footer {{
            background-color: {header_bg};
            color: {text_color};
        }}
        
        /* ========== 文字全量兜底 ========== */
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
        
        /* ========== 标题 ========== */
        h1, h2, h3, h4, h5, h6 {{
            color: {ThemeConfig.PRIMARY_COLOR} !important;
            font-weight: 600;
            letter-spacing: 0.3px;
        }}
        
        /* ========== 侧边栏 ========== */
        section[data-testid="stSidebar"] {{
            background-color: {sidebar_bg} !important;
            border-right: 1px solid {border_color};
            width: 280px !important;
        }}
        section[data-testid="stSidebar"] * {{
            color: {text_color} !important;
        }}
        
        /* ========== 输入框 ========== */
        .stTextInput input,
        .stTextArea textarea,
        .stNumberInput input,
        .stSelectbox div[data-baseweb="select"] > div {{
            background-color: {input_bg} !important;
            color: {text_color} !important;
            border: 1px solid {border_color} !important;
            border-radius: 8px !important;
        }}
        
        /* ========== 滑块 ========== */
        .stSlider [data-testid="stTickBar"] {{
            background: {border_color};
        }}
        .stSlider [data-testid="stThumbValue"] {{
            color: {ThemeConfig.PRIMARY_COLOR} !important;
        }}
        
        /* ========== 按钮 ========== */
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
        
        /* ========== 分割线 ========== */
        hr {{
            border-color: {border_color};
            opacity: 0.6;
            margin: 1rem 0;
        }}
        
        /* ========== 提示框 ========== */
        .stAlert {{
            border-radius: 10px;
            border: none;
            background-color: {card_bg} !important;
        }}
        .stAlert * {{
            color: {text_color} !important;
        }}
        
        /* ========== 功能卡片 ========== */
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
        
        /* ========== 布局优化 ========== */
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
    """初始化页面配置"""
    st.set_page_config(
        page_title=f"{PROJECT_NAME} v{PROJECT_VERSION}",
        page_icon="📱",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # 初始化状态
    default_states = {
        "dark_mode": False,
        "reviews_df": None,
        "clean_df": None,
        "categories": None,
        "prd_versions": None,
        "test_cases": None,
        "analysis_step": 0
    }
    for key, value in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_sidebar():
    """渲染侧边栏"""
    with st.sidebar:
        st.markdown("### ⚙️ 配置中心")
        st.divider()

        # 夜间模式：最稳妥的写法，点一下就变
        st.markdown("#### 🎨 显示设置")
        new_dark = st.toggle(
            "夜间模式",
            value=st.session_state.dark_mode
        )
        # 直接同步状态，不走回调，避免状态不同步
        if new_dark != st.session_state.dark_mode:
            st.session_state.dark_mode = new_dark
            st.rerun()

        st.divider()

        # 数据源
        st.markdown("#### 📥 数据源")
        data_source = st.radio(
            "数据来源",
            ["在线抓取", "本地文件导入"],
            index=0,
            label_visibility="collapsed"
        )

        st.divider()

        # AI配置
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
    st.title(f"📱 {PROJECT_NAME}")
    st.caption(PROJECT_DESCRIPTION)
    st.divider()


def render_feature_overview():
    """核心能力卡片，填充首页空白"""
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
            help="支持 CSV / JSON 格式，需包含评论ID、评分、评论内容字段"
        )
        return "", 0, uploaded_file


def render_data_limit_note():
    st.info("""
    **📌 数据说明与局限性**
    - 在线抓取数据源为苹果官方 iTunes RSS Feed，仅返回美国区最新评论
    - 官方接口单应用最多返回约500条评论，无法获取全量历史数据
    - 分析结论仅基于样本数据推导，不代表全部用户观点
    - 所有原始数据仅在本地处理，不会上传至第三方服务器
    """)


def main():
    init_page()
    apply_theme(st.session_state.dark_mode)

    data_source, enable_ai, generate_prd, generate_test, example_url = render_sidebar()

    render_header()
    render_feature_overview()

    app_url, max_pages, uploaded_file = render_data_input(data_source, example_url)

    # 按钮居中，控制宽度
    st.markdown("")
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        start_btn = st.button(
            "🚀 开始全流程分析",
            use_container_width=True,
            type="primary"
        )

    if start_btn:
        st.info("🔧 数据抓取与分析模块开发中，下一迭代即将上线...")

    st.divider()
    render_data_limit_note()


if __name__ == "__main__":
    main()
