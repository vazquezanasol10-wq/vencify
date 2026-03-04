import os
import telebot
from supabase import create_client
from flask import Flask
import threading

# -------------------------
# Configuración de Supabase
# -------------------------
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------------
# Configuración del bot
# -------------------------
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# -------------------------
# Función para registrar usuarios
# -------------------------
def registrar_usuario(chat_id, username, password):
    try:
        # Chequear si ya existe
        user = supabase.table("usuarios").select("*").eq("chat_id", chat_id).execute()
        if user.data and len(user.data) > 0:
            return "Ya estás registrado"
        
        # Insertar nuevo usuario
        res = supabase.table("usuarios").insert({
            "username": username,
            "password": password,
            "chat_id": chat_id,
            "activo": True
        }).execute()

        if res.error:
            return f"Error al registrar: {res.error.message}"
        return "Registro exitoso"
    except Exception as e:
        return f"Error inesperado: {str(e)}"

# -------------------------
# Comando /start de Telegram
# -------------------------
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = str(message.chat.id)
    username = f"user{chat_id}"
    password = "temporal123"

    respuesta = registrar_usuario(chat_id, username, password)
    bot.reply_to(message, respuesta)

# -------------------------
# Flask dummy para Render
# -------------------------
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot Vencify corriendo"

# -------------------------
# Arrancar bot en hilo aparte
# -------------------------
threading.Thread(target=lambda: bot.infinity_polling()).start()

# Arrancar Flask en el puerto que Render requiere
port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)



