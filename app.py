import streamlit as st
from supabase import create_client, Client
from datetime import datetime, timedelta
import calendar

# --- CONFIGURACIÓN VISUAL (Tus colores exactos) ---
st.set_page_config(page_title="Horario Desastre", page_icon="🍺", layout="centered")

COLOR_FONDO_GENERAL = "#D5F5E3" 
COLOR_ALEX_BG = "#F2D7D5"      
COLOR_JANI_BG = "#FEF9E7"      
COLOR_IRIA_BG = "#F4ECF7"      
COLOR_ALEX_TXT = "#C0392B"
COLOR_JANI_TXT = "#D4AC0D"
COLOR_IRIA_TXT = "#8E44AD"
COLOR_BTN_ELIMINAR = "#E74C3C"

# Aplicar el fondo general
st.markdown(f"""
    <style>
    .stApp {{ background-color: {COLOR_FONDO_GENERAL}; }}
    .stButton>button {{ border-radius: 10px; height: 3em; font-weight: bold; font-size: 18px !important; }}
    .calendar-day {{ border: 1px solid #eee; padding: 10px; border-radius: 5px; background-color: white; min-height: 80px; }}
    </style>
    """, unsafe_allow_html=True)

# --- CONEXIÓN ---
url = "https://kljizxbakvzytmaxqodw.supabase.co"
key = "sb_publishable_aV6LrJVsVo2a_129xBbNdw_TSO_7pDz"
supabase = create_client(url, key)

IDS = {"Alex": 1, "Janira": 2, "Iria": 3}

# --- FUNCIONES DE CÁLCULO ---
def calcular_horas(entrada, salida, contrato=5.0):
    if entrada == "00:00" and salida == "00:00": return 0.0, 0.0
    fmt = "%H:%M"
    t1, t2 = datetime.strptime(entrada, fmt), datetime.strptime(salida, fmt)
    if t2 < t1: t2 += timedelta(days=1)
    total = (t2 - t1).total_seconds() / 3600
    norm = min(total, contrato)
    extra = max(0, total - contrato)
    return round(norm, 2), round(extra, 2)

# --- NAVEGACIÓN ---
if 'page' not in st.session_state:
    st.session_state.page = 'inicio'
if 'emp_id' not in st.session_state:
    st.session_state.emp_id = None

def ir_a(pagina, emp_id=None):
    st.session_state.page = pagina
    st.session_state.emp_id = emp_id
    st.rerun()

# --- 1. PANTALLA INICIO ---
if st.session_state.page == 'inicio':
    st.markdown("<h1 style='text-align: center; color: #555; font-size: 50px;'>🍺 HORARIO DESASTRE 🍺</h1>", unsafe_allow_html=True)
    st.write("##")
    
    if st.button("ALEX", use_container_width=True): ir_a('menu_alex', 1)
    st.write("#")
    if st.button("JANIRA", use_container_width=True): ir_a('calendario', 2)
    st.write("#")
    if st.button("IRIA", use_container_width=True): ir_a('calendario', 3)

# --- 2. MENU ALEX ---
elif st.session_state.page == 'menu_alex':
    st.markdown(f"<style>.stApp {{ background-color: {COLOR_ALEX_BG}; }}</style>", unsafe_allow_html=True)
    if st.button("< VOLVER"): ir_a('inicio')
    st.markdown(f"<h1 style='text-align: center; color: {COLOR_ALEX_TXT};'>PANEL DE CONSULTA</h1>", unsafe_allow_html=True)
    
    st.write("##")
    if st.button("HORARIO JANIRA", use_container_width=True): ir_a('calendario', 2)
    if st.button("HORARIO IRIA", use_container_width=True): ir_a('calendario', 3)

