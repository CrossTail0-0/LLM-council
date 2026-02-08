import os
from dotenv import load_dotenv
from typing import List

# Load environment variables
load_dotenv()


class Settings:
    """Application settings loaded from environment variables"""
    
    def __init__(self):
        # HuggingFace API
        self.hf_token = os.getenv("HF_TOKEN", "")
        self.hf_base_url = os.getenv("HF_BASE_URL", "https://router.huggingface.co/v1")
        
        # Server config
        self.host = os.getenv("HOST", "0.0.0.0")
        self.port = int(os.getenv("PORT", "8000"))
        
        # CORS
        self.cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173")
        
        # LLM Models
        self.model_1 = os.getenv("MODEL_1", "openai/gpt-oss-safeguard-20b:groq")
        self.model_2 = os.getenv("MODEL_2", "moonshotai/Kimi-K2-Instruct-0905:groq")
        self.model_3 = os.getenv("MODEL_3", "meta-llama/Llama-3.3-70B-Instruct:groq")
        self.chairman_model = os.getenv("CHAIRMAN_MODEL", "meta-llama/Llama-3.3-70B-Instruct:groq")
    
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