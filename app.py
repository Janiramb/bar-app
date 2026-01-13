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
        height: 120px !important;
        font-size: 30px !important;
        margin-bottom: 25px !important;
        border: 4px solid #5D6D7E !important;
        border-radius: 20px !important;
        box-shadow: 4px 4px 10px rgba(0,0,0,0.2) !important;
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
        min-height: 95px;
        background-color: white;
        color: black;
    }}
    .resumen-pie {{
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #5D6D7E;
        text-align: center;
        font-size: 20px;
        font-weight: bold;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE CÁLCULO ---
def calcular_duracion_horas(h_ent, h_sal):
    fmt = "%H:%M"
    try:
        t1 = datetime.strptime(h_ent, fmt)
        t2 = datetime.strptime(h_sal, fmt)
        if t2 < t1: t2 += timedelta(days=1)
        return (t2 - t1).total_seconds() / 3600
    except: return 0.0

# --- NAVEGACIÓN ---
if 'page' not in st.session_state: st.session_state.page = 'inicio'
if 'm' not in st.session_state: st.session_state.m = datetime.now().month
if 'a' not in st.session_state: st.session_state.a = datetime.now().year

# --- PANTALLA 1: INICIO ---
if st.session_state.page == 'inicio':
    st.markdown("<h1 style='text-align:center; font-size: 55px; padding-bottom: 30px;'>🍺 HORARIO DESASTRE</h1>", unsafe_allow_html=True)
    _, col_centro, _ = st.columns([0.3, 2.4, 0.3])
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
    st.title("⚙️ Gestión de Horarios")
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    col_j, col_i = st.columns(2)
    with col_j:
        st.subheader("👩‍🦰 Base JANIRA")
        with st.form("form_jani"):
            h_j = [st.number_input(f"{d}", value=5.0, step=0.5, key=f"hj_{i}") for i, d in enumerate(dias)]
            if st.form_submit_button("💾 GUARDAR JANIRA"):
                for i, v in enumerate(h_j):
                    supabase.table("horarios_semanales").upsert({"empleado_id": 2, "dia_semana": i, "hora_inicio": str(v)}).execute()
                st.success("Horario Janira OK")
    with col_i:
        st.subheader("👩‍🦳 Base IRIA")
        with st.form("form_iria"):
            h_i = [st.number_input(f"{d}", value=5.0, step=0.5, key=f"hi_{i}") for i, d in enumerate(dias)]
            if st.form_submit_button("💾 GUARDAR IRIA"):
                for i, v in enumerate(h_i):
                    supabase.table("horarios_semanales").upsert({"empleado_id": 3, "dia_semana": i, "hora_inicio": str(v)}).execute()
                st.success("Horario Iria OK")

# --- PANTALLA 3: CALENDARIO ---
elif st.session_state.page == 'calendario':
    es_alex = (st.session_state.user == 'Alex')
    id_t = st.session_state.emp_id
    nom = st.session_state.user
    st.markdown(f"<style>.stApp {{ background-color: {COLOR_JANI if id_t==2 else COLOR_IRIA}; }}</style>", unsafe_allow_html=True)
    
    # Navegación mes
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

    # Cargar datos
    res_f = supabase.table("fichajes").select("*").eq("empleado_id", id_t).execute()
    df_f = pd.DataFrame(res_f.data) if res_f.data else pd.DataFrame()
    res_s = supabase.table("horarios_semanales").select("*").eq("empleado_id", id_t).execute()
    base_h = {int(i['dia_semana']): float(i['hora_inicio']) for i in res_s.data}
    res_e = supabase.table("dias_especiales").select("*").eq("empleado_id", id_t).execute()
    df_e = pd.DataFrame(res_e.data) if res_e.data else pd.DataFrame()

    total_mes_n, total_mes_e, total_mes_d = 0.0, 0.0, 0.0

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
                    total_mes_n += f['horas_normales']
                    total_mes_e += f['horas_extras']
                    # Calcular deuda
                    total_dia = f['horas_normales'] + f['horas_extras']
                    deuda_dia = max(0.0, h_con - total_dia)
                    total_mes_d += deuda_dia
                    
                    c_bg = "#D4EFDF" if f['horas_extras'] == 0 else "#FADBD8"
                    txt += f"<br><small>{f['hora_entrada']}-{f['hora_salida']}</small><br><b style='font-size:10px;'>{f['horas_normales']}N/{f['horas_extras']}E</b>"
                    if deuda_dia > 0: txt += f"<br><b style='color:red; font-size:9px;'>DEUDA: {deuda_dia}h</b>"
                
                st.markdown(f"<div class='dia-caja' style='background-color:{c_bg};'>{txt}</div>", unsafe_allow_html=True)
                if st.button("📝", key=f"d_{dia}"):
                    st.session_state.fichar = (f_s, h_con, f)
                    st.rerun()

    # Formulario Fichar/Modificar
    if 'fichar' in st.session_state:
        f_dia, h_con, f_actual = st.session_state.fichar
        with st.expander(f"Gestionar día {f_dia} (Contrato: {h_con}h)", expanded=True):
            ent = st.text_input("Entrada", f_actual['hora_entrada'] if f_actual else "22:00")
            sal = st.text_input("Salida", f_actual['hora_salida'] if f_actual else "03:00")
            
            c_btn1, c_btn2 = st.columns(2)
            if c_btn1.button("💾 GUARDAR / ACTUALIZAR"):
                total = calcular_duracion_horas(ent, sal)
                norm = min(total, h_con)
                ext = max(0, total - h_con)
                # Borramos anterior si existe y guardamos
                supabase.table("fichajes").delete().eq("empleado_id", id_t).eq("fecha_dia", f_dia).execute()
                supabase.table("fichajes").insert({"empleado_id": id_t, "fecha_dia": f_dia, "hora_entrada": ent, "hora_salida": sal, "horas_normales": norm, "horas_extras": ext}).execute()
                del st.session_state.fichar; st.rerun()
            
            if f_actual and c_btn2.button("🗑️ ELIMINAR TURNO"):
                supabase.table("fichajes").delete().eq("empleado_id", id_t).eq("fecha_dia", f_dia).execute()
                del st.session_state.fichar; st.rerun()

    # --- RESUMEN AL PIE ---
    st.write("---")
    st.markdown(f"""
        <div class='resumen-pie'>
            TOTAL MES: {round(total_mes_n, 2)}h Normales | 
            EXTRAS: {round(total_mes_e, 2)}h | 
            DEUDA: <span style='color:red;'>{round(total_mes_d, 2)}h</span>
        </div>
    """, unsafe_allow_html=True)
