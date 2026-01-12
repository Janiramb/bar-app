import streamlit as st
import psycopg2
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Bar App", page_icon="🍺")

def conectar_db():
    # USAMOS EL PUERTO 6543 (Transaction Pooler)
    # Reemplaza [TU-PROYECTO-ID] por: kljizxbakvzytmaxqodw
    # La contraseña es la que ya tienes: Tinacasa1999.
    DB_URI = "postgresql://postgres.kljizxbakvzytmaxqodw:Tinacasa1999.@aws-0-eu-central-1.pooler.supabase.com:6543/postgres?sslmode=require"
    
    try:
        return psycopg2.connect(DB_URI, connect_timeout=15)
    except Exception as e:
        st.error(f"❌ Error de red: {e}")
        return None

st.title("🍺 Horario Desastre")

user = st.selectbox("¿Quién eres?", ["Selecciona...", "Alex", "Janira", "Iria"])

if user != "Selecciona...":
    conn = conectar_db()
    
    if conn:
        st.success(f"✅ ¡Conectado! Hola {user}")
        # Aquí va el resto de tu lógica de botones
        conn.close()
    else:
        st.warning("⚠️ El servidor está tardando en responder. Prueba a recargar la página.")
