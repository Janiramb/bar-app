import streamlit as st
import psycopg2
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Horario Desastre", page_icon="🍺")

def conectar_db():
    # DIRECCIÓN MAESTRA: Forzamos la IP y quitamos el nombre que da error
    # Usamos sslmode=require porque la nube lo exige
    DB_URI = "host=15.237.253.218 port=5432 dbname=postgres user=postgres password=Tinacasa1999. sslmode=require"
    
    try:
        # Intentamos conectar con un tiempo de espera largo
        conn = psycopg2.connect(DB_URI, connect_timeout=20)
        return conn
    except Exception as e:
        st.error(f"❌ Fallo de red: {e}")
        return None

st.title("🍺 Horario Desastre")

user = st.selectbox("¿Quién eres?", ["Selecciona...", "Alex", "Janira", "Iria"])

if user != "Selecciona...":
    conn = conectar_db()
    
    if conn:
        st.success(f"✅ ¡Conectado! Hola {user}")
        # Aquí puedes empezar a trabajar
        conn.close()
    else:
        st.warning("⚠️ El servidor no responde. Por favor, dale al botón de abajo para reintentar.")
        if st.button("Reintentar ahora"):
            st.rerun()
