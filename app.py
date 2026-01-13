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
    .info-corte {{ background-color: #D6EAF8; padding: 10px; border-radius: 10px; border: 1px solid #3498DB; text-align: center; margin-bottom: 10px; font-weight: bold; }}
    .resumen-pie {{ background-color: transparent; padding: 20px; text-align: center; font-size: 20px; font-weight: bold; color: #2C3E50; }}
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE TIEMPOS ---
def calcular_tiempos_corte(h_ent, h_sal, h_con, es_ultimo_dia):
    fmt = "%H:%M"
    try:
        t1 = datetime.strptime(h_ent, fmt)
        t2 = datetime.strptime(h_sal, fmt)
        if t2 <= t1: t2 += timedelta(days=1)
        
        total_h = (t2 - t1).total_seconds() / 3600
        h_fuera = 0.0
        
        if es_ultimo_dia and (t2.day != t1.day):
            t_corte = datetime.strptime("23:59", "%H:%M") + timedelta(minutes=1)
            t_corte = t_corte.replace(year=t1.year, month=t1.month, day=t1.day)
            h_este_mes = (t_corte - t1).total_seconds() / 3600
            h_fuera = total_h - h_este_mes
            total_h = h_este_mes
            
        n = min(total_h, h_con)
        e = max(0.0, total_h - h_con)
        d = max(0.0, h_con - total_h)
        return round(n, 1), round(e, 1), round(d, 1), round(h_fuera, 1)
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
    st.title("⚙️ Gestión de Alex")
    
    # Cargar horarios base para que Alex los vea
    res_b = supabase.table("horarios_semanales").select("*").execute()
    db_base = pd.DataFrame(res_b.data) if res_b.data else pd.DataFrame()

    dias_n = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    cj, ci = st.columns(2)
    with cj:
        st.subheader("👩‍🦰 JANIRA")
        with st.form("fj"):
            hj = []
            for i, d in enumerate(dias_n):
                val = 5.0
                if not db_base.empty:
                    m = db_base[(db_base['empleado_id']==2) & (db_base['dia_semana']==i)]
                    if not m.empty: val = float(m.iloc[0]['hora_inicio'])
                hj.append(st.number_input(f"{d}", value=val, key=f"j{i}"))
            if st.form_submit_button("GUARDAR JANI"):
                supabase.table("horarios_semanales").delete().eq("empleado_id", 2).execute()
                for i, v in enumerate(hj): supabase.table("horarios_semanales").insert({"empleado_id": 2, "dia_semana": i, "hora_inicio": str(v)}).execute()
                st.success("Guardado")
    with ci:
        st.subheader("👩‍🦳 IRIA")
        with st.form("fi"):
            hi = []
            for i, d in enumerate(dias_n):
                val = 5.0
                if not db_base.empty:
                    m = db_base[(db_base['empleado_id']==3) & (db_base['dia_semana']==i)]
                    if not m.empty: val = float(m.iloc[0]['hora_inicio'])
                hi.append(st.number_input(f"{d}", value=val, key=f"i{i}"))
            if st.form_submit_button("GUARDAR IRIA"):
                supabase.table("horarios_semanales").delete().eq("empleado_id", 3).execute()
                for i, v in enumerate(hi): supabase.table("horarios_semanales").insert({"empleado_id": 3, "dia_semana": i, "hora_inicio": str(v)}).execute()
                st.success("Guardado")

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

    # Filtro del mes para el resumen
    inicio_m = f"{st.session_state.a}-{st.session_state.m:02d}-01"
    fin_m = f"{st.session_state.a}-{st.session_state.m:02d}-{calendar.monthrange(st.session_state.a, st.session_state.m)[1]}"
    
    # Buscar si hay horas pendientes del mes anterior (el último día del mes pasado)
    fecha_ant = datetime(st.session_state.a, st.session_state.m, 1) - timedelta(days=1)
    f_ant_s = fecha_ant.strftime("%Y-%m-%d")
    res_ant = supabase.table("fichajes").select("*").eq("empleado_id", id_t).eq("fecha_dia", f_ant_s).execute()
    
    h_pendientes = 0.0
    if res_ant.data:
        f_ant = res_ant.data[0]
        # Necesitamos el contrato de ese día para el cálculo
        res_s_ant = supabase.table("horarios_semanales").select("*").eq("empleado_id", id_t).eq("dia_semana", fecha_ant.weekday()).execute()
        h_con_ant = float(res_s_ant.data[0]['hora_inicio']) if res_s_ant.data else 5.0
        _, _, _, h_pendientes = calcular_tiempos_corte(f_ant['hora_entrada'], f_ant['hora_salida'], h_con_ant, True)

    if h_pendientes > 0:
        st.markdown(f"<div class='info-corte'>ℹ️ Tienes {h_pendientes}h extras del cierre del mes anterior</div>", unsafe_allow_html=True)

    # Cargar datos actuales
    res_f = supabase.table("fichajes").select("*").eq("empleado_id", id_t).gte("fecha_dia", inicio_m).lte("fecha_dia", fin_m).execute()
    df_f = pd.DataFrame(res_f.data) if res_f.data else pd.DataFrame()
    res_s = supabase.table("horarios_semanales").select("*").eq("empleado_id", id_t).execute()
    base_h = {int(i['dia_semana']): float(i['hora_inicio']) for i in res_s.data}

    total_real, total_brut, total_deb = 0.0, 0.0, 0.0
    cal = calendar.monthcalendar(st.session_state.a, st.session_state.m)
    ultimo_dia_m = calendar.monthrange(st.session_state.a, st.session_state.m)[1]
    
    for sem in cal:
        cols = st.columns(7)
        for i, dia in enumerate(sem):
            if dia == 0: continue
            f_s = f"{st.session_state.a}-{st.session_state.m:02d}-{dia:02d}"
            f_dt = datetime(st.session_state.a, st.session_state.m, dia)
            h_con = base_h.get(f_dt.weekday(), 5.0)
            f_row = df_f[df_f['fecha_dia'] == f_s]
            f = f_row.iloc[0].to_dict() if not f_row.empty else None
            
            with cols[i]:
                c_bg = "white"
                txt = f"<b>{dia}</b>"
                if f:
                    n, brute, deb, _ = calcular_tiempos_corte(f['hora_entrada'], f['hora_salida'], h_con, dia == ultimo_dia_m)
                    total_real += (n + brute); total_brut += brute; total_deb += deb
                    c_bg = "#D4EFDF" if brute == 0 else "#FADBD8"
                    txt += f"<br><small>{f['hora_entrada']}-{f['hora_salida']}</small><br>{round(n,1)}h N / {round(brute,1)}h E"
                    if deb > 0: 
                        c_bg = "#F5B041"
                        txt += f"<br><b style='color:#C0392B; font-size:12px;'>DEBES {round(deb,1)}h</b>"
                st.markdown(f"<div class='dia-caja' style='background-color:{c_bg};'>{txt}</div>", unsafe_allow_html=True)
                if st.button("📝", key=f"d{dia}"): st.session_state.fichar = (f_s, h_con, f); st.rerun()

    # RESUMEN (Sumando lo pendiente solo aquí)
    total_brut += h_pendientes
    st.markdown("---")
    st.markdown(f"""
        <div class='resumen-pie'>
            TOTAL MES: {round(total_real + total_deb, 1)}h NORMALES (Realizadas + Debidas)<br>
            EXTRAS NETAS: {round(total_brut - total_deb, 1)}h (Incluye {h_pendientes}h del mes anterior)
        </div>
    """, unsafe_allow_html=True)

    if 'fichar' in st.session_state:
        f_dia, h_c, f_act = st.session_state.fichar
        with st.form("f_f"):
            ent = st.text_input("Entrada", f_act['hora_entrada'] if f_act else "22:00")
            sal = st.text_input("Salida", f_act['hora_salida'] if f_act else "03:00")
            c1, c2 = st.columns(2)
            if c1.form_submit_button("💾 GUARDAR"):
                supabase.table("fichajes").delete().eq("empleado_id", id_t).eq("fecha_dia", f_dia).execute()
                supabase.table("fichajes").insert({"empleado_id": id_t, "fecha_dia": f_dia, "hora_entrada": ent, "hora_salida": sal, "horas_normales": 0, "horas_extras": 0}).execute()
                del st.session_state.fichar; st.rerun()
            if c2.form_submit_button("🗑️ BORRAR"):
                supabase.table("fichajes").delete().eq("empleado_id", id_t).eq("fecha_dia", f_dia).execute()
                del st.session_state.fichar; st.rerun()
