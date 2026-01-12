import streamlit as st
import psycopg2
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Bar App", page_icon="🍺")

def conectar_db():
    # El usuario para el Pooler DEBE ser: nombre_usuario.ID_PROYECTO
    # Tu ID de proyecto es: kljizxbakvzytmaxqodw
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
        # Aquí ya puedes poner tus botones de fichar
        conn.close()
    else:
        st.warning("⚠️ Error de acceso. Revisa los datos de conexión.")
