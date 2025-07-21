import logging
import httpx
import sqlite3
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TELEGRAM_TOKEN = '7755502455:AAE_IJSovKqsc67zc04q_3-QnTE5TJfduoc'
OPENROUTER_API_KEY = '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'
OPENROUTER_URL = 'https://openrouter.ai/api/v1/chat/completions'

DB_NAME = 'chat_history.db'

logging.basicConfig(level=logging.INFO)

# Создание базы данных и таблицы
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            user_id INTEGER,
            role TEXT,
            content TEXT
        )
    ''')
    conn.commit()
    conn.close()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = (
        "Привет! Я EasyBreath Bot, персональный помощник.\n"
        "Расскажи, как ты себя чувствуешь или задай вопрос — я помогу!"
    )
    await update.message.reply_text(message)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    user_id = update.message.from_user.id

    # Сохраняем сообщение пользователя
    save_message(user_id, 'user', user_message)

    try:
        # Получаем всю историю диалогов пользователя
        history = get_user_history(user_id)
        response_text = await get_openrouter_response(history)
        
        # Сохраняем ответ бота
        save_message(user_id, 'assistant', response_text)
        
        await update.message.reply_text(response_text)
    except Exception as e:
        logging.error(f'Error: {e}')
        await update.message.reply_text('Произошла ошибка при обращении к OpenRouter API.')

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

def save_message(user_id, role, content):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO messages (user_id, role, content)
        VALUES (?, ?, ?)
    ''', (user_id, role, content))
    conn.commit()
    conn.close()

def get_user_history(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT role, content FROM messages
        WHERE user_id = ?
        ORDER BY rowid ASC
    ''', (user_id,))
    rows = cursor.fetchall()
    conn.close()

    history = [{'role': role, 'content': content} for role, content in rows]
    return history

def main():
    init_db()
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущен...")
    app.run_polling()

if __name__ == '__main__':
    main()
