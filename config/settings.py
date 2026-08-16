"""
全局配置模块
统一管理主题配色、模型参数、常量配置，便于全局维护与修改
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# ==============================================
# 主题配色配置（紫色高级感主题）
# ==============================================
class ThemeConfig:
    """主题配色与样式配置"""
    
    # 主色调：深紫罗兰
    PRIMARY_COLOR = "#6C5CE7"
    # 辅助色：淡紫、靛蓝
    SECONDARY_COLOR = "#A29BFE"
    ACCENT_COLOR = "#74B9FF"
    
    # 日间模式
    LIGHT_BG = "#FFFFFF"
    LIGHT_CARD_BG = "#F8F9FA"
    LIGHT_TEXT = "#2D3436"
    LIGHT_SUBTEXT = "#636E72"
    LIGHT_BORDER = "#DFE6E9"
    
    # 夜间模式
    DARK_BG = "#1E1E2E"
    DARK_CARD_BG = "#2D2D44"
    DARK_TEXT = "#DFE6E9"
    DARK_SUBTEXT = "#B2BEC3"
    DARK_BORDER = "#444466"
    
    # 状态色
    SUCCESS_COLOR = "#00B894"
    WARNING_COLOR = "#FDCB6E"
    ERROR_COLOR = "#E17055"
    INFO_COLOR = "#0984E3"


# ==============================================
# 大模型配置
# ==============================================
class LLMConfig:
    """大模型API配置"""
    
    # DeepSeek 配置（OpenAI 兼容格式）
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    
    # 默认模型
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "deepseek-chat")
    # 生成温度：0最严谨，适合数据分析场景
    TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))
    
    # 缓存开关
    ENABLE_CACHE = os.getenv("ENABLE_CACHE", "True").lower() == "true"
    # 缓存目录
    CACHE_DIR = "cache"


# ==============================================
# 数据处理配置
# ==============================================
class DataConfig:
    """数据处理相关常量"""
    
    # 最低评论内容长度（低于此长度视为无效内容）
    MIN_CONTENT_LENGTH = 5
    # 相似度去重阈值
    SIMILARITY_THRESHOLD = 0.9
    # 证据等级划分阈值
    EVIDENCE_HIGH = 10   # >=10条：证据充足
    EVIDENCE_MID = 3     # >=3条：样本有限
    
    # App Store官方接口基础地址（美国区）
    ITUNES_RSS_BASE = "https://itunes.apple.com/us/rss/customerreviews/page={page}/id={app_id}/sortby=mostrecent/json"


# ==============================================
# 项目基础信息
# ==============================================
PROJECT_NAME = "iOS App Review 评论分析与版本规划工具"
PROJECT_VERSION = "1.0.0"
PROJECT_DESCRIPTION = "基于用户评论的自动化产品分析工具，实现评论抓取、AI语义分析、PRD生成与测试用例全链路闭环"
