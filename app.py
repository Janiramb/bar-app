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

# --- PALETA DE COLORES PERSONALIZADA ---
COLOR_FONDO_PASTEL = "#D5F5E3" # Verde Pastel Base
COLOR_ALEX = "#C0392B"         # Rojo
COLOR_JANI = "#E1AD01"         # Amarillo Mostaza
COLOR_IRIA = "#8E44AD"         # Morado
COLOR_FICHAJE = "#2ECC71"      # Verde para días trabajados
COLOR_ESTRELLA = "#F39C12"     # Naranja para días especiales

# --- ESTILOS CSS ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: {COLOR_FONDO_PASTEL}; }}
    .stButton>button {{
        color: black !important;
        background-color: white;
        border: 2px solid #555 !important;
        font-weight: bold !important;
        border-radius: 10px;
    }}
    .dia-caja {{
        border: 1px solid #999;
        padding: 5px;
        border-radius: 8px;
        text-align: center;
        min-height: 100px;
        color: black;
        background-color: white;
    }}
    /* Colores de cabecera por perfil */
    .header-alex {{ color: {COLOR_ALEX}; text-align: center; font-weight: bold; }}
    .header-jani {{ color: {COLOR_JANI}; text-align: center; font-weight: bold; }}
    .header-iria {{ color: {COLOR_IRIA}; text-align: center; font-weight: bold; }}
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES ---
def calcular_duracion(ent, sal):
    fmt = "%H:%M"
    try:
        t1, t2 = datetime.strptime(ent, fmt), datetime.strptime(sal, fmt)
        if t2 < t1: t2 += timedelta(days=1)
        return round((t2 - t1).total_seconds() / 3600, 2)
    except: return 0.0

# --- SESIÓN ---
if 'page' not in st.session_state: st.session_state.page = 'inicio'
if 'mes_ver' not in st.session_state: st.session_state.mes_ver = datetime.now().month
if 'anio_ver' not in st.session_state: st.session_state.anio_ver = datetime.now().year

