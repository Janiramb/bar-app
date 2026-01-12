import streamlit as st
import psycopg2
from datetime import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Horario Desastre", page_icon="🍺")

def conectar_db():
    # Usamos la IP directa para que tu PC no se pierda
    # Asegúrate de que la contraseña Tinacasa1999. sea la correcta
    DB_URI = "host=15.237.253.218 port=5432 dbname=postgres user=postgres password=Tinacasa1999. sslmode=require"
    
    try:
        # Aumentamos el tiempo de espera a 20 segundos
        conn = psycopg2.connect(DB_URI, connect_timeout=20)
        return conn
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo conectar: {e}")
        return None

st.title("🍺 Horario Desastre")

user = st.selectbox("¿Quién eres?", ["Selecciona...", "Alex", "Janira", "Iria"])

if user != "Selecciona...":
    # Intentamos conectar solo cuando se elige un usuario
    conn = conectar_db()
    
    if conn:
        st.success(f"✅ ¡Conectado con éxito, {user}!")
        cur = conn.cursor()
        
        # Aquí cargaremos tus botones en el siguiente paso
        if user == "Alex":
            st.info("Modo consulta activado.")
        else:
            st.write(f"### Panel de {user}")
            if st.button("📝 Fichar ahora"):
                st.write("Abriendo registro...")
        
        cur.close()
        conn.close()
    else:
        st.warning("⚠️ El servidor está tardando mucho. Pulsa el botón para reintentar.")
        if st.button("🔄 Reintentar Conexión"):
            st.rerun()

