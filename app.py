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
    .dia-caja {{ border: 1px solid #7FB3D5; padding: 10px; border-radius: 10px; text-align: center; min-height: 125px; background-color: white; color: black; }}
    .resumen-pie {{ background-color: white; padding: 20px; border-radius: 15px; border: 3px solid #5D6D7E; text-align: center; font-size: 20px; font-weight: bold; color: #2C3E50; }}
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE TIEMPOS ---
def calcular_tiempos_finales(h_ent, h_sal, h_con, es_ultimo_dia):
    fmt = "%H:%M"
    try:
        t1 = datetime.strptime(h_ent, fmt)
        t2 = datetime.strptime(h_sal, fmt)
        paso_medianoche = t2 <= t1
        if paso_medianoche: t2 += timedelta(days=1)
        total_h = (t2 - t1).total_seconds() / 3600

        if es_ultimo_dia and paso_medianoche:
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

# (Omitimos pantallas de inicio/alex por brevedad, centrándonos en el CALENDARIO corregido)
if st.session_state.page == 'calendario':
    id_t = st.session_state.emp_id
    es_alex = (st.session_state.user == 'Alex')
    
    # --- DATOS ---
    res_f = supabase.table("fichajes").select("*").eq("empleado_id", id_t).gte("fecha_dia", f"{st.session_state.a}-{st.session_state.m:02d}-01").lte("fecha_dia", f"{st.session_state.a}-{st.session_state.m:02d}-{calendar.monthrange(st.session_state.a, st.session_state.m)[1]}").execute()
    df_f = pd.DataFrame(res_f.data) if res_f.data else pd.DataFrame()
    res_s = supabase.table("horarios_semanales").select("*").eq("empleado_id", id_t).execute()
    base_h = {int(i['dia_semana']): float(i['hora_inicio']) for i in res_s.data}
    res_e = supabase.table("dias_especiales").select("*").eq("empleado_id", id_t).execute()
    df_e = pd.DataFrame(res_e.data) if res_e.data else pd.DataFrame()

    # --- INICIALIZAR CONTADORES ---
    total_contrato_mes = 0.0
    total_trabajado_mes = 0.0
    traspaso_saliente = 0.0
    
    cal = calendar.monthcalendar(st.session_state.a, st.session_state.m)
    ult_dia_m = calendar.monthrange(st.session_state.a, st.session_state.m)[1]

    # --- RENDER CALENDARIO ---
    for sem in cal:
        cols = st.columns(7)
        for i, dia in enumerate(sem):
            if dia == 0: continue
            f_s = f"{st.session_state.a}-{st.session_state.m:02d}-{dia:02d}"
            
            # 1. DETERMINAR CONTRATO DEL DÍA (Prioridad Estrella)
            esp = df_e[df_e['fecha'] == f_s].iloc[0] if not df_e.empty and not df_e[df_e['fecha'] == f_s].empty else None
            h_con = float(esp['horas_contrato']) if esp is not None else base_h.get(datetime(st.session_state.a, st.session_state.m, dia).weekday(), 0.0)
            
            total_contrato_mes += h_con # Aquí sumamos los 6h de los días 24 y 31 en vez de los base
            
            f = df_f[df_f['fecha_dia'] == f_s].iloc[0].to_dict() if not df_f.empty and not df_f[df_f['fecha_dia'] == f_s].empty else None
            
            with cols[i]:
                txt = f"<b>{dia}{' ★' if esp is not None else ''}</b>"
                c_bg = "white"
                if f:
                    h_reales, trasp = calcular_tiempos_finales(f['hora_entrada'], f['hora_salida'], h_con, dia == ult_dia_m)
                    total_trabajado_mes += h_reales
                    traspaso_saliente += trasp
                    
                    # Colores
                    if h_reales > h_con: c_bg = "#FADBD8" # Extra (Rojo/Rosa)
                    elif h_reales < h_con: c_bg = "#F5B041" # Debe (Naranja)
                    else: c_bg = "#D4EFDF" # Clavado (Verde)
                    
                    txt += f"<br><small>{f['hora_entrada']}-{f['hora_salida']}</small><br>{h_reales}h"
                
                st.markdown(f"<div class='dia-caja' style='background-color:{c_bg};'>{txt}</div>", unsafe_allow_html=True)
                if not es_alex and st.button("📝", key=f"d{dia}"): st.session_state.fichar = (f_s, h_con, f); st.rerun()

    # --- CÁLCULO FINAL DE RESUMEN ---
    # Horas trabajadas hoy + lo que traías del mes anterior (si existe la lógica)
    balance = total_trabajado_mes - total_contrato_mes
    
    extras_netas = max(0.0, balance)
    deuda_final = abs(min(0.0, balance))

    st.markdown("---")
    st.markdown(f"""<div class='resumen-pie'>
        CONTRATO MES: {round(total_contrato_mes, 1)}h | TRABAJADAS: {round(total_trabajado_mes, 1)}h<br>
        <span style='color: #1B4F72;'>BALANCE: {round(balance, 1)}h</span><br>
        RESULTADO: {round(deuda_final, 1)}h Debidas | {round(extras_netas, 1)}h Extras Netas
    </div>""", unsafe_allow_html=True)
