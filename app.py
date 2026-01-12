import streamlit as st
import psycopg2
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Bar App", page_icon="🍺")

def conectar_db():
    # Usamos el formato DSN que es más estable en la nube
    # Forzamos la IP directa para evitar fallos de nombre
    DB_URI = "host=15.237.253.218 port=5432 dbname=postgres user=postgres password=Tinacasa1999. sslmode=require"
    
    try:
        # Aumentamos el tiempo de espera a 30 segundos
        conn = psycopg2.connect(DB_URI, connect_timeout=30)
        return conn
    except Exception as e:
        # Usamos st.error en lugar de messagebox
        st.error(f"❌ Error de red: {e}")
        return None

st.title("🍺 Horario Desastre")

user = st.selectbox("¿Quién eres?", ["Selecciona...", "Alex", "Janira", "Iria"])

if user != "Selecciona...":
    conn = conectar_db()
    
    if conn:
        st.success(f"✅ ¡Conectado! Hola {user}")
        # Solo si hay conexión, creamos el cursor
        cur = conn.cursor()
        
        if user == "Alex":
            st.subheader("Panel de Consulta")
            st.info("Alex, aquí verás pronto el resumen de horas.")
        else:
            st.subheader(f"Panel de {user}")
            if st.button("📝 Fichar ahora", use_container_width=True):
                st.info("Registro de turno activado.")
        
        cur.close()
        conn.close()
    else:
        st.warning("⚠️ No se pudo conectar. Por favor, pulsa el botón de abajo.")
        if st.button("🔄 Reintentar"):
            st.rerun()
