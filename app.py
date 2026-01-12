import streamlit as st
from supabase import create_client, Client
from datetime import datetime, timedelta
import pandas as pd

# --- CONFIGURACIÓN Y ESTILO ---
st.set_page_config(page_title="Horario Desastre", page_icon="🍺", layout="wide")

# Colores de tu paleta original aplicados a Streamlit
estilo_css = """
<style>
    .stApp { background-color: #D5F5E3; }
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; }
</style>
"""
st.markdown(estilo_css, unsafe_allow_html=True)

# --- CONEXIÓN ---
url = "https://kljizxbakvzytmaxqodw.supabase.co"
key = "sb_publishable_aV6LrJVsVo2a_129xBbNdw_TSO_7pDz"
supabase = create_client(url, key)

# --- LÓGICA DE CÁLCULO (Tu lógica original) ---
def calcular_horas(entrada, salida, contrato=8.0):
    fmt = "%H:%M"
    t1 = datetime.strptime(entrada, fmt)
    t2 = datetime.strptime(salida, fmt)
    if t2 < t1: t2 += timedelta(days=1)
    total = (t2 - t1).total_seconds() / 3600
    
    normales = min(total, contrato)
    extras = max(0, total - contrato)
    deuda = max(0, contrato - total)
    return round(normales, 2), round(extras, 2), round(deuda, 2)

# --- PANTALLA PRINCIPAL ---
st.title("🍺 HORARIO DESASTRE")

user = st.sidebar.selectbox("¿Quién eres?", ["Selecciona...", "Alex", "Janira", "Iria"])

if user == "Selecciona...":
    st.info("Por favor, selecciona tu nombre en el menú de la izquierda.")
    st.image("https://img.freepik.com/vector-premium/cerveza-dibujos-animados-divertidos_24908-41716.jpg", width=200)

else:
    # --- PANEL PARA JANIRA E IRIA ---
    if user in ["Janira", "Iria"]:
        st.subheader(f"Hola {user}")
        
        col1, col2 = st.columns(2)
        with col1:
            fecha = st.date_input("Fecha", datetime.now())
            h_ent = st.time_input("Entrada", datetime.strptime("22:00", "%H:%M"))
        with col2:
            h_sal = st.time_input("Salida", datetime.strptime("03:00", "%H:%M"))
            contrato = st.number_input("Horas Contrato", value=5.0)

        tipo = st.radio("Tipo de día", ["Trabajo", "Vacaciones"], horizontal=True)

        if st.button("💾 GUARDAR FICHAJE"):
            ent_str = h_ent.strftime("%H:%M")
            sal_str = h_sal.strftime("%H:%M")
            
            if tipo == "Vacaciones":
                norm, ext, deu = contrato, 0.0, 0.0
                ent_str, sal_str = "00:00", "00:00"
            else:
                norm, ext, deu = calcular_horas(ent_str, sal_str, contrato)

            datos = {
                "nombre": user,
                "fecha": str(fecha),
                "entrada": ent_str,
                "salida": sal_str,
                "horas_normales": norm,
                "horas_extras": ext,
                "deuda": deu,
                "tipo": tipo.lower()
            }
            
            supabase.table("fichajes").insert(datos).execute()
            st.success("✅ ¡Fichaje guardado!")
            st.balloons()

    # --- PANEL PARA ALEX (EL JEFE) ---
    if user == "Alex":
        st.subheader("📊 Panel de Control (Alex)")
        
        # Filtro de empleado
        emp_ver = st.selectbox("Ver horario de:", ["Janira", "Iria"])
        
        # Consultar datos
        res = supabase.table("fichajes").filter("nombre", "eq", emp_ver).execute()
        
        if res.data:
            df = pd.DataFrame(res.data)
            
            # Cálculos totales
            total_n = df["horas_normales"].sum()
            total_e = df["horas_extras"].sum()
            total_d = df["deuda"].sum()
            netas = total_e - total_d

            # Tarjetas de resumen
            c1, c2, c3 = st.columns(3)
            c1.metric("Horas Normales", f"{total_n}h")
            c2.metric("Extras Totales", f"{total_e}h")
            c3.metric("Balance (Extras-Deuda)", f"{netas}h")

            st.dataframe(df[["fecha", "entrada", "salida", "horas_normales", "horas_extras", "deuda", "tipo"]])
        else:
            st.warning("Aún no hay datos para mostrar.")
