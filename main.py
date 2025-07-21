import logging
import httpx
import aiosqlite
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from core.config import conf

logging.basicConfig(level=logging.INFO)
