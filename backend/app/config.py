import os
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # HuggingFace API
    hf_token: str = ""
    hf_base_url: str = "https://router.huggingface.co/v1"
    
    # Server config
    host: str = "0.0.0.0"
    port: int = 8000
    
    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    
    # LLM Models
    model_1: str = "openai/gpt-oss-safeguard-20b:groq"
    model_2: str = "moonshotai/Kimi-K2-Instruct-0905:groq"
    model_3: str = "meta-llama/Llama-3.3-70B-Instruct:groq"
    chairman_model: str = "meta-llama/Llama-3.3-70B-Instruct:groq"  # Llama as chairman
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins into a list"""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def council_models(self) -> List[str]:
        """Get all council member models"""
        return [self.model_1, self.model_2, self.model_3]


# Global settings instance
settings = Settings()