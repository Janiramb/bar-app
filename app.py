import streamlit as st
import psycopg2
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Bar App", page_icon="🍺")

def conectar_db():
    try:
        # ⚠️ EL SECRETO: El usuario DEBE ser postgres.kljizxbakvzytmaxqodw
        # Esto le dice a Supabase exactamente a qué proyecto entrar
        conn = psycopg2.connect(
            host="aws-0-eu-central-1.pooler.supabase.com",
            port="6543",
            database="postgres",
            user="postgres.kljizxbakvzytmaxqodw", 
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
    with st.spinner('Conectando con el bar...'):
        conn = conectar_db()
    
    if conn:
        st.success(f"✅ ¡POR FIN! Conectado con éxito, {user}")
        # Aquí meteremos los botones de fichaje en cuanto salga el check verde
        conn.close()
    else:
        st.warning("⚠️ Casi lo tenemos, pero el usuario no ha sido reconocido aún.")
