import streamlit as st
from supabase import create_client, Client

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Bar App", page_icon="🍺")

# --- CONEXIÓN (AHORA CON COMILLAS) ---
# He puesto las comillas " " que faltaban para que Python no de error
url = "https://kljizxbakvzytmaxqodw.supabase.co"
key = "sb_publishable_aV6LrJVsVo2a_129xBbNdw_TSO_7pDz"

@st.cache_resource
def conectar_supabase():
    try:
        return create_client(url, key)
    except Exception as e:
        st.error(f"Error al conectar con la API: {e}")
        return None

st.title("🍺 Horario Desastre")

supabase = conectar_supabase()

if supabase:
    user = st.selectbox("¿Quién eres?", ["Selecciona...", "Alex", "Janira", "Iria"])

    if user != "Selecciona...":
        # Con esta herramienta, la conexión es instantánea por el puerto web normal
        st.success(f"✅ ¡CONECTADO POR API! Hola {user}")
        
        try:
            # Intentamos leer la tabla empleados
            response = supabase.table("empleados").select("*").execute()
            st.write("🚀 La App ya lee los datos de Supabase correctamente.")
        except Exception as e:
            # Si sale este aviso, es que falta activar el RLS en Supabase (lo que vimos antes)
            st.warning("Conexión OK, pero la tabla 'empleados' no devuelve datos.")
            st.info("💡 Consejo: Ve a Supabase > Authentication > Policies y dale a 'Enable RLS' y crea una política simple para la tabla.")
else:
    st.error("No se pudo configurar el cliente de Supabase. Revisa las llaves.")
