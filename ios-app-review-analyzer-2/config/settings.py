from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    llm_base_url: str = os.getenv("LLM_BASE_URL")
    llm_api_key: str = os.getenv("LLM_API_KEY")
    llm_model_name: str = os.getenv("LLM_MODEL_NAME")

settings = Settings()
