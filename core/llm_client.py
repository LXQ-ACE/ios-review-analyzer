"""
大模型客户端模块
统一封装AI调用能力，支持结构化输出、缓存、重试
兼容 OpenAI 格式的 API 接口
"""
import json
from openai import OpenAI
from pydantic import ValidationError
from config.settings import LLMConfig
from utils.cache import get_cache, set_cache, build_cache_key


class LLMClient:
    """大模型调用客户端"""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=LLMConfig.DEEPSEEK_API_KEY,
            base_url=LLMConfig.DEEPSEEK_BASE_URL
        )
        self.model = LLMConfig.DEFAULT_MODEL
        self.temperature = LLMConfig.TEMPERATURE
    
    def chat_completion(self, system_prompt: str, user_prompt: str, 
                        response_format=None, max_retries: int = 2) -> str:
        """
        通用文本补全
        
        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            response_format: 响应格式，可选 {"type": "json_object"}
            max_retries: 最大重试次数
            
        Returns:
            模型返回的文本内容
        """
        # 构建缓存键
        cache_key = build_cache_key("llm", system_prompt + user_prompt)
        
        # 尝试读取缓存
        cached = get_cache(cache_key)
        if cached:
            return cached
        
        # 调用模型，支持重试
        last_error = None
        for attempt in range(max_retries + 1):
            try:
                kwargs = {
                    "model": self.model,
                    "temperature": self.temperature,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                }
                
                if response_format:
                    kwargs["response_format"] = response_format
                
                response = self.client.chat.completions.create(**kwargs)
                content = response.choices[0].message.content.strip()
                
                # 写入缓存
                set_cache(cache_key, content)
                return content
                
            except Exception as e:
                last_error = e
                print(f"第 {attempt+1} 次调用失败: {str(e)}")
                continue
        
        raise RuntimeError(f"大模型调用失败，已重试 {max_retices} 次，最后错误: {str(last_error)}")
    
    def structured_completion(self, system_prompt: str, user_prompt: str, 
                              output_schema, max_retries: int = 2):
        """
        结构化输出：强制大模型返回JSON并解析为Pydantic对象
        
        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            output_schema: Pydantic 模型类
            max_retries: 最大重试次数
            
        Returns:
            解析后的 Pydantic 对象
        """
        # 在系统提示词中注入结构要求
        schema_json = output_schema.model_json_schema()
        enhanced_system = f"""{system_prompt}

【输出格式要求】
你必须严格按照以下 JSON Schema 结构输出结果，不得有任何额外说明文字：
{json.dumps(schema_json, ensure_ascii=False, indent=2)}

注意：
1. 只输出合法的 JSON 字符串，不要有 markdown 代码块标记
2. 所有字段必须严格匹配 Schema 定义
3. 数组类型字段即使为空也要返回空数组
"""
        
        last_error = None
        for attempt in range(max_retries + 1):
            try:
                content = self.chat_completion(
                    enhanced_system,
                    user_prompt,
                    response_format={"type": "json_object"}
                )
                
                # 清理可能的 markdown 标记
                content = content.strip()
                if content.startswith("```json"):
                    content = content[7:]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()
                
                # 解析为 Pydantic 对象
                data = json.loads(content)
                result = output_schema(**data)
                return result
                
            except (json.JSONDecodeError, ValidationError) as e:
                last_error = e
                print(f"第 {attempt+1} 次解析失败: {str(e)}")
                continue
        
        raise RuntimeError(f"结构化输出解析失败，最后错误: {str(last_error)}")


# 全局单例
_llm_client = None


def get_llm_client() -> LLMClient:
    """获取大模型客户端单例"""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
