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

# --- COLORES REFINADOS ---
COLOR_FONDO_BASE = "#A2D9CE"   # Verde menta oscuro
COLOR_ALEX = "#FADBD8"         # Rojo pastel
COLOR_JANI = "#FCF3CF"         # Amarillo mostaza pastel
COLOR_IRIA = "#EBDEF0"         # Morado pastel

# --- ESTILOS CSS (Botones grandes y visibles) ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: {COLOR_FONDO_BASE}; }}
    
    /* Botones de inicio: Gigantes y centrados */
    .big-button button {{
        height: 100px !important;
        font-size: 25px !important;
        margin-bottom: 20px !important;
        border: 3px solid #5D6D7E !important;
    }}

    /* Estilo para TODOS los botones (incluidos formularios) */
    .stButton>button, div[data-testid="stFormSubmitButton"]>button {{
        color: black !important;
        background-color: white !important;
        border: 2px solid #5D6D7E !important;
        border-radius: 15px;
        font-weight: bold !important;
        width: 100%;
        opacity: 1 !important;
    }}
    
    .dia-caja {{
        border: 1px solid #7FB3D5;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        min-height: 95px;
        background-color: white;
        color: black;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- NAVEGACIÓN ---
if 'page' not in st.session_state: st.session_state.page = 'inicio'
if 'm' not in st.session_state: st.session_state.m = datetime.now().month
if 'a' not in st.session_state: st.session_state.a = datetime.now().year

# --- PANTALLA 1: INICIO ---
if st.session_state.page == 'inicio':
    st.markdown("<h1 style='text-align:center; font-size: 60px; padding-bottom: 40px;'>🍺 HORARIO DESASTRE</h1>", unsafe_allow_html=True)
    
    # Usamos columnas para centrar los botones grandes
    _, col_centro, _ = st.columns([0.5, 2, 0.5])
    
    with col_centro:
        # Botón ALEX
        st.markdown(f'<div class="big-button">', unsafe_allow_html=True)
        st.markdown(f'<style>div[row-id="alx"] button {{background-color: {COLOR_ALEX} !important;}}</style>', unsafe_allow_html=True)
        if st.button("PERFIL ALEX", key="alx", use_container_width=True): 
            st.session_state.page = 'menu_alex'; st.rerun()
        
        # Botón JANIRA
        st.markdown(f'<style>div[row-id="jan"] button {{background-color: {COLOR_JANI} !important;}}</style>', unsafe_allow_html=True)
        if st.button("PERFIL JANI", key="jan", use_container_width=True):
            st.session_state.page = 'calendario'; st.session_state.user = 'Janira'; st.session_state.emp_id = 2; st.rerun()
        
        # Botón IRIA
        st.markdown(f'<style>div[row-id="iri"] button {{background-color: {COLOR_IRIA} !important;}}</style>', unsafe_allow_html=True)
        if st.button("PERFIL IRIA", key="iri", use_container_width=True):
            st.session_state.page = 'calendario'; st.session_state.user = 'Iria'; st.session_state.emp_id = 3; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- PANTALLA 2: MENU ALEX ---
elif st.session_state.page == 'menu_alex':
    st.markdown(f"<style>.stApp {{ background-color: {COLOR_ALEX}; }}</style>", unsafe_allow_html=True)
    if st.button("◀ VOLVER AL INICIO"): st.session_state.page = 'inicio'; st.rerun()
    st.title("⚙️ Panel de Gestión - Alex")
    
    t1, t2 = st.tabs(["📅 Horarios Base", "🌟 Días Estrella"])
    
    with t1:
        with st.form("f_base"):
            e = st.selectbox("Empleado", [2, 3], format_func=lambda x: "Janira" if x==2 else "Iria")
            d = st.selectbox("Día", range(7), format_func=lambda x: ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"][x])
            h = st.number_input("Contrato (Horas)", value=5.0, step=0.5)
            if st.form_submit_button("💾 Guardar o Modificar Horario"):
                supabase.table("horarios_semanales").upsert({"empleado_id": e, "dia_semana": d, "hora_inicio": str(h)}).execute()
                st.success(f"¡Hecho! Horario base guardado.")

    with t2:
        with st.form("f_esp"):
            e_e = st.selectbox("Empleado", [2, 3], format_func=lambda x: "Janira" if x==2 else "Iria", key="e_e")
            f_e = st.date_input("Fecha")
            h_e = st.number_input("Horas Especiales", value=8.0)
            if st.form_submit_button("🌟 Añadir Estrella al Calendario"):
                supabase.table("dias_especiales").insert({"empleado_id": e_e, "fecha": str(f_e), "horas_contrato": h_e}).execute()
                st.success("Estrella añadida correctamente.")

    st.divider()
    if st.button("👁️ Ver Calendario JANIRA"): st.session_state.page = 'calendario'; st.session_state.user = 'Alex'; st.session_state.ver_id = 2; st.rerun()
    if st.button("👁️ Ver Calendario IRIA"): st.session_state.page = 'calendario'; st.session_state.user = 'Alex'; st.session_state.ver_id = 3; st.rerun()

# --- PANTALLA 3: CALENDARIO ---
elif st.session_state.page == 'calendario':
    es_alex = (st.session_state.user == 'Alex')
    id_t = st.session_state.ver_id if es_alex else st.session_state.emp_id
    nom = "Janira" if id_t == 2 else "Iria"
    st.markdown(f"<style>.stApp {{ background-color: {COLOR_JANI if id_t==2 else COLOR_IRIA}; }}</style>", unsafe_allow_html=True)
    
    # Controles de mes
    c1, c2, c3 = st.columns([1, 2, 1])
    if c1.button("◀ MES"):
        st.session_state.m -= 1
        if st.session_state.m < 1: st.session_state.m = 12; st.session_state.a -= 1
        st.rerun()
    if c3.button("MES ▶"):
        st.session_state.m += 1
        if st.session_state.m > 12: st.session_state.m = 1; st.session_state.a += 1
        st.rerun()
    with c2:
        st.markdown(f"<h2 style='text-align:center;'>{calendar.month_name[st.session_state.m].upper()} {st.session_state.a}</h2>", unsafe_allow_html=True)

    if st.button("🏠 INICIO"): st.session_state.page = 'inicio'; st.rerun()
    # (Aquí sigue el resto del código del calendario...)

