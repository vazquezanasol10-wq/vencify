import os
import telebot
from supabase import create_client
from flask import Flask
import requests

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
PORT = int(os.environ.get("PORT", 10000))

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Eliminar webhook si existe
requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/deleteWebhook")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

def registrar_usuario(chat_id):
    username = f"user{chat_id}"
    password = "temporal123"

    try:
        supabase.table("usuarios").upsert({
            "username": username,
            "password": password,
            "chat_id": chat_id,
            "activo": True
        }, on_conflict="chat_id").execute()

        return "Registro exitoso"

    except Exception as e:
        return f"Error inesperado: {str(e)}"


@bot.message_handler(commands=['start'])
def start(message):
    chat_id = str(message.chat.id)
    bot.reply_to(message, registrar_usuario(chat_id))


@bot.message_handler(commands=['ping'])
def ping(message):
    bot.reply_to(message, "pong ✅")


@app.route("/")
def home():
    return "Vencify corriendo 🚀"


if __name__ == "__main__":
    from threading import Thread

    # Flask en un hilo
    Thread(target=lambda: app.run(host="0.0.0.0", port=PORT)).start()

    # Polling en el proceso principal (SIN threading extra)
    bot.infinity_polling(skip_pending=True)
