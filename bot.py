import os
import telebot
from supabase import create_client
from flask import Flask
import threading
import requests

# -------------------------
# Configuración de variables
# -------------------------
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
PORT = int(os.environ.get("PORT", 10000))

if not SUPABASE_URL or not SUPABASE_KEY or not TELEGRAM_TOKEN:
    raise Exception("❌ Asegurate de haber seteado SUPABASE_URL, SUPABASE_KEY y TELEGRAM_TOKEN")

# -------------------------
# Inicializar Supabase y Telebot
# -------------------------
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Borrar webhook activo (previene error 409)
requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/deleteWebhook")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# -------------------------
# Función para registrar usuarios con upsert usando chat_id
# -------------------------
def registrar_usuario(chat_id):
    username = f"user{chat_id}"
    password = "temporal123"

    try:
        res = supabase.table("usuarios").upsert(
            {
                "username": username,
                "password": password,
                "chat_id": chat_id,
                "activo": True
            },
            on_conflict="chat_id"
        ).execute()

        return "Registro exitoso"

    except Exception as e:
        return f"Error inesperado: {str(e)}"
# -------------------------
# Comandos del bot
# -------------------------
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = str(message.chat.id)
    respuesta = registrar_usuario(chat_id)
    bot.reply_to(message, respuesta)

@bot.message_handler(commands=['ping'])
def ping(message):
    bot.reply_to(message, "pong ✅")

# -------------------------
# Flask dummy para Render
# -------------------------
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot Vencify corriendo 🚀"

# -------------------------
# Hilo para polling
# -------------------------
threading.Thread(target=lambda: bot.infinity_polling()).start()

# -------------------------
# Arrancar Flask en puerto Render
# -------------------------
if __name__ == "__main__":
    print("Bot iniciado y Flask corriendo...")
    app.run(host="0.0.0.0", port=PORT)



