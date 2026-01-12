import streamlit as st
import psycopg2
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Bar App", page_icon="🍺")

def conectar_db():
    try:
        # CONEXIÓN POR IP DIRECTA (Sáltate el error de Host)
        # El host 15.237.253.218 es el que corresponde a tu base de datos
        conn = psycopg2.connect(
            host="15.237.253.218",
            port="5432",
            database="postgres",
            user="postgres",
            password="Tinacasa1999.",
            sslmode="require",
            connect_timeout=30
        )
        return conn
    except Exception as e:
        st.error(f"❌ Error de red: {e}")
        return None

st.title("🍺 Horario Desastre")

user = st.selectbox("¿Quién eres?", ["Selecciona...", "Alex", "Janira", "Iria"])

if user != "Selecciona...":
    with st.spinner('Conectando con el bar...'):
        conn = conectar_db()
    
    if conn:
        st.success(f"✅ ¡POR FIN CONECTADO! Hola {user}")
        # Mantenemos la conexión abierta un segundo para confirmar
        conn.close()
    else:
        st.warning("⚠️ El servidor no responde. Revisa el SSL en Supabase.")
