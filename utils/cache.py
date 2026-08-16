"""
结果缓存模块
对大模型分析结果进行本地缓存，避免重复调用，提升性能并降低成本
"""
import os
import json
from config.settings import LLMConfig
from utils.helpers import generate_md5


def _get_cache_path(cache_key: str) -> str:
    """获取缓存文件路径"""
    if not os.path.exists(LLMConfig.CACHE_DIR):
        os.makedirs(LLMConfig.CACHE_DIR, exist_ok=True)
    return os.path.join(LLMConfig.CACHE_DIR, f"{cache_key}.json")


def get_cache(cache_key: str):
    """
    读取缓存结果
    
    Args:
        cache_key: 缓存键
        
    Returns:
        缓存数据，不存在返回None
    """
    if not LLMConfig.ENABLE_CACHE:
        return None
    
    path = _get_cache_path(cache_key)
    if not os.path.exists(path):
        return None
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def set_cache(cache_key: str, data):
    """
    写入缓存结果
    
    Args:
        cache_key: 缓存键
        data: 要缓存的数据
    """
    if not LLMConfig.ENABLE_CACHE:
        return
    
    path = _get_cache_path(cache_key)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def build_cache_key(prefix: str, content: str) -> str:
    """
    构建标准化缓存键
    """
    content_hash = generate_md5(content)
    return f"{prefix}_{content_hash}"
