import streamlit as st
from supabase import create_client, Client

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Bar App", page_icon="🍺")

# SUSTITUYE ESTO CON TUS DATOS DE SETTINGS > API
url = https://kljizxbakvzytmaxqodw.supabase.co
key = sb_publishable_aV6LrJVsVo2a_129xBbNdw_TSO_7pDz

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
        # Con esta herramienta, la conexión es instantánea
        st.success(f"✅ ¡CONECTADO POR API! Hola {user}")
        
        # Ejemplo: Consultar empleados para probar que lee datos
        try:
            response = supabase.table("empleados").select("*").execute()
            st.write("Conexión real establecida con éxito.")
        except Exception as e:
            st.warning("Conexión OK, pero la tabla 'empleados' no se lee. Revisa si activaste RLS.")
else:
    st.error("No se pudo configurar el cliente de Supabase.")

