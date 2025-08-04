"""
Configuration utilities for the AI Resume Assistant.
"""

import os
from dotenv import load_dotenv
from typing import Optional
import streamlit as st

# Load environment variables
load_dotenv()


class Config:
    """Configuration management for the application."""
    
    # OpenRouter Settings
    OPENROUTER_API_KEY: Optional[str] = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    
    # LangChain Settings
    LANGCHAIN_TRACING_V2: str = os.getenv("LANGCHAIN_TRACING_V2", "false")
    LANGCHAIN_ENDPOINT: str = os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")
    LANGCHAIN_API_KEY: Optional[str] = os.getenv("LANGCHAIN_API_KEY")
    LANGCHAIN_PROJECT: str = os.getenv("LANGCHAIN_PROJECT", "ai-resume-assistant")
    
    # App Settings
    MAX_FILE_SIZE_MB: int = 10
    SUPPORTED_FILE_TYPES: list = ['.pdf']
    
    # UI Settings
    APP_TITLE: str = "AI Resume Assistant"
    APP_DESCRIPTION: str = "Analyze your resume against job descriptions for better matching"
    
    @classmethod
    def get_openrouter_api_key(cls) -> str:
        """Get OpenRouter API key from environment or Streamlit secrets."""
        # Try environment variable first
        api_key = cls.OPENROUTER_API_KEY
        
        # Fallback to Streamlit secrets
        if not api_key and hasattr(st, 'secrets'):
            try:
                api_key = st.secrets.get("OPENROUTER_API_KEY")
            except Exception:
                pass
        
        if not api_key:
            raise ValueError(
                "OpenRouter API key not found. Please set OPENROUTER_API_KEY environment variable "
                "or add it to Streamlit secrets."
            )
        
        return api_key
    
    @classmethod
    def validate_config(cls) -> dict:
        """Validate configuration and return status."""
        validation = {
            "valid": True,
            "issues": []
        }
        
        # Check OpenRouter API key
        try:
            cls.get_openrouter_api_key()
        except ValueError as e:
            validation["valid"] = False
            validation["issues"].append(str(e))
        
        return validation


# UI Configuration
UI_CONFIG = {
    "page_config": {
        "page_title": Config.APP_TITLE,
        "page_icon": "📋",
        "layout": "wide",
        "initial_sidebar_state": "expanded"
    },
    "colors": {
        "primary": "#1f77b4",
        "secondary": "#ff7f0e",
        "success": "#2ca02c",
        "warning": "#ff7f0e",
        "danger": "#d62728"
    },
    "styling": {
        "hide_menu": True,
        "hide_footer": True,
        "show_toolbar": False
    }
}

# Analysis Configuration
ANALYSIS_CONFIG = {
    "scoring": {
        "excellent": 80,
        "good": 60,
        "fair": 40,
        "poor": 0
    },
    "keywords": {
        "min_length": 3,
        "max_keywords": 50,
        "exclude_common": True
    },
    "recommendations": {
        "max_suggestions": 10,
        "priority_levels": ["high", "medium", "low"]
    }
} 