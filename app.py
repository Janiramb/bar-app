import streamlit as st
import psycopg2
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Bar App", page_icon="🍺")

def conectar_db():
    # Hemos cambiado el nombre por la IP directa 15.237.253.218
    # Usamos el puerto 5432 y añadimos sslmode=require
    DB_URI = "postgresql://postgres:Tinacasa1999.@15.237.253.218:5432/postgres?sslmode=require"
    
    try:
        # Añadimos un tiempo de espera para que no se quede colgado
        return psycopg2.connect(DB_URI, connect_timeout=15)
    except Exception as e:
        st.error(f"⚠️ Error de conexión a la base de datos: {e}")
        return None

st.title("🍺 Horario Desastre")

user = st.selectbox("¿Quién eres?", ["Selecciona...", "Alex", "Janira", "Iria"])

if user != "Selecciona...":
    conn = conectar_db()
    
    # Solo intentamos usar la base de datos si la conexión funcionó
    if conn is not None:
        cur = conn.cursor()
        
        if user == "Alex":
            st.subheader("Panel de Consulta (Lectura)")
            st.info("Alex, aquí verás el resumen de horas.")
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
    else:
        st.warning("No se pudo establecer la conexión. Por favor, recarga la página en unos segundos.")

