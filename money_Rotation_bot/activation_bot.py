import json
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from key_manager import (
    is_valid_key, is_key_expired, get_user_data,
    activate_key, is_key_used_by_another_user
)

# 🌐 Load/save helpers
def load_json(file):
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# 🏁 Global user state
user_states = {}

# 👋 /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.message.chat_id)
    user_states[chat_id] = {"step": "awaiting_key"}
    await update.message.reply_text(
        "🔐 Welcome to the Activation Bot!\n\n"
        "🖊 Meherbani farma kar pehle apni activation key bhejein is format mein:\n\n"
        "KEY-XXXX-XXXX\n\n"
        "🤝 Shukriya!",
        parse_mode="Markdown"
    )

# 💬 Handle all messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.message.chat_id)
    text = update.message.text.strip()
    name = update.message.from_user.first_name or "User"
    bot_token = context.bot.token

    if chat_id not in user_states:
        await update.message.reply_text("❓ Bara-e-karam pehle /start command bhejein.")
        return

    step = user_states[chat_id]["step"]

    if step == "awaiting_key":
        if not is_valid_key(text):
            await update.message.reply_text("❌ Key ghalat hai ya pehle istemal ho chuki hai.")
            return

        if is_key_used_by_another_user(text, chat_id):
            await update.message.reply_text("🚫 Yeh key kisi aur user se link hai.")
            return

        if is_key_expired(text):
            await update.message.reply_text("⌛ Yeh key expire ho chuki hai. Nayi key ke liye team se rabta karein.")
            return

        user_states[chat_id]["key"] = text
        user_states[chat_id]["step"] = "awaiting_token"
        await update.message.reply_text(
            "✅ Key accepted!\n\n"
            "📨 Ab apna bot token is format mein bhejein:\n"
            "123456789:AaBbCcDdEe...",
            parse_mode="Markdown"
        )

    elif step == "awaiting_token":
        token = text
        key = user_states[chat_id]["key"]

        # 🎯 Activate or renew
        activate_key(key, chat_id, token, name)

        await update.message.reply_text(
            "✅ Bot activation successful!\n\n"
            "📡 Aapka bot 24/7 signal bhejne ke liye tayar hai.\n"
            "🟢 Market k opportunity dety he aap apna signal receive karen gey.",
            parse_mode="Markdown"
        )

        print(f"✅ Key activated for chat_id: {chat_id}")
        del user_states[chat_id]

# 🚀 Run bot
def main():
    TOKEN = "7516463170:AAHvLSFUOCBOJhx7_7IjRVVj4lHrAtxhe7o"  # ← Replace with your activation bot token
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🚀 Activation bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
