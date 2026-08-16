"""
通用工具函数模块
存放与业务无关的通用辅助方法
"""
import re
import hashlib


def extract_app_id(url: str) -> str:
    """
    从App Store链接中提取应用ID
    支持多种链接格式：
    - https://apps.apple.com/us/app/xxx/id123456789
    - https://itunes.apple.com/us/app/id123456789
    
    Args:
        url: App Store应用链接
        
    Returns:
        提取到的数字ID，提取失败返回空字符串
    """
    if not url:
        return ""
    
    # 匹配 id+数字 的模式
    pattern = r"/id(\d+)"
    match = re.search(pattern, url)
    
    if match:
        return match.group(1)
    return ""


def generate_md5(text: str) -> str:
    """
    生成文本的MD5哈希，用于缓存键生成
    """
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def safe_int(value, default=0) -> int:
    """
    安全的整数转换，转换失败返回默认值
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default