# --- 3. CALENDARIO ---
elif st.session_state.page == 'calendario':
    emp_id = st.session_state.emp_id
    nombre = [k for k, v in IDS.items() if v == emp_id][0]
    
    # Colores según el empleado
    bg = COLOR_JANI_BG if emp_id == 2 else COLOR_IRIA_BG
    txt_col = COLOR_JANI_TXT if emp_id == 2 else COLOR_IRIA_TXT
    st.markdown(f"<style>.stApp {{ background-color: {bg}; }}</style>", unsafe_allow_html=True)
    
    col_v, col_n = st.columns([1, 4])
    with col_v:
        if st.button("< VOLVER"): ir_a('menu_alex' if st.session_state.emp_id == 1 else 'inicio')
    
    st.markdown(f"<h1 style='text-align: center; color: {txt_col};'>HOLA {nombre.upper()}</h1>", unsafe_allow_html=True)

    # Selector de Mes
    hoy = datetime.now()
    mes = st.selectbox("Selecciona Mes", range(1, 13), index=hoy.month-1)
    anio = hoy.year

    # Cargar datos de Supabase
    res = supabase.table("fichajes").select("*").eq("empleado_id", emp_id).execute()
    fichajes_dict = {f['fecha_dia']: f for f in res.data} if res.data else {}

    # Dibujar Calendario
    cal = calendar.monthcalendar(anio, mes)
    for semana in cal:
        cols = st.columns(7)
        for i, dia in enumerate(semana):
            if dia == 0:
                cols[i].write("")
            else:
                fecha_str = f"{anio}-{mes:02d}-{dia:02d}"
                with cols[i]:
                    # Celda de día
                    if fecha_str in fichajes_dict:
                        f = fichajes_dict[fecha_str]
                        st.markdown(f"<div class='calendar-day' style='background-color:#ABEBC6;'><b>{dia}</b><br><small>{f['hora_entrada']}-{f['hora_salida']}</small></div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='calendar-day'><b>{dia}</b></div>", unsafe_allow_html=True)
                    
                    # Botón para gestionar el día
                    if st.button("⚙️", key=f"btn_{dia}"):
                        st.session_state.dia_gestion = fecha_str
                        st.rerun()

    # --- POPUP / GESTIÓN DE DÍA ---
    if 'dia_gestion' in st.session_state:
        st.divider()
        st.subheader(f"Gestionar día: {st.session_state.dia_gestion}")
        
        # Si ya existe fichaje, mostrar opción de ELIMINAR
        if st.session_state.dia_gestion in fichajes_dict:
            f = fichajes_dict[st.session_state.dia_gestion]
            st.info(f"Turno actual: {f['hora_entrada']} a {f['hora_salida']} ({f['horas_normales']}h N)")
            if st.button("🗑️ ELIMINAR FICHAJE", type="primary"):
                supabase.table("fichajes").delete().eq("empleado_id", emp_id).eq("fecha_dia", st.session_state.dia_gestion).execute()
                del st.session_state.dia_gestion
                st.rerun()
        else:
            # Formulario para nuevo fichaje
            with st.form("nuevo_fichaje"):
                h_e = st.selectbox("H. Entrada", [f"{i:02d}:00" for i in range(24)], index=22)
                h_s = st.selectbox("H. Salida", [f"{i:02d}:00" for i in range(24)], index=3)
                contrato = st.number_input("Contrato (h)", value=5.0)
                if st.form_submit_button("GUARDAR"):
                    n, e = calcular_horas(h_e, h_s, contrato)
                    datos = {
                        "empleado_id": emp_id,
                        "fecha_dia": st.session_state.dia_gestion,
                        "hora_entrada": h_e,
                        "hora_salida": h_s,
                        "horas_normales": n,
                        "horas_extras": e,
                        "tipo": "trabajo"
                    }
                    supabase.table("fichajes").insert(datos).execute()
                    del st.session_state.dia_gestion
                    st.rerun()
        
        if st.button("Cerrar gestión"):
            del st.session_state.dia_gestion
            st.rerun()
