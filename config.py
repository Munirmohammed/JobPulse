import os
from dataclasses import dataclass
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class EmailConfig:
    address: str
    password: str
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587

@dataclass
class PersonalInfo:
    name: str
    linkedin: str
    github: str
    portfolio: Optional[str] = None

@dataclass
class BotConfig:
    discord_token: Optional[str] = None
    github_token: Optional[str] = None
    google_sheets_creds: Optional[str] = None
    sheet_name: str = "Job Leads"
    daily_email_limit: int = 25
    keywords: List[str] = None
    hunter_api_key: Optional[str] = None  # Free: 100 searches/month at hunter.io
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = [
                'backend developer', 'backend engineer', 'node.js', 'typescript',
                'python developer', 'api developer', 'microservices', 'rest api',
                'database', 'aws', 'docker', 'kubernetes', 'react developer',
                'full stack', 'software engineer', 'web developer', 'remote'
            ]

# Production configuration - now using environment variables for security
CONFIG = BotConfig(
    discord_token=os.getenv('DISCORD_TOKEN'),
    github_token=os.getenv('GITHUB_TOKEN'),
    google_sheets_creds=os.getenv('GOOGLE_SHEETS_CREDS_PATH', './google-sheets-credentials.json'),
    sheet_name='HireBot Leads',
    hunter_api_key=os.getenv('HUNTER_API_KEY')  # Optional free API key
)

EMAIL_CONFIG = EmailConfig(
    address=os.getenv('EMAIL_ADDRESS', 'your-email@gmail.com'),
    password=os.getenv('EMAIL_PASSWORD', 'your-app-password')
)

PERSONAL_INFO = PersonalInfo(
    name=os.getenv('PERSONAL_NAME', 'Your Name'),
    linkedin=os.getenv('PERSONAL_LINKEDIN', 'https://linkedin.com/in/yourprofile'),
    github=os.getenv('PERSONAL_GITHUB', 'https://github.com/yourusername')
)
