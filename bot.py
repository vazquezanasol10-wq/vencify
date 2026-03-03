import os
import sqlite3
import hashlib
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.environ.get("PORT", 10000))

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

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    # IMPORTANTE: poner tu URL de Render después del primer deploy
    RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=f"{RENDER_URL}/{TOKEN}",
        url_path=TOKEN,
    )



