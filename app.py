import streamlit as st
import psycopg2
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Bar App", page_icon="🍺")

def conectar_db():
    # ⚠️ CAMBIO CLAVE: El usuario ahora incluye el ID de tu proyecto (postgres.kljizxbakvzytmaxqodw)
    # Esto es obligatorio para usar el puerto 6543 en Supabase
    DB_URI = "postgresql://postgres.kljizxbakvzytmaxqodw:Tinacasa1999.@aws-0-eu-central-1.pooler.supabase.com:6543/postgres?sslmode=require"
    
    try:
        # Intentamos conectar con un tiempo de espera de 15 segundos
        return psycopg2.connect(DB_URI, connect_timeout=15)
    except Exception as e:
        st.error(f"❌ Error de red: {e}")
        return None

st.title("🍺 Horario Desastre")

user = st.selectbox("¿Quién eres?", ["Selecciona...", "Alex", "Janira", "Iria"])

if user != "Selecciona...":
    conn = conectar_db()
    
    if conn:
        st.success(f"✅ ¡Conectado con éxito! Hola {user}")
        # Aquí es donde pondremos los botones de fichar en el siguiente paso
        conn.close()
    else:
        st.warning("⚠️ No se pudo establecer la conexión. Revisa los logs de la App.")
