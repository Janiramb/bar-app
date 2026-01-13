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
COLOR_FONDO_BASE = "#A2D9CE"   # Verde menta oscuro
COLOR_ALEX = "#FADBD8"         # Rojo pastel
COLOR_JANI = "#FCF3CF"         # Amarillo mostaza pastel
COLOR_IRIA = "#EBDEF0"         # Morado pastel

# --- ESTILOS CSS ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: {COLOR_FONDO_BASE}; }}
    .big-button button {{
        height: 80px !important;
        font-size: 22px !important;
        border: 3px solid #5D6D7E !important;
    }}
    .stButton>button, div[data-testid="stFormSubmitButton"]>button {{
        color: black !important;
        background-color: white !important;
        border: 2px solid #5D6D7E !important;
        border-radius: 12px;
        font-weight: bold !important;
        width: 100%;
    }}
    .dia-caja {{
        border: 1px solid #7FB3D5;
        padding: 8px;
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
if 'm' not in st.session_state: st.session_state.m = datetime.now().month
if 'a' not in st.session_state: st.session_state.a = datetime.now().year

# --- PANTALLA 1: INICIO ---
if st.session_state.page == 'inicio':
    st.markdown("<h1 style='text-align:center; font-size: 50px;'>🍺 HORARIO DESASTRE</h1>", unsafe_allow_html=True)
    _, col_centro, _ = st.columns([0.5, 2, 0.5])
    with col_centro:
        st.markdown('<div class="big-button">', unsafe_allow_html=True)
        st.markdown(f'<style>div[row-id="alx"] button {{background-color: {COLOR_ALEX} !important;}}</style>', unsafe_allow_html=True)
        if st.button("🧔 PERFIL ALEX", key="alx"): st.session_state.page = 'menu_alex'; st.rerun()
        st.write("")
        st.markdown(f'<style>div[row-id="jan"] button {{background-color: {COLOR_JANI} !important;}}</style>', unsafe_allow_html=True)
        if st.button("👩‍🦰 PERFIL JANIRA", key="jan"):
            st.session_state.page = 'calendario'; st.session_state.user = 'Janira'; st.session_state.emp_id = 2; st.rerun()
        st.write("")
        st.markdown(f'<style>div[row-id="iri"] button {{background-color: {COLOR_IRIA} !important;}}</style>', unsafe_allow_html=True)
        if st.button("👩‍🦳 PERFIL IRIA", key="iri"):
            st.session_state.page = 'calendario'; st.session_state.user = 'Iria'; st.session_state.emp_id = 3; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- PANTALLA 2: MENU ALEX ---
elif st.session_state.page == 'menu_alex':
    st.markdown(f"<style>.stApp {{ background-color: {COLOR_ALEX}; }}</style>", unsafe_allow_html=True)
    if st.button("◀ VOLVER"): st.session_state.page = 'inicio'; st.rerun()
    st.title("⚙️ Gestión de Horarios Base")

    dias_nombre = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    col_j, col_i = st.columns(2)

    with col_j:
        st.subheader("👩‍🦰 Horario Base JANIRA")
        with st.form("form_jani"):
            horas_j = []
            for d in range(7):
                horas_j.append(st.number_input(f"{dias_nombre[d]}", value=5.0, step=0.5, key=f"j_{d}"))
            if st.form_submit_button("💾 GUARDAR HORARIO JANI"):
                for d, h in enumerate(horas_j):
                    supabase.table("horarios_semanales").upsert({"empleado_id": 2, "dia_semana": d, "hora_inicio": str(h)}).execute()
                st.success("Horario de Janira actualizado")

    with col_i:
        st.subheader("👩‍🦳 Horario Base IRIA")
        with st.form("form_iria"):
            horas_i = []
            for d in range(7):
                horas_i.append(st.number_input(f"{dias_nombre[d]}", value=5.0, step=0.5, key=f"i_{d}"))
            if st.form_submit_button("💾 GUARDAR HORARIO IRIA"):
                for d, h in enumerate(horas_i):
                    supabase.table("horarios_semanales").upsert({"empleado_id": 3, "dia_semana": d, "hora_inicio": str(h)}).execute()
                st.success("Horario de Iria actualizado")

    st.divider()
    st.subheader("🌟 Días Estrella (Días Sueltos)")
    with st.expander("Añadir día especial"):
        with st.form("f_esp"):
            e_e = st.selectbox("Empleado", [2, 3], format_func=lambda x: "Janira" if x==2 else "Iria")
            f_e = st.date_input("Fecha")
            h_e = st.number_input("Horas", value=8.0)
            if st.form_submit_button("Añadir Estrella ★"):
                supabase.table("dias_especiales").insert({"empleado_id": e_e, "fecha": str(f_e), "horas_contrato": h_e}).execute()
                st.success("Día especial añadido")

# --- PANTALLA 3: CALENDARIO INTERACTIVO ---
elif st.session_state.page == 'calendario':
    es_alex = (st.session_state.user == 'Alex')
    id_t = st.session_state.ver_id if es_alex else st.session_state.emp_id
    nom = "Janira" if id_t == 2 else "Iria"
    st.markdown(f"<style>.stApp {{ background-color: {COLOR_JANI if id_t==2 else COLOR_IRIA}; }}</style>", unsafe_allow_html=True)
    
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

    # Cargar datos de Supabase
    res_f = supabase.table("fichajes").select("*").eq("empleado_id", id_t).execute()
    df_f = pd.DataFrame(res_f.data) if res_f.data else pd.DataFrame()
    res_s = supabase.table("horarios_semanales").select("*").eq("empleado_id", id_t).execute()
    base_h = {int(i['dia_semana']): float(i['hora_inicio']) for i in res_s.data}
    res_e = supabase.table("dias_especiales").select("*").eq("empleado_id", id_t).execute()
    df_e = pd.DataFrame(res_e.data) if res_e.data else pd.DataFrame()

    # Dibujar calendario
    cal = calendar.monthcalendar(st.session_state.a, st.session_state.m)
    cols_h = st.columns(7)
    for i, d in enumerate(["LUN", "MAR", "MIE", "JUE", "VIE", "SAB", "DOM"]): cols_h[i].markdown(f"**{d}**")

    for sem in cal:
        cols = st.columns(7)
        for i, dia in enumerate(sem):
            if dia == 0: continue
            f_s = f"{st.session_state.a}-{st.session_state.m:02d}-{dia:02d}"
            f_dt = datetime(st.session_state.a, st.session_state.m, dia)
            
            f = df_f[df_f['fecha_dia'] == f_s].iloc[0] if not df_f.empty and not df_f[df_f['fecha_dia'] == f_s].empty else None
            esp = df_e[df_e['fecha'] == f_s].iloc[0] if not df_e.empty and not df_e[df_e['fecha'] == f_s].empty else None
            h_con = esp['horas_contrato'] if esp is not None else base_h.get(f_dt.weekday(), 5.0)

            with cols[i]:
                c_bg = "white"
                txt = f"<b>{dia}{' ★' if esp is not None else ''}</b>"
                if f is not None:
                    c_bg = "#D4EFDF"
                    txt += f"<br><small>{f['hora_entrada']}-{f['hora_salida']}</small><br><b style='font-size:10px;'>{f['horas_normales']}N/{f['horas_extras']}E</b>"
                st.markdown(f"<div class='dia-caja' style='background-color:{c_bg};'>{txt}</div>", unsafe_allow_html=True)
                if not es_alex:
                    if st.button("📝", key=f"d_{dia}"):
                        st.session_state.fichar = (f_s, h_con)
                        st.rerun()

    # Formulario para fichar
    if 'fichar' in st.session_state and not es_alex:
        f_dia, h_base = st.session_state.fichar
        with st.expander(f"Fichar día {f_dia}", expanded=True):
            ent = st.text_input("Entrada", "22:00")
            sal = st.text_input("Salida", "03:00")
            if st.button("Confirmar"):
                supabase.table("fichajes").insert({"empleado_id": id_t, "fecha_dia": f_dia, "hora_entrada": ent, "hora_salida": sal, "horas_normales": h_base, "horas_extras": 0.0}).execute()
                del st.session_state.fichar; st.rerun()
