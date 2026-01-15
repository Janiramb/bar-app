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

# --- ESTILOS CSS ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: {COLOR_FONDO_BASE}; }}
    .dia-caja {{ border: 1px solid #7FB3D5; padding: 10px; border-radius: 10px; text-align: center; min-height: 125px; background-color: white; color: black; }}
    .resumen-pie {{ background-color: white; padding: 20px; border-radius: 15px; border: 3px solid #5D6D7E; text-align: center; font-size: 20px; font-weight: bold; color: #2C3E50; }}
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE TIEMPOS ---
def calcular_horas_fisicas(h_ent, h_sal, es_ultimo_dia):
    fmt = "%H:%M"
    try:
        t1 = datetime.strptime(h_ent, fmt)
        t2 = datetime.strptime(h_sal, fmt)
        if t2 <= t1: t2 += timedelta(days=1)
        total_h = (t2 - t1).total_seconds() / 3600
        
        # Si es último día, calculamos si hay traspaso (horas tras medianoche)
        h_traspaso = 0.0
        if es_ultimo_dia and (datetime.strptime(h_sal, fmt) < datetime.strptime(h_ent, fmt)):
            medianoche = (t1 + timedelta(days=1)).replace(hour=0, minute=0)
            h_este_mes = (medianoche - t1).total_seconds() / 3600
            h_traspaso = total_h - h_este_mes
            return round(h_este_mes, 2), round(h_traspaso, 2)

        return round(total_h, 2), 0.0
    except: return 0.0, 0.0

# --- NAVEGACIÓN ---
if 'page' not in st.session_state: st.session_state.page = 'inicio'
if 'm' not in st.session_state: st.session_state.m = datetime.now().month
if 'a' not in st.session_state: st.session_state.a = datetime.now().year

# --- PANTALLAS (INICIO / ALEX) ---
if st.session_state.page == 'inicio':
    st.markdown("<h1 style='text-align:center;'>🍺 HORARIO DESASTRE</h1>", unsafe_allow_html=True)
    _, col_c, _ = st.columns([0.5, 2, 0.5])
    with col_c:
        if st.button("🧔 PERFIL ALEX", key="alx", use_container_width=True): st.session_state.page = 'menu_alex'; st.rerun()
        if st.button("👩‍🦰 PERFIL JANIRA", key="jan", use_container_width=True):
            st.session_state.page = 'calendario'; st.session_state.user = 'Janira'; st.session_state.emp_id = 2; st.rerun()
        if st.button("👩‍🦳 PERFIL IRIA", key="iri", use_container_width=True):
            st.session_state.page = 'calendario'; st.session_state.user = 'Iria'; st.session_state.emp_id = 3; st.rerun()

elif st.session_state.page == 'menu_alex':
    st.markdown(f"<style>.stApp {{ background-color: {COLOR_ALEX}; }}</style>", unsafe_allow_html=True)
    if st.button("◀ VOLVER"): st.session_state.page = 'inicio'; st.rerun()
    st.title("⚙️ Gestión de Alex")
    tab1, tab2, tab3 = st.tabs(["📅 Horarios Base", "🌟 Días Estrella", "👁️ Ver Calendarios"])
    with tab1:
        # (Lógica de horarios base igual)
        pass
    with tab2:
        with st.form("f_star"):
            e_id = st.selectbox("Empleado", [2, 3], format_func=lambda x: "Janira" if x==2 else "Iria")
            f_star = st.date_input("Fecha Especial")
            h_star = st.number_input("Horas Contrato", value=6.0, step=0.5)
            if st.form_submit_button("GUARDAR ESTRELLA"):
                supabase.table("dias_especiales").insert({"empleado_id": e_id, "fecha": str(f_star), "horas_contrato": h_star}).execute()
                st.success("Estrella añadida")
    with tab3:
        # (Lógica ver calendarios igual)
        pass

# --- PANTALLA CALENDARIO ---
elif st.session_state.page == 'calendario':
    es_alex = (st.session_state.user == 'Alex')
    id_t = st.session_state.emp_id
    st.markdown(f"<style>.stApp {{ background-color: {COLOR_JANI if id_t==2 else COLOR_IRIA}; }}</style>", unsafe_allow_html=True)
    
    # Navegación meses
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

    # --- LÓGICA TRASPASO ANTERIOR ---
    fecha_ant = datetime(st.session_state.a, st.session_state.m, 1) - timedelta(days=1)
    res_ant = supabase.table("fichajes").select("*").eq("empleado_id", id_t).eq("fecha_dia", fecha_ant.strftime("%Y-%m-%d")).execute()
    traspaso_recibido = 0.0
    if res_ant.data:
        f_ant = res_ant.data[0]
        # Para saber el traspaso del último día anterior, usamos la lógica de medianoche
        _, traspaso_recibido = calcular_horas_fisicas(f_ant['hora_entrada'], f_ant['hora_salida'], True)
    
    if traspaso_recibido > 0: st.info(f"Horas del mes anterior (tras medianoche): {traspaso_recibido}h")

    # --- DATOS ---
    res_f = supabase.table("fichajes").select("*").eq("empleado_id", id_t).gte("fecha_dia", f"{st.session_state.a}-{st.session_state.m:02d}-01").lte("fecha_dia", f"{st.session_state.a}-{st.session_state.m:02d}-{calendar.monthrange(st.session_state.a, st.session_state.m)[1]}").execute()
    df_f = pd.DataFrame(res_f.data) if res_f.data else pd.DataFrame()
    res_s = supabase.table("horarios_semanales").select("*").eq("empleado_id", id_t).execute()
    base_h = {int(i['dia_semana']): float(i['hora_inicio']) for i in res_s.data}
    res_e = supabase.table("dias_especiales").select("*").eq("empleado_id", id_t).execute()
    df_e = pd.DataFrame(res_e.data) if res_e.data else pd.DataFrame()

    # --- TOTALES DEL BLOQUE MENSUAL ---
    total_contrato_acumulado = 0.0
    total_trabajado_fisico = 0.0
    traspaso_proximo_mes = 0.0

    cal = calendar.monthcalendar(st.session_state.a, st.session_state.m)
    ult_dia_m = calendar.monthrange(st.session_state.a, st.session_state.m)[1]

    for sem in cal:
        cols = st.columns(7)
        for i, dia in enumerate(sem):
            if dia == 0: continue
            f_s = f"{st.session_state.a}-{st.session_state.m:02d}-{dia:02d}"
            
            # 1. Determinar CONTRATO (Estrella sustituye Base)
            esp = df_e[df_e['fecha'] == f_s].iloc[0] if not df_e.empty and not df_e[df_e['fecha'] == f_s].empty else None
            h_con = float(esp['horas_contrato']) if esp is not None else base_h.get(datetime(st.session_state.a, st.session_state.m, dia).weekday(), 0.0)
            
            total_contrato_acumulado += h_con
            
            # 2. Determinar TRABAJADO
            f = df_f[df_f['fecha_dia'] == f_s].iloc[0].to_dict() if not df_f.empty and not df_f[df_f['fecha_dia'] == f_s].empty else None
            
            with cols[i]:
                txt = f"<b>{dia}{' ★' if esp is not None else ''}</b>"
                c_bg = "white"
                if f:
                    h_fisicas, trasp = calcular_horas_fisicas(f['hora_entrada'], f['hora_salida'], dia == ult_dia_m)
                    total_trabajado_fisico += h_fisicas
                    traspaso_proximo_mes += trasp
                    
                    # Colores por día
                    if h_fisicas > h_con: c_bg = "#FADBD8"
                    elif h_fisicas < h_con: c_bg = "#F5B041"
                    else: c_bg = "#D4EFDF"
                    
                    txt += f"<br><small>{f['hora_entrada']}-{f['hora_salida']}</small><br>{h_fisicas}h"
                
                st.markdown(f"<div class='dia-caja' style='background-color:{c_bg};'>{txt}</div>", unsafe_allow_html=True)
                if not es_alex and st.button("📝", key=f"d{dia}"): st.session_state.fichar = (f_s, h_con, f); st.rerun()

    # --- BALANCE FINAL (MATEMÁTICA PURA) ---
    trabajadas_totales = total_trabajado_fisico + traspaso_recibido
    balance_final = trabajadas_totales - total_contrato_acumulado
    
    # Si balance es positivo, son extras. Si es negativo, es deuda.
    extras_netas = max(0.0, balance_final)
    deuda_neta = abs(min(0.0, balance_final))

    st.markdown("---")
    st.markdown(f"""<div class='resumen-pie'>
        CONTRATO MES: {round(total_contrato_acumulado, 2)}h | TRABAJADAS TOTALES: {round(trabajadas_totales, 2)}h<br>
        <span style='color: {"green" if balance_final >= 0 else "red"};'>
            DIFERENCIA: {round(balance_final, 2)}h
        </span><br>
        <b>RESULTADO: {round(deuda_neta, 2)}h Debidas | {round(extras_netas, 2)}h Extras Netas</b>
    </div>""", unsafe_allow_html=True)
    
    if traspaso_proximo_mes > 0:
        st.info(f"Aviso: El día {ult_dia_m} trabajaste {traspaso_proximo_mes}h tras la medianoche que se sumarán en el resumen del próximo mes.")

    # Formulario fichaje
    if 'fichar' in st.session_state and not es_alex:
        # (Lógica formulario igual)
        pass
