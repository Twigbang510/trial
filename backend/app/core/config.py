import os
import dotenv

dotenv.load_dotenv()

class Settings:
    def __init__(self):
        self.PROJECT_NAME: str = os.getenv("PROJECT_NAME")
        self.SECRET_KEY: str = os.getenv("SECRET_KEY")
        self.DATABASE_URL: str = os.getenv("DATABASE_URL")

        # Email config
        self.SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
        self.SMTP_USERNAME: str = os.getenv("SMTP_USERNAME")
        self.SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD")
        self.FROM_EMAIL: str = os.getenv("FROM_EMAIL")

        # Gemini AI config
        self.GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")

        # Validate required environment variables
        required_vars = [
            "SECRET_KEY",
            "DATABASE_URL", 
            "SMTP_USERNAME",
            "SMTP_PASSWORD",
            "FROM_EMAIL",
            "GEMINI_API_KEY"
        ]
        
        missing_vars = [var for var in required_vars if not getattr(self, var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

settings = Settings()