# --- PANTALLA 1: INICIO ---
if st.session_state.page == 'inicio':
    st.markdown("<h1 style='text-align:center; color:#555;'>🍺 HORARIO DESASTRE 🍺</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.write("##")
        st.markdown(f'<style>div[row-id="alx"] button {{border-color: {COLOR_ALEX} !important; color: {COLOR_ALEX} !important;}}</style>', unsafe_allow_html=True)
        if st.button("🧔 ALEX", key="alx", use_container_width=True): 
            st.session_state.page = 'menu_alex'; st.rerun()
        
        st.write("")
        st.markdown(f'<style>div[row-id="jan"] button {{background-color: {COLOR_JANI} !important; color: white !important;}}</style>', unsafe_allow_html=True)
        if st.button("👩‍🦰 JANIRA", key="jan", use_container_width=True):
            st.session_state.page = 'calendario'; st.session_state.user = 'Janira'; st.session_state.emp_id = 2; st.rerun()
        
        st.write("")
        st.markdown(f'<style>div[row-id="iri"] button {{background-color: {COLOR_IRIA} !important; color: white !important;}}</style>', unsafe_allow_html=True)
        if st.button("👩‍🦳 IRIA", key="iri", use_container_width=True):
            st.session_state.page = 'calendario'; st.session_state.user = 'Iria'; st.session_state.emp_id = 3; st.rerun()

# --- PANTALLA 2: MENU ALEX ---
elif st.session_state.page == 'menu_alex':
    st.markdown(f"<style>.stApp {{ background-color: {COLOR_ALEX}22; }}</style>", unsafe_allow_html=True)
    if st.button("◀ VOLVER"): st.session_state.page = 'inicio'; st.rerun()
    st.markdown(f"<h1 class='header-alex'>PANEL DE CONTROL - ALEX</h1>", unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("⚙️ Horarios Base")
        with st.form("form_base"):
            e_id = st.selectbox("Empleado", [2, 3], format_func=lambda x: "Janira" if x==2 else "Iria")
            h_base = st.number_input("Horas fijas contrato", value=5.0)
            if st.form_submit_button("Guardar Horario Base"):
                supabase.table("empleados").update({"rol": f"Contrato: {h_base}h"}).eq("id", e_id).execute()
                st.success("Contrato actualizado")

    with col_b:
        st.subheader("🌟 Días Especiales")
        with st.form("form_esp"):
            e_id_esp = st.selectbox("Empleado", [2, 3], format_func=lambda x: "Janira" if x==2 else "Iria", key="s2")
            f_esp = st.date_input("Fecha específica")
            h_esp = st.number_input("Horas para ese día", value=8.0)
            if st.form_submit_button("Guardar Día Especial"):
                supabase.table("dias_especiales").insert({"empleado_id": e_id_esp, "fecha": str(f_esp), "horas_contrato": h_esp}).execute()
                st.success("Día especial guardado con ★")

    st.divider()
    if st.button("Consultar JANIRA", use_container_width=True): 
        st.session_state.page = 'calendario'; st.session_state.user = 'Alex'; st.session_state.ver_id = 2; st.rerun()
    if st.button("Consultar IRIA", use_container_width=True): 
        st.session_state.page = 'calendario'; st.session_state.user = 'Alex'; st.session_state.ver_id = 3; st.rerun()

# --- PANTALLA 3: CALENDARIO ---
elif st.session_state.page == 'calendario':
    es_alex = (st.session_state.user == 'Alex')
    id_trab = st.session_state.ver_id if es_alex else st.session_state.emp_id
    nombre_v = "Janira" if id_trab == 2 else "Iria"
    clase_css = "header-jani" if id_trab == 2 else "header-iria"
    
    # Color de fondo suave basado en el perfil
    bg_perfil = COLOR_JANI if id_trab == 2 else COLOR_IRIA
    st.markdown(f"<style>.stApp {{ background-color: {bg_perfil}15; }}</style>", unsafe_allow_html=True)

    c_at, c_me, c_ad = st.columns([1, 2, 1])
    if c_at.button("◀"):
        st.session_state.mes_ver = 12 if st.session_state.mes_ver == 1 else st.session_state.mes_ver - 1
        st.rerun()
    if c_ad.button("▶"):
        st.session_state.mes_ver = 1 if st.session_state.mes_ver == 12 else st.session_state.mes_ver + 1
        st.rerun()
    with c_me:
        st.markdown(f"<h2 class='{clase_css}'>{calendar.month_name[st.session_state.mes_ver].upper()} - {nombre_v.upper()}</h2>", unsafe_allow_html=True)

    if st.button("🏠 INICIO"): st.session_state.page = 'inicio'; st.rerun()

    # Cargar Datos
    res_f = supabase.table("fichajes").select("*").eq("empleado_id", id_trab).execute()
    df_f = pd.DataFrame(res_f.data) if res_f.data else pd.DataFrame()
    res_e = supabase.table("dias_especiales").select("*").eq("empleado_id", id_trab).execute()
    df_e = pd.DataFrame(res_e.data) if res_e.data else pd.DataFrame()

    cal = calendar.monthcalendar(st.session_state.anio_ver, st.session_state.mes_ver)
    cols_h = st.columns(7)
    for i, d in enumerate(["LUN", "MAR", "MIE", "JUE", "VIE", "SAB", "DOM"]): cols_h[i].write(f"**{d}**")

    for semana in cal:
        cols = st.columns(7)
        for i, dia in enumerate(semana):
            if dia == 0: continue
            f_str = f"{st.session_state.anio_ver}-{st.session_state.mes_ver:02d}-{dia:02d}"
            f = df_f[df_f['fecha_dia'] == f_str].iloc[0] if not df_f.empty and not df_f[df_f['fecha_dia'] == f_str].empty else None
            esp = df_e[df_e['fecha'] == f_str].iloc[0] if not df_e.empty and not df_e[df_e['fecha'] == f_str].empty else None
            
            with cols[i]:
                c_bg = "white"
                star = "★" if esp is not None else ""
                txt = f"<b>{dia}{star}</b>"
                if f is not None:
                    c_bg = COLOR_FICHAJE
                    txt += f"<br><small>{f['hora_entrada']}-{f['hora_salida']}</small><br><b style='font-size:10px;'>{f['horas_normales']}N/{f['horas_extras']}E</b>"
                elif esp is not None:
                    c_bg = COLOR_ESTRELLA + "44" # Estrellado suave
                
                st.markdown(f"<div class='dia-caja' style='background-color:{c_bg};'>{txt}</div>", unsafe_allow_html=True)
                if not es_alex:
                    if st.button("📝", key=f"b_{dia}"):
                        st.session_state.fichar_dia = (f_str, esp['horas_contrato'] if esp is not None else 5.0)
                        st.rerun()
