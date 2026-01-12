import streamlit as st
from supabase import create_client, Client
from datetime import datetime, timedelta
import pandas as pd

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Horario Desastre", page_icon="🍺")

# Estilo visual rápido
st.markdown("""
    <style>
    .stApp { background-color: #D5F5E3; }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXIÓN ---
url = "https://kljizxbakvzytmaxqodw.supabase.co"
key = "sb_publishable_aV6LrJVsVo2a_129xBbNdw_TSO_7pDz"
supabase = create_client(url, key)

# Diccionario para convertir nombres a IDs (según tu código original)
IDS = {"Alex": 1, "Janira": 2, "Iria": 3}

# --- LÓGICA DE CÁLCULO ---
def calcular_horas(entrada, salida, contrato=5.0):
    fmt = "%H:%M"
    try:
        t1 = datetime.strptime(entrada, fmt)
        t2 = datetime.strptime(salida, fmt)
        if t2 < t1: t2 += timedelta(days=1)
        total = (t2 - t1).total_seconds() / 3600
        
        normales = min(total, contrato)
        extras = max(0, total - contrato)
        return round(normales, 2), round(extras, 2)
    except:
        return 0.0, 0.0

st.title("🍺 HORARIO DESASTRE")

user = st.selectbox("¿Quién eres?", ["Selecciona...", "Alex", "Janira", "Iria"])

if user != "Selecciona...":
    id_actual = IDS[user]
    
    if user in ["Janira", "Iria"]:
        st.subheader(f"Panel de {user}")
        
        with st.form("form_fichaje"):
            fecha = st.date_input("Fecha del turno", datetime.now())
            col1, col2 = st.columns(2)
            with col1:
                h_ent = st.time_input("Entrada", datetime.strptime("22:00", "%H:%M"))
            with col2:
                h_sal = st.time_input("Salida", datetime.strptime("03:00", "%H:%M"))
            
            h_cont = st.number_input("Horas de contrato hoy", value=5.0)
            tipo_dia = st.selectbox("Tipo", ["trabajo", "vacaciones"])
            
            enviar = st.form_submit_button("💾 GUARDAR FICHAJE")
            
            if enviar:
                ent_str = h_ent.strftime("%H:%M")
                sal_str = h_sal.strftime("%H:%M")
                
                if tipo_dia == "vacaciones":
                    norm, extra = h_cont, 0.0
                    ent_str, sal_str = "00:00", "00:00"
                else:
                    norm, extra = calcular_horas(ent_str, sal_str, h_cont)

                # USANDO TUS COLUMNAS EXACTAS
                datos = {
                    "empleado_id": id_actual,
                    "fecha_dia": str(fecha),
                    "hora_entrada": ent_str,
                    "hora_salida": sal_str,
                    "horas_normales": norm,
                    "horas_extras": extra,
                    "tipo": tipo_dia
                }
                
                try:
                    supabase.table("fichajes").insert(datos).execute()
                    st.success(f"✅ ¡Guardado! Horas: {norm}n + {extra}e")
                    st.balloons()
                except Exception as e:
                    st.error(f"Error al guardar: {e}")

    if user == "Alex":
        st.subheader("📊 Resumen para Alex")
        emp_ver = st.radio("Ver empleado:", [2, 3], format_func=lambda x: "Janira" if x==2 else "Iria")
        
        res = supabase.table("fichajes").select("*").eq("empleado_id", emp_ver).execute()
        
        if res.data:
            df = pd.DataFrame(res.data)
            st.write(f"Total Horas Normales: {df['horas_normales'].sum()}")
            st.write(f"Total Horas Extras: {df['horas_extras'].sum()}")
            st.dataframe(df[["fecha_dia", "hora_entrada", "hora_salida", "horas_normales", "horas_extras", "tipo"]])
        else:
            st.info("No hay fichajes registrados para este empleado.")
