import streamlit as st
import psycopg2
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Bar App", page_icon="🍺")

def conectar_db():
    try:
        # En lugar de una URI larga, separamos los datos para que no haya errores de lectura
        conn = psycopg2.connect(
            host="aws-0-eu-central-1.pooler.supabase.com",
            port="6543",
            database="postgres",
            user="postgres.kljizxbakvzytmaxqodw", # Tu ID de proyecto
            password="Tinacasa1999.", # Tu contraseña
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
    conn = conectar_db()
    
    if conn:
        st.success(f"✅ ¡POR FIN! Conectado con éxito, {user}")
        # Cerramos para probar que la conexión es estable
        conn.close()
    else:
        st.warning("⚠️ Sigue fallando la identificación. Revisa el ID de proyecto.")
