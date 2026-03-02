import streamlit as st
import hashlib
import sqlite3
import requests
from datetime import datetime, date

st.set_page_config(
    page_title="Vencify ASV",
    page_icon="📦",
    layout="wide"
)

# ----------------------------
# HEADER SIMPLE Y PROFESIONAL
# ----------------------------

col1, col2 = st.columns([1, 6])

with col1:
    st.image("logo.png", width=690)
with col2:
    st.markdown(
        """
        <h1 style='font-size:52px; margin-bottom:0px;'>
            Vencify ASV
        </h1>
        """,
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='color:gray; margin-top:0px;'>Sistema inteligente de gestión de vencimientos</p>",
        unsafe_allow_html=True
    )

st.divider()

# ----------------------------
# CONEXIÓN SQLITE LOCAL
# ----------------------------

conn = sqlite3.connect("usuarios.db", check_same_thread=False)
c = conn.cursor()
# ===============================
# CONFIGURACIÓN LOCAL
# ===============================

TOKEN = st.secrets["BOT_TOKEN"]
BOT_USERNAME = "Controlvencimientos_bot"
ADMIN_CHAT_ID = st.secrets["ADMIN_CHAT_ID"]
# ===============================
# DB SETUP
# ===============================

conn = sqlite3.connect("usuarios.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    chat_id TEXT,
    activo INTEGER DEFAULT 0,
    es_admin INTEGER DEFAULT 0
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS vencimientos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,
    nombre TEXT,
    fecha TEXT,
    unidad INTEGER,
    alertas_enviadas TEXT DEFAULT ''
)
""")

conn.commit()

try:
    c.execute("ALTER TABLE vencimientos ADD COLUMN alertas_enviadas TEXT DEFAULT ''")
    conn.commit()
except:
    pass
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Crear admin automáticamente si no existe
admin_password = hash_password("admin123")

c.execute("""
INSERT OR IGNORE INTO usuarios
(username, password, chat_id, activo, es_admin)
VALUES (?, ?, ?, 1, 1)
""", ("admin_master", admin_password, ADMIN_CHAT_ID))

conn.commit()

# ===============================
# FUNCIONES
# ===============================
def enviar_mensaje(chat_id, texto):
    url = f"https://api.telegram.org/bot8594278387:AAGOQfqMtNmQjX1O3UXLDl4kRkO2l5NyoNY/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": texto
    }
    requests.post(url, data=data)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verificar_login(username, password):
    password_hash = hash_password(password)

    c.execute("""
        SELECT id, username, chat_id, es_admin, activo
        FROM usuarios
        WHERE username=? AND password=?
    """, (username, password_hash))

    user = c.fetchone()

    if user is None:
        return None

    if user[4] == 0:
        return "inactivo"

    return {
        "id": user[0],
        "username": user[1],
        "chat_id": user[2],
        "es_admin": user[3]
    }

def enviar_mensaje(chat_id, texto):
    url = f"https://api.telegram.org/bot8594278387:AAGOQfqMtNmQjX1O3UXLDl4kRkO2l5NyoNY/sendMessage"
    payload = {"chat_id": chat_id, "text": texto}
    requests.post(url, data=payload)

def verificar_alertas(usuario_id, chat_id):
    hoy = date.today()

    c.execute("""
        SELECT id, nombre, fecha, alertas_enviadas
        FROM vencimientos
        WHERE usuario_id=?
    """, (usuario_id,))

    vencs = c.fetchall()

    for v in vencs:
        producto_id = v[0]
        nombre = v[1]
        fecha_v = datetime.strptime(v[2], "%Y-%m-%d").date()
        dias = (fecha_v - hoy).days

        alertas_enviadas = v[3]
        if alertas_enviadas:
            alertas_enviadas = alertas_enviadas.split(",")
        else:
            alertas_enviadas = []

        mensaje = None
        codigo_alerta = None

        if dias == 12:
            codigo_alerta = "12"
            mensaje = f"📦 {nombre}\nFaltan 12 días.\n👉 Ponelo más cerca de la caja."

        elif dias == 10:
            codigo_alerta = "10"
            mensaje = f"📦 {nombre}\nFaltan 10 días.\n💰 Sugerencia: 20% de descuento."

        elif dias == 7:
            codigo_alerta = "7"
            mensaje = f"📦 {nombre}\nFaltan 7 días.\n🔥 30% de descuento."

        elif dias == 5:
            codigo_alerta = "5"
            mensaje = f"📦 {nombre}\nFaltan 5 días.\n🎯 Promo por cantidad."

        elif dias == 3:
            codigo_alerta = "3"
            mensaje = f"📦 {nombre}\nFaltan 3 días.\n⚡ HACÉ UN 2x1."

        elif dias == 2:
            codigo_alerta = "2"
            mensaje = f"⚠️⚠️ {nombre} VENCE EN 2 DÍAS ⚠️⚠️"

        elif dias == 1:
            codigo_alerta = "1"
            mensaje = f"🚨🚨 {nombre} VENCE MAÑANA 🚨🚨"

        # SOLO ENVÍA SI NO FUE ENVIADA ANTES
        if mensaje and codigo_alerta not in alertas_enviadas:
            enviar_mensaje(chat_id, mensaje)

            alertas_enviadas.append(codigo_alerta)
            nuevo_valor = ",".join(alertas_enviadas)

            c.execute("""
                UPDATE vencimientos
                SET alertas_enviadas=?
                WHERE id=?
            """, (nuevo_valor, producto_id))

            conn.commit()

# ===============================
# SESSION INIT
# ===============================

if "usuario_id" not in st.session_state:
    st.session_state.usuario_id = None

# ===============================
# NO LOGUEADO
# ===============================

if st.session_state.usuario_id is None:

    st.title("📦 Sistema de Vencimientos")

    st.markdown("### 📲 Paso 1: Registrate con Telegram")

    st.markdown("""
