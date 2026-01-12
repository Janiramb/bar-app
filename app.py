import streamlit as st
import psycopg2
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Bar App", page_icon="🍺")

def conectar_db():
    try:
        # Usamos el Pooler de AWS que es el más estable para Streamlit
        # IMPORTANTE: El usuario lleva el ID del proyecto al final (.kljizxbakvzytmaxqodw)
        conn = psycopg2.connect(
            host="aws-0-eu-central-1.pooler.supabase.com",
            port="6543",
            database="postgres",
            user="postgres.kljizxbakvzytmaxqodw",
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
    with st.spinner('Despertando la base de datos...'):
        conn = conectar_db()
    
    if conn:
        st.success(f"✅ ¡CONECTADO! Hola {user}")
        # Aquí meteremos la lógica de guardado en el siguiente paso
        conn.close()
    else:
        st.warning("⚠️ El servidor sigue sin responder. Mira el paso de abajo.")
        if st.button("🔄 Reintentar conexión"):
            st.rerun()
