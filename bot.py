import os
import telebot
from supabase import create_client

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
    # Buscar si ya existe por chat_id
    user = supabase.table("usuarios").select("*").eq("chat_id", chat_id).execute()
    if user.data:
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

# -------------------------
# Manejador del comando /start
# -------------------------
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = str(message.chat.id)

    # Generar username y password para prueba
    username = f"user{chat_id}"
    password = "temporal123"

    respuesta = registrar_usuario(chat_id, username, password)
    bot.reply_to(message, respuesta)

# -------------------------
# Arrancar el bot
# -------------------------
if __name__ == "__main__":
    print("Bot iniciado...")
    bot.infinity_polling()






