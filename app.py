import streamlit as st
import psycopg2
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Bar App", page_icon="🍺")

def conectar_db():
    try:
        # Usamos la conexión directa (Puerto 5432)
        # El host es tu dirección completa de Supabase
        # El usuario es solo 'postgres' (aquí NO se pone el ID del proyecto)
        conn = psycopg2.connect(
            host="db.kljizxbakvzytmaxqodw.supabase.co",
            port="5432",
            database="postgres",
            user="postgres",
            password="Tinacasa1999.",
            sslmode="require",
            connect_timeout=20
        )
        return conn
    except Exception as e:
        st.error(f"❌ Error de red: {e}")
        return None

st.title("🍺 Horario Desastre")

user = st.selectbox("¿Quién eres?", ["Selecciona...", "Alex", "Janira", "Iria"])

if user != "Selecciona...":
    with st.spinner('Conectando...'):
        conn = conectar_db()
    
    if conn:
        st.success(f"✅ ¡POR FIN! Conectado con éxito, {user}")
        conn.close()
    else:
        st.warning("⚠️ Sigue sin conectar. Vamos a revisar la IP.")
