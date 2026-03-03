import os
import sqlite3
import hashlib
import random
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# 🔐 Token desde variable de entorno
TOKEN = os.getenv("BOT_TOKEN")

# Base de datos
conn = sqlite3.connect("usuarios.db", check_same_thread=False)
c = conn.cursor()

def generar_password():
    return str(random.randint(1000, 9999))

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    chat_id = str(update.effective_chat.id)

    if username is None:
        await update.message.reply_text("Necesitás tener username en Telegram.")
        return

    password = generar_password()
    password_hash = hash_password(password)

    try:
        c.execute("""
        INSERT INTO usuarios (username, password, chat_id, activo, es_admin)
        VALUES (?, ?, ?, 0, 0)
        """, (username, password_hash, chat_id))
        conn.commit()

        await update.message.reply_text(
            f"Registro enviado.\nTu contraseña es: {password}\nEsperá aprobación del admin."
        )

    except:
        await update.message.reply_text("Ya estás registrado.")

# Crear app Telegram
telegram_app = ApplicationBuilder().token(TOKEN).build()
telegram_app.add_handler(CommandHandler("start", start))

# Crear Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot activo 🚀"

@app.route(f"/{TOKEN}", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    await telegram_app.process_update(update)
    return "OK"

if _name_ == "_main_":
    PORT = int(os.environ.get("PORT", 10000))

    # Cambiar esto después con tu URL real de Render
    RENDER_URL = "https://vencify-bot.onrender.com"

    telegram_app.bot.set_webhook(url=f"{RENDER_URL}/{TOKEN}")

    app.run(host="0.0.0.0", port=PORT)

