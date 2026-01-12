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

# --- COLORES INTENSOS PASTEL ---
COLOR_FONDO = "#D5F5E3"
COLOR_VERDE_INTENSO = "#7DCEA0" # Verde más vivo para fichajes
COLOR_JANI = "#F4D03F"         # Amarillo más fuerte
COLOR_IRIA = "#BB8FCE"         # Lila más intenso
COLOR_ESPECIAL = "#F7DC6F"     # Dorado para días con estrella

# --- ESTILOS CSS ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: {COLOR_FONDO}; }}
    .stButton>button {{
        color: black !important;
        background-color: white;
        border: 2px solid #555 !important;
        font-weight: bold !important;
    }}
    .dia-caja {{
        border: 1px solid #999;
        padding: 5px;
        border-radius: 8px;
        text-align: center;
        min-height: 95px;
        color: black;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- UTILIDADES ---
def calcular_duracion(ent, sal):
    fmt = "%H:%M"
    try:
        t1, t2 = datetime.strptime(ent, fmt), datetime.strptime(sal, fmt)
        if t2 < t1: t2 += timedelta(days=1)
        return (t2 - t1).total_seconds() / 3600
    except: return 0.0

# --- SESSIÓN ---
if 'page' not in st.session_state: st.session_state.page = 'inicio'
if 'mes_ver' not in st.session_state: st.session_state.mes_ver = datetime.now().month
if 'anio_ver' not in st.session_state: st.session_state.anio_ver = datetime.now().year

# --- PANTALLA 1: INICIO ---
if st.session_state.page == 'inicio':
    st.markdown("<h1 style='text-align:center;'>🍺 HORARIO DESASTRE 🍺</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🧔 ALEX", use_container_width=True): 
            st.session_state.page = 'menu_alex'; st.rerun()
        st.write("")
        st.markdown(f'<style>div[row-id="j"] button {{background-color: {COLOR_JANI} !important;}}</style>', unsafe_allow_html=True)
        if st.button("👩‍🦰 JANIRA", key="j", use_container_width=True):
            st.session_state.page = 'calendario'; st.session_state.user = 'Janira'; st.session_state.emp_id = 2; st.rerun()
        st.write("")
        st.markdown(f'<style>div[row-id="i"] button {{background-color: {COLOR_IRIA} !important;}}</style>', unsafe_allow_html=True)
        if st.button("👩‍🦳 IRIA", key="i", use_container_width=True):
            st.session_state.page = 'calendario'; st.session_state.user = 'Iria'; st.session_state.emp_id = 3; st.rerun()

# --- PANTALLA 2: MENU ALEX ---
elif st.session_state.page == 'menu_alex':
    if st.button("◀ VOLVER"): st.session_state.page = 'inicio'; st.rerun()
    st.title("Panel de Control - Alex")
    tab1, tab2 = st.tabs(["📊 Consultar", "⚙️ Configurar Días/Contratos"])
    
    with tab1:
        c1, c2 = st.columns(2)
        if c1.button("Ver JANIRA"): st.session_state.page = 'calendario'; st.session_state.user = 'Alex'; st.session_state.ver_id = 2; st.rerun()
        if c2.button("Ver IRIA"): st.session_state.page = 'calendario'; st.session_state.user = 'Alex'; st.session_state.ver_id = 3; st.rerun()
    
    with tab2:
        with st.form("alex_config"):
            e_id = st.selectbox("Empleado", [2, 3], format_func=lambda x: "Janira" if x==2 else "Iria")
            f_esp = st.date_input("Fecha")
            h_base = st.number_input("Horas de contrato para este día", value=5.0)
            if st.form_submit_button("Guardar Día Especial / Base"):
                supabase.table("dias_especiales").insert({"empleado_id": e_id, "fecha": str(f_esp), "horas_contrato": h_base}).execute()
                st.success("Día especial registrado (Aparecerá con ★)")

# --- PANTALLA 3: CALENDARIO ---
elif st.session_state.page == 'calendario':
    es_alex = (st.session_state.user == 'Alex')
    id_trab = st.session_state.ver_id if es_alex else st.session_state.emp_id
    nombre_v = "Janira" if id_trab == 2 else "Iria"

    # Estilo fondo según empleado
    bg_color = COLOR_JANI if id_trab == 2 else COLOR_IRIA
    st.markdown(f"<style>.stApp {{ background-color: {bg_color}33; }}</style>", unsafe_allow_html=True)

    # Navegación Mes
    c_at, c_me, c_ad = st.columns([1, 2, 1])
    if c_at.button("◀"):
        st.session_state.mes_ver = 12 if st.session_state.mes_ver == 1 else st.session_state.mes_ver - 1
        st.rerun()
    if c_ad.button("▶"):
        st.session_state.mes_ver = 1 if st.session_state.mes_ver == 12 else st.session_state.mes_ver + 1
        st.rerun()
    with c_me:
        st.markdown(f"<h2 style='text-align:center;'>{calendar.month_name[st.session_state.mes_ver].upper()} - {nombre_v}</h2>", unsafe_allow_html=True)

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
            fecha_s = f"{st.session_state.anio_ver}-{st.session_state.mes_ver:02d}-{dia:02d}"
            
            f = df_f[df_f['fecha_dia'] == fecha_s].iloc[0] if not df_f.empty and not df_f[df_f['fecha_dia'] == fecha_s].empty else None
            esp = df_e[df_e['fecha'] == fecha_s].iloc[0] if not df_e.empty and not df_e[df_e['fecha'] == fecha_s].empty else None
            
            with cols[i]:
                c_bg = "white"
                simbolo = "★" if esp is not None else ""
                txt = f"<b>{dia}{simbolo}</b>"
                
                if f is not None:
                    c_bg = COLOR_VERDE_INTENSO if f['tipo'] == 'trabajo' else "#AED6F1"
                    txt += f"<br><small>{f['hora_entrada']}-{f['hora_salida']}</small>"
                    txt += f"<br><b style='font-size:10px;'>{f['horas_normales']}N / {f['horas_extras']}E</b>"
                elif esp is not None:
                    c_bg = COLOR_ESPECIAL
                
                st.markdown(f"<div class='dia-caja' style='background-color:{c_bg};'>{txt}</div>", unsafe_allow_html=True)
                
                if not es_alex:
                    if st.button("📝", key=f"btn_{dia}"):
                        st.session_state.fichar_dia = (fecha_s, esp['horas_contrato'] if esp is not None else 5.0)
                        st.rerun()

    # Formulario Fichaje
    if 'fichar_dia' in st.session_state and not es_alex:
        f_dia, h_base = st.session_state.fichar_dia
        with st.expander(f"Fichar día {f_dia} (Base: {h_base}h)", expanded=True):
            h_i = st.text_input("Entrada", "22:00")
            h_o = st.text_input("Salida", "03:00")
            if st.button("Guardar"):
                total = calcular_duracion(h_i, h_o)
                norm = min(total, h_base)
                extra = max(0, total - h_base)
                supabase.table("fichajes").insert({
                    "empleado_id": id_trab, "fecha_dia": f_dia, "hora_entrada": h_i,
                    "hora_salida": h_o, "horas_normales": norm, "horas_extras": extra, "tipo": "trabajo"
                }).execute()
                del st.session_state.fichar_dia; st.rerun()
            if st.button("🗑️"):
                supabase.table("fichajes").delete().eq("empleado_id", id_trab).eq("fecha_dia", f_dia).execute()
                del st.session_state.fichar_dia; st.rerun()
