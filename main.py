import logging
import httpx
import aiosqlite
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from core.config import conf
from core.database import create_tables


OPENROUTER_API_KEY = conf['OPENROUTER_API_KEY']
OPENROUTER_URL = conf['OPENROUTER_URL']

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я EasyBreath Bot, персональный помощник.\n"
        "Расскажи, как ты себя чувствуешь или задай вопрос — я помогу!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    user_id = update.message.from_user.id

    await save_message(user_id, 'user', user_message)

    try:
        history = await get_user_history(user_id)
        response_text = await get_openrouter_response(history)
        await save_message(user_id, 'assistant', response_text)
        await update.message.reply_text(response_text)
    except Exception as e:
        logging.error(f'Error: {e}')
        await update.message.reply_text(f'Произошла ошибка:\n```\n{e}\n```')

async def get_openrouter_response(history):
    headers = {
        'Authorization': f'Bearer {OPENROUTER_API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": history
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(OPENROUTER_URL, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']

async def save_message(user_id, role, content):
    async with aiosqlite.connect(conf["DB_NAME"]) as db:
        await db.execute(
            "INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)",
            (user_id, role, content)
        )
        await db.commit()

async def get_user_history(user_id):
    async with aiosqlite.connect(conf["DB_NAME"]) as db:
        cursor = await db.execute(
            "SELECT role, content FROM messages WHERE user_id = ? ORDER BY rowid ASC",
            (user_id,)
        )
        rows = await cursor.fetchall()
        await cursor.close()

    if not rows:
        return [{"role": "system", "content": "You are a helpful assistant."}]

    history = [{'role': role, 'content': content} for role, content in rows]
    return history

async def main():
    await create_tables()
    app = ApplicationBuilder().token(conf['BOT_TOKEN']).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущен...")
    await app.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
