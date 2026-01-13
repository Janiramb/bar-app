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
COLOR_FONDO_BASE = "#A2D9CE"
COLOR_ALEX = "#FADBD8"
COLOR_JANI = "#FCF3CF"
COLOR_IRIA = "#EBDEF0"

# --- ESTILOS ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: {COLOR_FONDO_BASE}; }}
    .big-button button {{ height: 100px !important; font-size: 25px !important; border-radius: 20px !important; border: 4px solid #5D6D7E !important; }}
    .stButton>button, div[data-testid="stFormSubmitButton"]>button {{ color: black !important; background-color: white !important; border: 2px solid #5D6D7E !important; font-weight: bold !important; }}
    .dia-caja {{ border: 1px solid #7FB3D5; padding: 10px; border-radius: 10px; text-align: center; min-height: 120px; background-color: white; color: black; }}
    .info-corte {{ background-color: #D6EAF8; padding: 15px; border-radius: 10px; border: 2px solid #3498DB; text-align: center; margin-bottom: 15px; font-size: 18px; color: #1B4F72; }}
    .resumen-pie {{ background-color: white; padding: 20px; border-radius: 15px; border: 3px solid #5D6D7E; text-align: center; font-size: 20px; font-weight: bold; color: #2C3E50; }}
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE TIEMPOS ---
def calcular_tiempos_traspaso(h_ent, h_sal, h_con, es_ultimo_dia):
    fmt = "%H:%M"
    try:
        t1 = datetime.strptime(h_ent, fmt)
        t2 = datetime.strptime(h_sal, fmt)
        if t2 <= t1: t2 += timedelta(days=1)
        total_h = (t2 - t1).total_seconds() / 3600
        h_traspaso = 0.0
        if es_ultimo_dia and (t2.day != t1.day):
            t_corte = (datetime.combine(t1.date(), datetime.min.time()) + timedelta(days=1))
            h_este_mes = (t_corte - t1).total_seconds() / 3600
            h_traspaso = total_h - h_este_mes
            total_h = h_este_mes
        n = min(total_h, h_con)
        e = max(0.0, total_h - h_con)
        d = max(0.0, h_con - total_h)
        return round(n, 1), round(e, 1), round(d, 1), round(h_traspaso, 1)
    except: return 0.0, 0.0, 0.0, 0.0

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
        if st.button("🧔 PERFIL ALEX", key="alx", use_container_width=True): st.session_state.page = 'menu_alex'; st.rerun()
        if st.button("👩‍🦰 PERFIL JANIRA", key="jan", use_container_width=True):
            st.session_state.page = 'calendario'; st.session_state.user = 'Janira'; st.session_state.emp_id = 2; st.rerun()
        if st.button("👩‍🦳 PERFIL IRIA", key="iri", use_container_width=True):
            st.session_state.page = 'calendario'; st.session_state.user = 'Iria'; st.session_state.emp_id = 3; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- PANTALLA ALEX ---
elif st.session_state.page == 'menu_alex':
    st.markdown(f"<style>.stApp {{ background-color: {COLOR_ALEX}; }}</style>", unsafe_allow_html=True)
    if st.button("◀ VOLVER"): st.session_state.page = 'inicio'; st.rerun()
    st.title("⚙️ Panel de Control - Alex")
    
    tab1, tab2 = st.tabs(["📅 Horarios Base", "🌟 Días Estrella"])
    
    with tab1:
        res_b = supabase.table("horarios_semanales").select("*").execute()
        db_base = pd.DataFrame(res_b.data) if res_b.data else pd.DataFrame()
        dias_n = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        
        cj, ci = st.columns(2)
        with cj:
            st.subheader("👩‍🦰 JANIRA")
            if not db_base.empty:
                df_j = db_base[db_base['empleado_id']==2].copy()
                if not df_j.empty:
                    df_j['Día'] = df_j['dia_semana'].map(lambda x: dias_n[int(x)])
                    st.table(df_j[['Día', 'hora_inicio']])
            with st.form("fj"):
                hj = [st.number_input(f"Nuevo {d}", value=5.0, step=0.5, key=f"j{i}") for i, d in enumerate(dias_n)]
                if st.form_submit_button("ACTUALIZAR JANIRA"):
                    supabase.table("horarios_semanales").delete().eq("empleado_id", 2).execute()
                    for i, v in enumerate(hj): supabase.table("horarios_semanales").insert({"empleado_id": 2, "dia_semana": i, "hora_inicio": str(v)}).execute()
                    st.success("Cargado"); st.rerun()

        with ci:
            st.subheader("👩‍🦳 IRIA")
            if not db_base.empty:
                df_i = db_base[db_base['empleado_id']==3].copy()
                if not df_i.empty:
                    df_i['Día'] = df_i['dia_semana'].map(lambda x: dias_n[int(x)])
                    st.table(df_i[['Día', 'hora_inicio']])
            with st.form("fi"):
                hi = [st.number_input(f"Nuevo {d}", value=5.0, step=0.5, key=f"i{i}") for i, d in enumerate(dias_n)]
                if st.form_submit_button("ACTUALIZAR IRIA"):
                    supabase.table("horarios_semanales").delete().eq("empleado_id", 3).execute()
                    for i, v in enumerate(hi): supabase.table("horarios_semanales").insert({"empleado_id": 3, "dia_semana": i, "hora_inicio": str(v)}).execute()
                    st.success("Cargado"); st.rerun()

    with tab2:
        st.subheader("Marcar Día con Estrella ★")
        with st.form("f_estrella"):
            e_id = st.selectbox("Empleado", [2, 3], format_func=lambda x: "Janira" if x==2 else "Iria")
            f_est = st.date_input("Fecha Especial")
            h_est = st.number_input("Horas Contrato para este día", value=8.0, step=0.5)
            if st.form_submit_button("GUARDAR DÍA ESTRELLA"):
                supabase.table("dias_especiales").insert({"empleado_id": e_id, "fecha": str(f_est), "horas_contrato": h_est}).execute()
                st.success(f"Estrella añadida para el {f_est}")

# --- PANTALLA CALENDARIO ---
elif st.session_state.page == 'calendario':
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

    # Lógica de Traspaso
    fecha_ant = datetime(st.session_state.a, st.session_state.m, 1) - timedelta(days=1)
    res_ant = supabase.table("fichajes").select("*").eq("empleado_id", id_t).eq("fecha_dia", fecha_ant.strftime("%Y-%m-%d")).execute()
    traspaso = 0.0
    if res_ant.data:
        f_ant = res_ant.data[0]
        res_s_ant = supabase.table("horarios_semanales").select("*").eq("empleado_id", id_t).eq("dia_semana", fecha_ant.weekday()).execute()
        h_con_ant = float(res_s_ant.data[0]['hora_inicio']) if res_s_ant.data else 5.0
        _, _, _, traspaso = calcular_tiempos_traspaso(f_ant['hora_entrada'], f_ant['hora_salida'], h_con_ant, True)
    if traspaso > 0: st.markdown(f"<div class='info-corte'>ℹ️ {traspaso}h normales traspasadas del mes anterior</div>", unsafe_allow_html=True)

    # Datos
    res_f = supabase.table("fichajes").select("*").eq("empleado_id", id_t).gte("fecha_dia", f"{st.session_state.a}-{st.session_state.m:02d}-01").lte("fecha_dia", f"{st.session_state.a}-{st.session_state.m:02d}-{calendar.monthrange(st.session_state.a, st.session_state.m)[1]}").execute()
    df_f = pd.DataFrame(res_f.data) if res_f.data else pd.DataFrame()
    res_s = supabase.table("horarios_semanales").select("*").eq("empleado_id", id_t).execute()
    base_h = {int(i['dia_semana']): float(i['hora_inicio']) for i in res_s.data}
    res_e = supabase.table("dias_especiales").select("*").eq("empleado_id", id_t).execute()
    df_e = pd.DataFrame(res_e.data) if res_e.data else pd.DataFrame()

    total_r, total_b, total_d = 0.0, 0.0, 0.0
    cal = calendar.monthcalendar(st.session_state.a, st.session_state.m)
    ult_dia = calendar.monthrange(st.session_state.a, st.session_state.m)[1]

    for sem in cal:
        cols = st.columns(7)
        for i, dia in enumerate(sem):
            if dia == 0: continue
            f_s = f"{st.session_state.a}-{st.session_state.m:02d}-{dia:02d}"
            esp = df_e[df_e['fecha'] == f_s].iloc[0] if not df_e.empty and not df_e[df_e['fecha'] == f_s].empty else None
            h_con = esp['horas_contrato'] if esp is not None else base_h.get(datetime(st.session_state.a, st.session_state.m, dia).weekday(), 5.0)
            f_row = df_f[df_f['fecha_dia'] == f_s]
            f = f_row.iloc[0].to_dict() if not f_row.empty else None
            
            with cols[i]:
                txt = f"<b>{dia}{' ★' if esp is not None else ''}</b>"
                c_bg = "white"
                if f:
                    n, b, d, _ = calcular_tiempos_traspaso(f['hora_entrada'], f['hora_salida'], h_con, dia == ult_dia)
                    total_r += n; total_b += b; total_d += d
                    c_bg = "#D4EFDF" if b == 0 else "#FADBD8"
                    txt += f"<br><small>{f['hora_entrada']}-{f['hora_salida']}</small><br>{n}N/{b}E"
                    if d > 0: txt += f"<br><b style='color:red;'>-{d}h</b>"
                st.markdown(f"<div class='dia-caja' style='background-color:{c_bg};'>{txt}</div>", unsafe_allow_html=True)
                if st.button("📝", key=f"d{dia}"): st.session_state.fichar = (f_s, h_con, f); st.rerun()

    # Resumen
    st.markdown("---")
    st.markdown(f"<div class='resumen-pie'>TOTAL MES: {round(total_r + total_d + traspaso, 1)}h NORMALES ({round(total_r + traspaso, 1)} Realizadas + {total_d} Debidas)<br>EXTRAS NETAS: {round(total_b - total_d, 1)}h</div>", unsafe_allow_html=True)

    if 'fichar' in st.session_state:
        f_dia, h_c, f_act = st.session_state.fichar
        with st.form("form_f"):
            ent = st.text_input("Entrada", f_act['hora_entrada'] if f_act else "22:00")
            sal = st.text_input("Salida", f_act['hora_salida'] if f_act else "03:00")
            if st.form_submit_button("💾 GUARDAR"):
                supabase.table("fichajes").delete().eq("empleado_id", id_t).eq("fecha_dia", f_dia).execute()
                supabase.table("fichajes").insert({"empleado_id": id_t, "fecha_dia": f_dia, "hora_entrada": ent, "hora_salida": sal, "horas_normales": 0, "horas_extras": 0}).execute()
                del st.session_state.fichar; st.rerun()