1️⃣ Abrí el bot  
2️⃣ Escribí **/start**  
3️⃣ Recibirás tu contraseña  
4️⃣ Esperá aprobación  
5️⃣ Iniciá sesión  
""")

    st.link_button("🚀 Abrir Telegram", f"https://t.me/Controlvencimientos_bot")

    st.divider()

    st.subheader("🔐 Iniciar sesión")

    username = st.text_input("Usuario (tu username de Telegram)")
    password = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):
        usuario = verificar_login(username, password)

        if usuario is None:
            st.error("Usuario o contraseña incorrectos")

        elif usuario == "inactivo":
            st.warning("Tu cuenta aún no fue aprobada por el administrador")

        else:
            st.session_state.usuario_id = usuario["id"]
            st.session_state.username = usuario["username"]
            st.session_state.chat_id = usuario["chat_id"]
            st.session_state.es_admin = usuario["es_admin"]
            st.rerun()

# ===============================
# LOGUEADO
# ===============================

else:

    st.sidebar.write(f"👤 {st.session_state.username}")

    if st.sidebar.button("Cerrar sesión"):
        st.session_state.usuario_id = None
        st.rerun()

    # ================= ADMIN PANEL =================

    if st.session_state.es_admin == 1:

        st.title("🛠 Panel Admin")

        st.subheader("Usuarios pendientes")

        c.execute("SELECT id, username FROM usuarios WHERE activo=0")
        pendientes = c.fetchall()

        for u in pendientes:

            st.write(f"Usuario: {u[1]}")

    # BOTÓN APROBAR
            if st.button("Aprobar", key=f"aprobar_{u[0]}"):

                c.execute("UPDATE usuarios SET activo=1 WHERE id=?", (u[0],))
                conn.commit()
                c.execute("SELECT chat_id, username, password FROM usuarios WHERE id=?", (u[0],))
                usuario_aprobado = c.fetchone()

                if usuario_aprobado:
                    chat_id = usuario_aprobado[0]
                    username = usuario_aprobado[1]
                    password = usuario_aprobado[2]

                    mensaje = f"""
