import streamlit as st
from supabase import create_client, Client
from datetime import datetime, timedelta
import calendar
import pandas as pd

# --- CONSTANTES DE COLOR ORIGINALES ---
COLOR_FONDO_GENERAL = "#D5F5E3" 
COLOR_ALEX_BG = "#F2D7D5"      
COLOR_JANI_BG = "#FEF9E7"      
COLOR_IRIA_BG = "#F4ECF7"      
COLOR_VACACIONES_BG = "#A2D9CE"
COLOR_FALTA_BG = "#F1948A"
COLOR_ALEX_TXT = "#C0392B"
COLOR_JANI_TXT = "#D4AC0D"
COLOR_IRIA_TXT = "#8E44AD"
COLOR_BTN_JANI = "#F9E79F"
COLOR_BTN_IRIA = "#D7BDE2"
COLOR_BTN_ALEX = "#E6B0AA"
COLOR_BTN_GUARDAR = "#ABEBC6"
COLOR_BTN_VACACIONES = "#76D7C4"

st.set_page_config(page_title="Horario Desastre", page_icon="🍺", layout="wide")

# --- CONEXIÓN ---
url = "https://kljizxbakvzytmaxqodw.supabase.co"
key = "sb_publishable_aV6LrJVsVo2a_129xBbNdw_TSO_7pDz"
supabase = create_client(url, key)

