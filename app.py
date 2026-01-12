import streamlit as st
import psycopg2
import time
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Bar App", page_icon="🍺")

def conectar_db():
    # Usamos la IP directa y el formato más compatible
    DB_URI = "host=15.237.253.218 port=5432 dbname=postgres user=postgres password=Tinacasa1999. sslmode=require"
    
    intentos = 0
    while intentos < 3:
        try:
            # Intentamos conectar con un tiempo de espera muy amplio
            conn = psycopg2.connect(DB_URI, connect_timeout=30)
            return conn
        except Exception as e:
            intentos += 1
            if intentos == 3:
                st.error(f"❌ Agotados los 3 intentos de red: {e}")
                return None
            time.sleep(2) # Esperamos 2 segundos antes de reintentar

st.title("🍺 Horario Desastre")

user = st.selectbox("¿Quién eres?", ["Selecciona...", "Alex", "Janira", "Iria"])

if user != "Selecciona...":
    with st.spinner('Conectando con la base de datos...'):
        conn = conectar_db()
    
    if conn:
        st.success(f"✅ ¡Conectado! Hola {user}")
        # Aquí cargaríamos el resto de la App
        conn.close()
    else:
        st.warning("⚠️ Supabase no responde. Por favor, revisa el paso de abajo.")
        if st.button("🔄 Forzar Reintento"):
            st.rerun()
