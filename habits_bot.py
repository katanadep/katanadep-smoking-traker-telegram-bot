import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import sqlite3
from datetime import datetime
import json

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def init_db():
    conn = sqlite3.connect('smoking_tracker.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS smoking_records
                 (user_id INTEGER, timestamp TEXT, count INTEGER)''')
    conn.commit()
    conn.close()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(
        text="Open Tracker",
        web_app=WebAppInfo(url="https://your-domain.com/index.html")
    )]]
    
    await update.message.reply_text(
        "Hi! Click the button below to open the smoking tracker:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = json.loads(update.message.web_app_data.data)
        if data.get('action') == 'record_puff':
            user_id = update.effective_user.id
            timestamp = data.get('date')
            count = data.get('count', 1)

            conn = sqlite3.connect('smoking_tracker.db')
            c = conn.cursor()
            c.execute("INSERT INTO smoking_records VALUES (?, ?, ?)", 
                     (user_id, timestamp, count))
            conn.commit()
            conn.close()

    except Exception as e:
        logging.error(f"Error processing web app data: {e}")

def main():
    init_db()
    
    application = Application.builder().token("your-bot-token").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data))

    application.run_polling()

if __name__ == '__main__':
    main()