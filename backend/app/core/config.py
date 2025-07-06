import os
import dotenv

dotenv.load_dotenv()

class Settings:
    def __init__(self):
        self.PROJECT_NAME: str = os.getenv("PROJECT_NAME")
        self.SECRET_KEY: str = os.getenv("SECRET_KEY")
        self.MONGODB_URL: str = os.getenv("MONGODB_URL")
        self.MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "trial_webapp")
        self.ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

        # Email config
        self.SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
        self.SMTP_USERNAME: str = os.getenv("SMTP_USERNAME")
        self.SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD")
        self.FROM_EMAIL: str = os.getenv("FROM_EMAIL")

        # Gemini AI config
        self.GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")

        # OpenAI AI config (OPTIONAL)
        self.OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
        self.OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "")
        self.MODERATION_HARMFUL_THRESHOLD: float = float(os.getenv("MODERATION_HARMFUL_THRESHOLD", "0.7"))

        # NEW: Moderation method selection
        self.MODERATION_METHOD: str = os.getenv("MODERATION_METHOD", "auto")  # auto, local, gemini, openai, ensemble
        
        # Validate moderation method
        valid_methods = ["auto", "local", "gemini", "openai", "ensemble", "keywords"]
        if self.MODERATION_METHOD.lower() not in valid_methods:
            raise ValueError(f"Invalid MODERATION_METHOD: {self.MODERATION_METHOD}. Must be one of: {', '.join(valid_methods)}")

        # Validate required environment variables
        required_vars = [
            "SECRET_KEY",
            "SMTP_USERNAME",
            "SMTP_PASSWORD",
            "FROM_EMAIL",
            "GEMINI_API_KEY",
            # "OPENAI_API_KEY",
            # "OPENAI_MODEL"
        ]
        
        missing_vars = [var for var in required_vars if not getattr(self, var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

        # Log moderation configuration
        self._log_moderation_config()

    def _log_moderation_config(self):
        """Log the current moderation configuration"""
        import logging
        logger = logging.getLogger(__name__)
        
        print(f"Moderation Configuration:")
        print(f"Method: {self.MODERATION_METHOD}")
        print(f"Threshold: {self.MODERATION_HARMFUL_THRESHOLD}")
        print(f"Gemini API: {'Available' if self.GEMINI_API_KEY else 'Not configured'}")
        print(f"OpenAI API: {'Available' if self.OPENAI_API_KEY else 'Not configured'}")
        
        # Check local models availability
        try:
            import torch
            import transformers
            print(f"Local Models: Available (PyTorch {torch.__version__}, Transformers {transformers.__version__})")
        except ImportError:
            print(f"Local Models: Not available (missing dependencies)")

settings = Settings()
