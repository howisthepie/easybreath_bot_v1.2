import os
from dotenv import load_dotenv

load_dotenv()

conf = {
    "BOT_TOKEN": os.getenv("BOT_TOKEN"),
    "OPENROUTER_API_KEY": os.getenv("OPENROUTER_API_KEY"),
    "OPENROUTER_URL": 'https://openrouter.ai/api/v1/chat/completions',
    "DB_NAME": 'databese.db'
}
