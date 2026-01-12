import streamlit as st
from supabase import create_client, Client
from datetime import datetime, timedelta
import calendar
import pandas as pd

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Horario Desastre", page_icon="🍺", layout="wide")

# --- CONEXIÓN ---
url = "https://kljizxbakvzytmaxqodw.supabase.co"
key = "sb_publishable_aV6LrJVsVo2a_129xBbNdw_TSO_7pDz"
supabase = create_client(url, key)

# --- COLORES ---
COLOR_FONDO = "#D5F5E3"
COLOR_ALEX = "#E6B0AA"
COLOR_JANI = "#F9E79F"
COLOR_IRIA = "#D7BDE2"

# --- ESTILOS CSS LIMPIOS ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: {COLOR_FONDO}; }}
    .stButton>button {{
        color: black !important;
        background-color: white;
        border: 2px solid #555 !important;
        font-weight: bold !important;
        height: 60px;
    }}
    .dia-caja {{
        border: 1px solid #ccc;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        min-height: 80px;
        background-color: white;
        color: black;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- NAVEGACIÓN ---
if 'page' not in st.session_state: st.session_state.page = 'inicio'

# --- PANTALLA 1: INICIO ---
if st.session_state.page == 'inicio':
    st.markdown("<h1 style='text-align:center; color:#333;'>🍺 HORARIO DESASTRE 🍺</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.write("##")
        if st.button("🧔 ALEX (Jefe)", use_container_width=True):
            st.session_state.page = 'menu_alex'; st.rerun()
        
        st.write("")
        if st.button("👩‍🦰 JANIRA", use_container_width=True):
            st.session_state.page = 'calendario'; st.session_state.user = 'Janira'; st.session_state.emp_id = 2; st.rerun()
        
        st.write("")
        if st.button("👩‍🦳 IRIA", use_container_width=True):
            st.session_state.page = 'calendario'; st.session_state.user = 'Iria'; st.session_state.emp_id = 3; st.rerun()

# --- PANTALLA 2: MENU ALEX ---
elif st.session_state.page == 'menu_alex':
    st.markdown("<style>.stApp { background-color: #F2D7D5; }</style>", unsafe_allow_html=True)
    if st.button("◀ VOLVER AL INICIO"): st.session_state.page = 'inicio'; st.rerun()
    
    st.title("Panel de Control - Alex")
    
    tab1, tab2 = st.tabs(["📊 Consultar Horarios", "⚙️ Configurar Días Especiales"])
    
    with tab1:
        st.write("Selecciona a quién quieres consultar:")
        if st.button("Consultar a JANIRA"):
            st.session_state.page = 'calendario'; st.session_state.user = 'Alex'; st.session_state.ver_id = 2; st.rerun()
        if st.button("Consultar a IRIA"):
            st.session_state.page = 'calendario'; st.session_state.user = 'Alex'; st.session_state.ver_id = 3; st.rerun()
            
    with tab2:
        st.write("Añadir horas de contrato o días especiales:")
        with st.form("form_especial"):
            e_id = st.selectbox("Empleado", [2, 3], format_func=lambda x: "Janira" if x==2 else "Iria")
            f_esp = st.date_input("Fecha")
            h_esp = st.number_input("Horas Contrato", value=5.0)
            if st.form_submit_button("Guardar Configuración"):
                supabase.table("dias_especiales").insert({"empleado_id": e_id, "fecha": str(f_esp), "horas_contrato": h_esp}).execute()
                st.success("Día configurado con éxito")

# --- PANTALLA 3: CALENDARIO ---
elif st.session_state.page == 'calendario':
    user_es_alex = (st.session_state.user == 'Alex')
    id_trabajador = st.session_state.ver_id if user_es_alex else st.session_state.emp_id
    nombre_visto = "Janira" if id_trabajador == 2 else "Iria"
    
    if st.button("◀ VOLVER"):
        st.session_state.page = 'menu_alex' if user_es_alex else 'inicio'; st.rerun()
    
    st.title(f"Calendario de {nombre_visto}")
    if user_es_alex: st.warning("Modo Lectura: Solo Alex puede ver, no modificar.")

    # Cargar Fichajes
    res = supabase.table("fichajes").select("*").eq("empleado_id", id_trabajador).execute()
    df_f = pd.DataFrame(res.data) if res.data else pd.DataFrame()

    hoy = datetime.now()
    cal = calendar.monthcalendar(hoy.year, hoy.month)
    
    # Grid de Calendario
    for semana in cal:
        cols = st.columns(7)
        for i, dia in enumerate(semana):
            if dia == 0: continue
            fecha_s = f"{hoy.year}-{hoy.month:02d}-{dia:02d}"
            
            # Buscar si hay fichaje
            f = None
            if not df_f.empty:
                m = df_f[df_f['fecha_dia'] == fecha_s]
                if not m.empty: f = m.iloc[0]
            
            with cols[i]:
                color = "white"
                txt = f"<b>{dia}</b>"
                if f is not None:
                    color = "#ABEBC6" if f['tipo'] == 'trabajo' else "#AED6F1"
                    txt += f"<br><small>{f['hora_entrada']}-{f['hora_salida']}</small>"
                
                st.markdown(f"<div class='dia-caja' style='background-color:{color};'>{txt}</div>", unsafe_allow_html=True)
                
                # SOLO Janira/Iria ven el botón de editar
                if not user_es_alex:
                    if st.button("📝", key=f"btn_{dia}"):
                        st.session_state.fichar_dia = fecha_s
                        st.rerun()

    # Formulario de Fichaje (Solo para ellas)
    if 'fichar_dia' in st.session_state and not user_es_alex:
        with st.expander(f"Fichar día {st.session_state.fichar_dia}", expanded=True):
            h_i = st.text_input("Entrada", "22:00")
            h_o = st.text_input("Salida", "03:00")
            if st.button("Guardar Turno"):
                supabase.table("fichajes").insert({
                    "empleado_id": id_trabajador, "fecha_dia": st.session_state.fichar_dia,
                    "hora_entrada": h_i, "hora_salida": h_o, "horas_normales": 5.0, "horas_extras": 0.0, "tipo": "trabajo"
                }).execute()
                del st.session_state.fichar_dia; st.rerun()
            if st.button("🗑️ Eliminar"):
                supabase.table("fichajes").delete().eq("empleado_id", id_trabajador).eq("fecha_dia", st.session_state.fichar_dia).execute()
                del st.session_state.fichar_dia; st.rerun()