# --- ESTILOS CSS PARA REPLICAR CUSTOMTKINTER ---
def cargar_estilos(bg):
    st.markdown(f"""
        <style>
        .stApp {{ background-color: {bg}; }}
        /* Botones de Inicio */
        .stButton>button {{
            border-radius: 5px;
            font-size: 20px !important;
            height: 70px;
            border: 2px solid #555;
            color: black;
        }}
        /* Cajas de Calendario */
        .dia-container {{
            border: 1px solid #eee;
            background-color: #F9F9F9;
            padding: 8px;
            border-radius: 6px;
            min-height: 110px;
            text-align: center;
            font-family: 'Arial';
        }}
        .resumen-footer {{
            background-color: white;
            padding: 15px;
            border-radius: 5px;
            border: 1px solid #2C3E50;
            font-size: 16px;
            text-align: center;
            font-weight: bold;
            color: #2C3E50;
        }}
        </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE CÁLCULO ORIGINAL ---
def calcular_duracion_turno(h_inicio, h_fin):
    if h_inicio == "00:00" and h_fin == "00:00": return 0.0
    fmt = "%H:%M"
    t1 = datetime.strptime(h_inicio, fmt)
    t2 = datetime.strptime(h_fin, fmt)
    if t2 < t1: t2 += timedelta(days=1)
    return round((t2 - t1).total_seconds() / 3600, 2)

# --- NAVEGACIÓN ---
if 'page' not in st.session_state: st.session_state.page = 'inicio'

# --- PANTALLA INICIO ---
if st.session_state.page == 'inicio':
    cargar_estilos(COLOR_FONDO_GENERAL)
    st.markdown("<h1 style='text-align: center; font-size: 60px; font-weight: bold; color: #555;'>🍺 HORARIO DESASTRE 🍺</h1>", unsafe_allow_html=True)
    st.write("##")
    
    col_c, col_b, col_a = st.columns([1, 1.5, 1])
    with col_b:
        if st.button("ALEX", use_container_width=True): 
            st.session_state.page = 'menu_alex'; st.rerun()
        st.write("")
        # Botón Janira con su color
        st.markdown(f'<style>div[row-id="jani_btn"] button {{background-color: {COLOR_BTN_JANI} !important;}}</style>', unsafe_allow_html=True)
        if st.button("JANIRA", key="jani_btn", use_container_width=True):
            st.session_state.page = 'calendario'; st.session_state.emp_id = 2; st.rerun()
        st.write("")
        # Botón Iria con su color
        st.markdown(f'<style>div[row-id="iria_btn"] button {{background-color: {COLOR_BTN_IRIA} !important;}}</style>', unsafe_allow_html=True)
        if st.button("IRIA", key="iria_btn", use_container_width=True):
            st.session_state.page = 'calendario'; st.session_state.emp_id = 3; st.rerun()
        st.write("##")
        if st.button("❌ CERRAR APP", type="primary", use_container_width=True): st.stop()

# --- PANTALLA MENU ALEX ---
elif st.session_state.page == 'menu_alex':
    cargar_estilos(COLOR_ALEX_BG)
    if st.button("◀ VOLVER"): st.session_state.page = 'inicio'; st.rerun()
    st.markdown(f"<h1 style='text-align: center; color: {COLOR_ALEX_TXT}; font-weight: bold;'>PANEL DE CONSULTA</h1>", unsafe_allow_html=True)
    st.write("##")
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        if st.button("HORARIO JANIRA", use_container_width=True): 
            st.session_state.page = 'calendario'; st.session_state.emp_id = 2; st.rerun()
        st.write("")
        if st.button("HORARIO IRIA", use_container_width=True): 
            st.session_state.page = 'calendario'; st.session_state.emp_id = 3; st.rerun()

# --- PANTALLA CALENDARIO (Réplica de CustomTkinter) ---
elif st.session_state.page == 'calendario':
    emp_id = st.session_state.emp_id
    nombre = "Janira" if emp_id == 2 else "Iria"
    bg = COLOR_JANI_BG if emp_id == 2 else COLOR_IRIA_BG
    txt_c = COLOR_JANI_TXT if emp_id == 2 else COLOR_IRIA_TXT
    cargar_estilos(bg)
    
    col_v, col_m, col_n = st.columns([1, 4, 1])
    with col_v:
        if st.button("◀ VOLVER"): 
            st.session_state.page = 'inicio'; st.rerun()
    
    # Simulación de Navegación de Mes
    mes_actual = datetime.now().month
    anio_actual = datetime.now().year
    st.markdown(f"<h1 style='text-align: center; color: {txt_c}; font-weight: bold;'>HOLA {nombre.upper()}</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center;'>{calendar.month_name[mes_actual].upper()} {anio_actual}</h3>", unsafe_allow_html=True)

    # Dibujar Grid
    cols_h = st.columns(7)
    for i, d in enumerate(["LUN", "MAR", "MIE", "JUE", "VIE", "SAB", "DOM"]):
        cols_h[i].markdown(f"<p style='text-align:center; color:#999; font-weight:bold;'>{d}</p>", unsafe_allow_html=True)

    # Cargar datos
    res = supabase.table("fichajes").select("*").eq("empleado_id", emp_id).execute()
    fichajes_df = pd.DataFrame(res.data) if res.data else pd.DataFrame()
    
    cal = calendar.monthcalendar(anio_actual, mes_actual)
    total_n, total_e, total_d = 0, 0, 0

    for semana in cal:
        cols = st.columns(7)
        for i, dia in enumerate(semana):
            if dia == 0: continue
            fecha_str = f"{anio_actual}-{mes_actual:02d}-{dia:02d}"
            
            # Buscar fichaje
            f = fichajes_df[fichajes_df['fecha_dia'] == fecha_str].iloc[0] if not fichajes_df.empty and not fichajes_df[fichajes_df['fecha_dia'] == fecha_str].empty else None
            
            with cols[i]:
                bg_dia = "#F9F9F9"
                texto_dia = f"<b>{dia}</b>"
                h_cont = 5.0 # Contrato base
                
                if f is not None:
                    n, e = f['horas_normales'], f['horas_extras']
                    deuda = round(h_cont - (n + e), 2) if (n+e) < h_cont else 0
                    total_n += n; total_e += e; total_d += deuda
                    
                    if f['tipo'] == 'vacaciones':
                        bg_dia = COLOR_VACACIONES_BG
                        texto_dia += f"<br><span style='color:{COLOR_VACACIONES_TXT}; font-weight:bold;'>☀️ VACS</span>"
                    else:
                        bg_dia = "#ABEBC6" if deuda == 0 else "#EDBB99"
                        texto_dia += f"<br><small>{f['hora_entrada']}-{f['hora_salida']}</small><br><small>{n}h N / {e}h E</small>"
                        if deuda > 0: texto_dia += f"<br><b style='color:red; font-size:10px;'>DEUDA {deuda}h</b>"

                st.markdown(f"<div class='dia-container' style='background-color:{bg_dia};'>{texto_dia}</div>", unsafe_allow_html=True)
                if st.button("📝", key=f"edit_{dia}"):
                    st.session_state.edit_dia = (dia, fecha_str)
                    st.rerun()

    # --- POPUP GESTIÓN ---
    if 'edit_dia' in st.session_state:
        dia_n, f_str = st.session_state.edit_dia
        st.markdown(f"### Gestionar {dia_n}/{mes_actual}")
        
        # Eliminar si existe
        if not fichajes_df.empty and not fichajes_df[fichajes_df['fecha_dia'] == f_str].empty:
            if st.button("🗑️ ELIMINAR", type="primary", use_container_width=True):
                supabase.table("fichajes").delete().eq("empleado_id", emp_id).eq("fecha_dia", f_str).execute()
                del st.session_state.edit_dia; st.rerun()
        else:
            with st.form("fichar"):
                c1, c2 = st.columns(2)
                h_i = c1.selectbox("Entrada", [f"{i:02d}:00" for i in range(24)], index=22)
                h_s = c2.selectbox("Salida", [f"{i:02d}:00" for i in range(24)], index=3)
                h_c = st.number_input("Horas Contrato", value=5.0)
                if st.form_submit_button("GUARDAR"):
                    norm, extra = calcular_duracion_turno(h_i, h_s), 0 # Simplificado
                    norm, extra = (h_c, round(calcular_duracion_turno(h_i, h_s)-h_c, 2)) if calcular_duracion_turno(h_i, h_s) > h_c else (calcular_duracion_turno(h_i, h_s), 0.0)
                    supabase.table("fichajes").insert({"empleado_id": emp_id, "fecha_dia": f_str, "hora_entrada": h_i, "hora_salida": h_s, "horas_normales": norm, "horas_extras": extra, "tipo": "trabajo"}).execute()
                    del st.session_state.edit_dia; st.rerun()
        if st.button("Cerrar"): del st.session_state.edit_dia; st.rerun()

    # --- RESUMEN FINAL ---
    st.write("##")
    neto_e = round(total_e - total_d, 2)
    total_ord = round(total_n + total_d, 2)
    txt_res = f"TOTAL MES: {round(total_n, 2)}h Realizadas + {round(total_d, 2)}h Debidas = {total_ord}h NORMALES | EXTRAS: {round(total_e, 2)}h - {total_d}h Deuda = {neto_e}h NETAS"
    st.markdown(f"<div class='resumen-footer'>{txt_res}</div>", unsafe_allow_html=True)
