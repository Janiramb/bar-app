import streamlit as st
import psycopg2
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Bar App", page_icon="🍺")

def conectar_db():
    # Intentamos la conexión con el formato que Supabase exige para AWS
    # Fíjate que el host ha cambiado ligeramente para asegurar que llegue al sitio correcto
    try:
        conn = psycopg2.connect(
            host="aws-0-eu-central-1.pooler.supabase.com",
            port="6543",
            database="postgres",
            user="postgres.kljizxbakvzytmaxqodw", 
            password="Tinacasa1999.",
            sslmode="require",
            connect_timeout=30,
            options="-c target_session_attrs=read-write" # Esto ayuda a estabilizar la sesión
        )
        return conn
    except Exception as e:
        # Si el anterior falla, intentamos la dirección directa sin pooler
        try:
            return psycopg2.connect(
                host="db.kljizxbakvzytmaxqodw.supabase.co",
                port="5432",
                database="postgres",
                user="postgres",
                password="Tinacasa1999.",
                sslmode="require",
                connect_timeout=20
            )
        except:
            st.error(f"❌ Error de red persistente: {e}")
            return None

st.title("🍺 Horario Desastre")

user = st.selectbox("¿Quién eres?", ["Selecciona...", "Alex", "Janira", "Iria"])

if user != "Selecciona...":
    with st.spinner('Conectando con la base de datos...'):
        conn = conectar_db()
    
    if conn:
        st.success(f"✅ ¡POR FIN! Conexión establecida. Hola {user}")
        conn.close()
    else:
        st.warning("⚠️ El servidor de Supabase rechaza la identificación.")
        st.info("Revisa en Supabase: Settings > Database > Connection Info y confirma el 'User'.")
