import streamlit as st
import psycopg2
from datetime import datetime, timedelta

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Bar App", page_icon="🍺")

# --- CONEXIÓN DIRECTA A LA NUBE ---
def conectar_db():
    # 1. Usamos el puerto 6543 (Transaction Pooler) que es más estable para Apps
    # 2. Añadimos sslmode=require para que la nube lo acepte
    DB_URI = "postgresql://postgres:Tinacasa1999.@db.kljizxbakvzytmaxqodw.supabase.co:6543/postgres?sslmode=require"
    
    try:
        return psycopg2.connect(DB_URI, connect_timeout=10)
    except Exception as e:
        st.error(f"Error de conexión real: {e}")
        return None

st.title("🍺 Horario Desastre")

user = st.selectbox("¿Quién eres?", ["Selecciona...", "Alex", "Janira", "Iria"])

if user != "Selecciona...":
    conn = conectar_db()
    cur = conn.cursor()
    
    if user == "Alex":
        st.subheader("Panel de Consulta (Lectura)")
        st.info("Alex, aquí verás el resumen de horas.")
        # Aquí se mostrarán las tablas automáticamente
    else:
        st.subheader(f"Hola {user}")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📝 Fichar", use_container_width=True):
                st.session_state.accion = "fichar"
        with col2:
            if st.button("🏖 Vacaciones", use_container_width=True):
                st.session_state.accion = "vacas"
    

    conn.close()