🎉 BIENVENIDO A VENCIFY ASV

Tu cuenta fue APROBADA ✅

🔑 Usuario: {username}
🔐 Contraseña: {password}

Ingresá a la app:
http://localhost:8501
"""

                    enviar_mensaje(chat_id, mensaje)

                st.success("Usuario aprobado y notificado ✅")


    # BOTÓN RECHAZAR
            if st.button("Rechazar", key=f"rechazar_{u[0]}"):

                c.execute("SELECT chat_id, username FROM usuarios WHERE id=?", (u[0],))
                usuario_rechazado = c.fetchone()

                if usuario_rechazado:
                    chat_id = usuario_rechazado[0]
                    username = usuario_rechazado[1]

                    mensaje = f"""
❌ SOLICITUD RECHAZADA

Hola {username},

Tu solicitud fue rechazada por el administrador.

Podés volver a intentar enviando /start nuevamente dentro de 1 hora.

Gracias por tu interés en Vencify ASV.
"""

                    enviar_mensaje(chat_id, mensaje)

                c.execute("DELETE FROM usuarios WHERE id=?", (u[0],))
                conn.commit()
                st.warning("Usuario rechazado y notificado ❌")
        st.subheader("👀 Ver productos de usuarios")

        c.execute("SELECT id, username FROM usuarios WHERE activo=1 AND es_admin=0")
        usuarios_activos = c.fetchall()

        for usr in usuarios_activos:
            if st.button(f"Ver productos de {usr[1]}", key=f"ver_{usr[0]}"):

                c.execute("""
            SELECT nombre, fecha, unidad
            FROM vencimientos
            WHERE usuario_id=?
        """, (usr[0],))

                productos = c.fetchall()

                if productos:
                    st.write(f"📦 Productos de {usr[1]}:")
                    for p in productos:
                        st.write(f"- {p[0]} | Vence: {p[1]} | Stock: {p[2]}")
                else:
                    st.info("No tiene productos registrados.")

    # ================= USUARIO NORMAL =================


    st.title("📦 Mis Vencimientos")

    nombre = st.text_input("Nombre del producto")
    fecha = st.date_input("Fecha de vencimiento")
    unidad = st.number_input("Stock", min_value=1)

    if st.button("Agregar vencimiento"):
        c.execute("""
            INSERT INTO vencimientos (usuario_id, nombre, fecha, unidad)
            VALUES (?, ?, ?, ?)
        """, (
            st.session_state.usuario_id,
            nombre,
            fecha.strftime("%Y-%m-%d"),
            unidad
        ))
        conn.commit()
        st.success("Vencimiento agregado")
        st.rerun()

    st.divider()

    c.execute("""
        SELECT id, nombre, fecha, unidad
        FROM vencimientos
        WHERE usuario_id=?
    """, (st.session_state.usuario_id,))

    vencs = c.fetchall()

    for v in vencs:
        fecha_v = datetime.strptime(v[2], "%Y-%m-%d").date()
        dias = (fecha_v - date.today()).days

        st.write(f"**{v[1]}** - {v[2]} - {dias} días restantes - Stock: {v[3]}")

        if st.button(
            f"Consumir 1 unidad de {v[1]}",
            key=f"consumir_{v[0]}"):
            nuevo_stock = v[3] - 1

            if nuevo_stock <= 0:
                c.execute("DELETE FROM vencimientos WHERE id=?", (v[0],))
                conn.commit()
                st.success(f"{v[1]} eliminado (stock agotado)")
            else:
                c.execute("UPDATE vencimientos SET unidad=? WHERE id=?", (nuevo_stock, v[0]))
                conn.commit()

            st.rerun()

    verificar_alertas(st.session_state.usuario_id, st.session_state.chat_id)




