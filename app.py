import streamlit as st
import psycopg2
from datetime import datetime

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Horario Desastre", page_icon="🍺")

# --- 2. FUNCIÓN DE CONEXIÓN ROBUSTA ---
def conectar_db():
    # Usamos el puerto 6543 y el modo 'session' que es el más estable
    # También forzamos el uso de IPv4 para evitar el error de los logs anteriores
    DB_URI = "postgresql://postgres:Tinacasa1999.@db.kljizxbakvzytmaxqodw.supabase.co:6543/postgres?sslmode=require&connect_timeout=20"
    try:
        return psycopg2.connect(DB_URI)
    except Exception as e:
        # Si falla, intentamos una vez más con la IP directa
        try:
            DB_URI_IP = "postgresql://postgres:Tinacasa1999.@15.237.253.218:6543/postgres?sslmode=require&connect_timeout=20"
            return psycopg2.connect(DB_URI_IP)
        except:
            st.error(f"⚠️ Error crítico de conexión: {e}")
            return None

# --- 3. DISEÑO ---
st.markdown("<h1 style='text-align: center;'>🍺 Horario Desastre</h1>", unsafe_allow_html=True)

user = st.selectbox("¿Quién eres?", ["Selecciona...", "Alex", "Janira", "Iria"])

if user != "Selecciona...":
    conn = conectar_db()
    
    if conn:
        st.success(f"✅ Conectado como {user}")
        cur = conn.cursor()
        
        if user == "Alex":
            st.subheader("📋 Panel de Alex")
            st.info("Resumen de horas disponible pronto.")
        else:
            st.subheader(f"👋 Hola {user}")
            # Botones de acción
            if st.button("📝 Registrar Turno", use_container_width=True):
                st.write("Formulario de fichaje abierto...")
                
        cur.close()
        conn.close()
    else:
        st.warning("⏱️ El servidor tarda en responder. Pulsa el botón de abajo para reintentar.")
        if st.button("Reintentar conexión"):
            st.rerun()
