import streamlit as st
import psycopg2
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Bar App", page_icon="🍺")

def conectar_db():
    # Esta es la cadena de conexión completa (URI). 
    # Es la forma más segura de que Supabase reconozca tu 'Tenant' (proyecto)
    DB_URI = "postgresql://postgres.kljizxbakvzytmaxqodw:Tinacasa1999.@aws-0-eu-central-1.pooler.supabase.com:6543/postgres?sslmode=require"
    
    try:
        # Conectamos usando la URI directamente
        return psycopg2.connect(DB_URI, connect_timeout=30)
    except Exception as e:
        st.error(f"❌ Error de red: {e}")
        return None

st.title("🍺 Horario Desastre")

user = st.selectbox("¿Quién eres?", ["Selecciona...", "Alex", "Janira", "Iria"])

if user != "Selecciona...":
    with st.spinner('Entrando en la base de datos...'):
        conn = conectar_db()
    
    if conn:
        st.success(f"✅ ¡POR FIN! Conectado con éxito, {user}")
        # Aquí meteremos los botones en cuanto salga este mensaje verde
        conn.close()
    else:
        st.warning("⚠️ El servidor sigue sin reconocer el usuario. Mira el paso de abajo.")
