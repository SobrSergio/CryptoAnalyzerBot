import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
DATABASE_URL = os.getenv('DATABASE_URL')