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

# --- COLORES PASTEL ---
COLOR_FONDO_BASE = "#A2D9CE"
COLOR_ALEX = "#FADBD8"
COLOR_JANI = "#FCF3CF"
COLOR_IRIA = "#EBDEF0"

# --- ESTILOS CSS ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: {COLOR_FONDO_BASE}; }}
    .big-button button {{ height: 100px !important; font-size: 25px !important; border-radius: 20px !important; border: 4px solid #5D6D7E !important; }}
    .stButton>button, div[data-testid="stFormSubmitButton"]>button {{ color: black !important; background-color: white !important; border: 2px solid #5D6D7E !important; font-weight: bold !important; }}
    .dia-caja {{ border: 1px solid #7FB3D5; padding: 8px; border-radius: 8px; text-align: center; min-height: 110px; background-color: white; color: black; }}
    .resumen-pie {{ background-color: white; padding: 20px; border-radius: 15px; border: 3px solid #5D6D7E; text-align: center; font-size: 18px; color: black; }}
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE APOYO ---
def calcular_horas_exactas(h_ent, h_sal, h_contrato):
    fmt = "%H:%M"
    try:
        t1 = datetime.strptime(h_ent, fmt)
        t2 = datetime.strptime(h_sal, fmt)
        if t2 <= t1: t2 += timedelta(days=1)
        horas_totales = (t2 - t1).total_seconds() / 3600
        contrato_decimal = float(h_contrato)
        n = min(horas_totales, contrato_decimal)
        e = max(0.0, horas_totales - contrato_decimal)
        d = max(0.0, contrato_decimal - horas_totales)
        return round(n, 2), round(e, 2), round(d, 2)
    except: return 0.0, 0.0, 0.0

# --- NAVEGACIÓN ---
if 'page' not in st.session_state: st.session_state.page = 'inicio'
if 'm' not in st.session_state: st.session_state.m = datetime.now().month
if 'a' not in st.session_state: st.session_state.a = datetime.now().year

# --- PANTALLA INICIO ---
if st.session_state.page == 'inicio':
    st.markdown("<h1 style='text-align:center;'>🍺 HORARIO DESASTRE</h1>", unsafe_allow_html=True)
    _, col_centro, _ = st.columns([0.5, 2, 0.5])
    with col_centro:
        st.markdown('<div class="big-button">', unsafe_allow_html=True)
        if st.button("🧔 PERFIL ALEX", key="alx", use_container_width=True): 
            st.session_state.page = 'menu_alex'; st.session_state.user = 'Alex'; st.rerun()
        if st.button("👩‍🦰 PERFIL JANIRA", key="jan", use_container_width=True):
            st.session_state.page = 'calendario'; st.session_state.user = 'Janira'; st.session_state.emp_id = 2; st.rerun()
        if st.button("👩‍🦳 PERFIL IRIA", key="iri", use_container_width=True):
            st.session_state.page = 'calendario'; st.session_state.user = 'Iria'; st.session_state.emp_id = 3; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- PANTALLA ALEX ---
elif st.session_state.page == 'menu_alex':
    st.markdown(f"<style>.stApp {{ background-color: {COLOR_ALEX}; }}</style>", unsafe_allow_html=True)
    if st.button("◀ VOLVER"): st.session_state.page = 'inicio'; st.rerun()
    st.title("⚙️ Panel de Alex")
    
    # CARGAR DATOS ACTUALES
    res_b = supabase.table("horarios_semanales").select("*").execute()
    db_base = pd.DataFrame(res_b.data) if res_b.data else pd.DataFrame()

    t1, t2, t3 = st.tabs(["📅 Horarios Base", "🌟 Días Estrella", "👁️ Ver Calendarios"])
    
    with t1:
        st.subheader("Configurar semana")
        dias_n = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        c_j, c_i = st.columns(2)
        with c_j:
            with st.form("fj"):
                st.write("JANIRA")
                h_j = []
                for i, d in enumerate(dias_n):
                    val = 5.0
                    if not db_base.empty:
                        m = db_base[(db_base['empleado_id']==2) & (db_base['dia_semana']==i)]
                        if not m.empty: val = float(m.iloc[0]['hora_inicio'])
                    h_j.append(st.number_input(f"{d}", value=val, key=f"j{i}"))
                if st.form_submit_button("GUARDAR JANI"):
                    supabase.table("horarios_semanales").delete().eq("empleado_id", 2).execute()
                    for i, v in enumerate(h_j):
                        supabase.table("horarios_semanales").insert({"empleado_id": 2, "dia_semana": i, "hora_inicio": str(v)}).execute()
                    st.success("Guardado Janira"); st.rerun()
        with c_i:
            with st.form("fi"):
                st.write("IRIA")
                h_i = []
                for i, d in enumerate(dias_n):
                    val = 5.0
                    if not db_base.empty:
                        m = db_base[(db_base['empleado_id']==3) & (db_base['dia_semana']==i)]
                        if not m.empty: val = float(m.iloc[0]['hora_inicio'])
                    h_i.append(st.number_input(f"{d}", value=val, key=f"i{i}"))
                if st.form_submit_button("GUARDAR IRIA"):
                    supabase.table("horarios_semanales").delete().eq("empleado_id", 3).execute()
                    for i, v in enumerate(h_i):
                        supabase.table("horarios_semanales").insert({"empleado_id": 3, "dia_semana": i, "hora_inicio": str(v)}).execute()
                    st.success("Guardado Iria"); st.rerun()
    
    with t2:
        st.subheader("Añadir Estrella ★")
        with st.form("fe"):
            emp_e = st.selectbox("Empleado", [2, 3], format_func=lambda x: "Janira" if x==2 else "Iria")
            fecha_e = st.date_input("Fecha")
            horas_e = st.number_input("Horas contrato hoy", value=8.0)
            if st.form_submit_button("AÑADIR ESTRELLA"):
                supabase.table("dias_especiales").insert({"empleado_id": emp_e, "fecha": str(fecha_e), "horas_contrato": horas_e}).execute()
                st.success("Estrella añadida")

    with t3:
        if st.button("Ir al calendario de JANIRA", use_container_width=True):
            st.session_state.page = 'calendario'; st.session_state.emp_id = 2; st.session_state.user = 'Alex'; st.rerun()
        if st.button("Ir al calendario de IRIA", use_container_width=True):
            st.session_state.page = 'calendario'; st.session_state.emp_id = 3; st.session_state.user = 'Alex'; st.rerun()

# --- PANTALLA CALENDARIO ---
elif st.session_state.page == 'calendario':
    es_alex = (st.session_state.user == 'Alex')
    id_t = st.session_state.emp_id
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
    with c2: st.markdown(f"<h2 style='text-align:center;'>{calendar.month_name[st.session_state.m].upper()} {st.session_state.a}</h2>", unsafe_allow_html=True)
    if st.button("🏠 INICIO"): st.session_state.page = 'inicio'; st.rerun()

    res_f = supabase.table("fichajes").select("*").eq("empleado_id", id_t).execute()
    df_f = pd.DataFrame(res_f.data) if res_f.data else pd.DataFrame()
    res_s = supabase.table("horarios_semanales").select("*").eq("empleado_id", id_t).execute()
    base_h = {int(i['dia_semana']): float(i['hora_inicio']) for i in res_s.data}
    res_e = supabase.table("dias_especiales").select("*").eq("empleado_id", id_t).execute()
    df_e = pd.DataFrame(res_e.data) if res_e.data else pd.DataFrame()

    t_n, t_e, t_d = 0.0, 0.0, 0.0
    cal = calendar.monthcalendar(st.session_state.a, st.session_state.m)
    
    for sem in cal:
        cols = st.columns(7)
        for i, dia in enumerate(sem):
            if dia == 0: continue
            f_s = f"{st.session_state.a}-{st.session_state.m:02d}-{dia:02d}"
            f_dt = datetime(st.session_state.a, st.session_state.m, dia)
            esp = df_e[df_e['fecha'] == f_s].iloc[0] if not df_e.empty and not df_e[df_e['fecha'] == f_s].empty else None
            h_con = esp['horas_contrato'] if esp is not None else base_h.get(f_dt.weekday(), 5.0)
            f_row = df_f[df_f['fecha_dia'] == f_s]
            f = f_row.iloc[0].to_dict() if not f_row.empty else None
            
            with cols[i]:
                c_bg = "white"
                star = " ★" if esp is not None else ""
                txt = f"<b>{dia}{star}</b>"
                if f:
                    n, extra, d = calcular_horas_exactas(f['hora_entrada'], f['hora_salida'], h_con)
                    t_n += n; t_e += extra; t_d += d
                    c_bg = "#D4EFDF" if extra == 0 else "#FADBD8"
                    txt += f"<br><small>{f['hora_entrada']}-{f['hora_salida']}</small><br>{round(n,1)}N/{round(extra,1)}E"
                    if d > 0: txt += f"<br><b style='color:red; font-size:10px;'>-{round(d,1)}h</b>"
                st.markdown(f"<div class='dia-caja' style='background-color:{c_bg};'>{txt}</div>", unsafe_allow_html=True)
                if not es_alex and st.button("📝", key=f"d{dia}"): st.session_state.fichar = (f_s, h_con, f); st.rerun()

    if 'fichar' in st.session_state:
        f_dia, h_c, f_act = st.session_state.fichar
        with st.form("form_f"):
            e_in = st.text_input("Entrada", f_act['hora_entrada'] if f_act else "22:00")
            s_out = st.text_input("Salida", f_act['hora_salida'] if f_act else "03:00")
            c1, c2 = st.columns(2)
            if c1.form_submit_button("💾 GUARDAR"):
                n, e, d = calcular_horas_exactas(e_in, s_out, h_c)
                supabase.table("fichajes").delete().eq("empleado_id", id_t).eq("fecha_dia", f_dia).execute()
                supabase.table("fichajes").insert({"empleado_id": id_t, "fecha_dia": f_dia, "hora_entrada": e_in, "hora_salida": s_out, "horas_normales": n, "horas_extras": e}).execute()
                del st.session_state.fichar; st.rerun()
            if c2.form_submit_button("🗑️ BORRAR"):
                supabase.table("fichajes").delete().eq("empleado_id", id_t).eq("fecha_dia", f_dia).execute()
                del st.session_state.fichar; st.rerun()
        if st.button("Cerrar"): del st.session_state.fichar; st.rerun()

    # RESUMEN
    extras_netas = max(0.0, t_e - t_d)
    st.markdown(f"""<div class='resumen-pie'>
        TOTAL MES: {round(t_n, 1)}h Normales | EXTRAS NETAS: {round(extras_netas, 1)}h | <span style='color:red;'>Deuda compensada: {round(t_d, 1)}h</span>
    </div>""", unsafe_allow_html=True)
