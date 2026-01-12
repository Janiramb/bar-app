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

# --- PALETA PASTEL REFINADA ---
COLOR_FONDO_BASE = "#E8F8F5"   # Verde agua muy suave
COLOR_ALEX_PASTEL = "#FADBD8"  # Rojo/Rosa pastel
COLOR_JANI_PASTEL = "#FCF3CF"  # Amarillo mostaza muy suave
COLOR_IRIA_PASTEL = "#EBDEF0"  # Morado/Lila pastel
COLOR_VERDE_FICHAJE = "#D4EFDF" # Verde pastel para días hechos

# --- ESTILOS ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: {COLOR_FONDO_BASE}; }}
    .stButton>button {{
        color: black !important;
        border: 1px solid #999 !important;
        border-radius: 12px;
        font-weight: bold !important;
    }}
    .dia-caja {{
        border: 1px solid #ddd;
        padding: 8px;
        border-radius: 10px;
        text-align: center;
        min-height: 100px;
        background-color: white;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- NAVEGACIÓN ---
if 'page' not in st.session_state: st.session_state.page = 'inicio'
if 'mes_ver' not in st.session_state: st.session_state.mes_ver = datetime.now().month

# --- PANTALLA 1: INICIO ---
if st.session_state.page == 'inicio':
    st.markdown("<h1 style='text-align:center; color:#5D6D7E;'>🍺 HORARIO DESASTRE 🍺</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.write("##")
        st.markdown(f'<style>div[row-id="alx"] button {{background-color: {COLOR_ALEX_PASTEL} !important;}}</style>', unsafe_allow_html=True)
        if st.button("🧔 PERFIL ALEX", key="alx", use_container_width=True): 
            st.session_state.page = 'menu_alex'; st.rerun()
        
        st.write("")
        st.markdown(f'<style>div[row-id="jan"] button {{background-color: {COLOR_JANI_PASTEL} !important;}}</style>', unsafe_allow_html=True)
        if st.button("👩‍🦰 PERFIL JANIRA", key="jan", use_container_width=True):
            st.session_state.page = 'calendario'; st.session_state.user = 'Janira'; st.session_state.emp_id = 2; st.rerun()
        
        st.write("")
        st.markdown(f'<style>div[row-id="iri"] button {{background-color: {COLOR_IRIA_PASTEL} !important;}}</style>', unsafe_allow_html=True)
        if st.button("👩‍🦳 PERFIL IRIA", key="iri", use_container_width=True):
            st.session_state.page = 'calendario'; st.session_state.user = 'Iria'; st.session_state.emp_id = 3; st.rerun()

# --- PANTALLA 2: MENU ALEX ---
elif st.session_state.page == 'menu_alex':
    st.markdown(f"<style>.stApp {{ background-color: {COLOR_ALEX_PASTEL}; }}</style>", unsafe_allow_html=True)
    if st.button("◀ VOLVER"): st.session_state.page = 'inicio'; st.rerun()
    st.title("⚙️ Configuración de Alex")
    
    col_izq, col_der = st.columns(2)
    
    with col_izq:
        st.subheader("📅 Horarios Base Semanales")
        st.write("Define las horas por defecto para cada día.")
        with st.form("horarios_base"):
            emp = st.selectbox("Empleado", [2, 3], format_func=lambda x: "Janira" if x==2 else "Iria")
            dia = st.selectbox("Día de la semana", range(7), format_func=lambda x: ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"][x])
            horas = st.number_input("Horas contrato", value=5.0, step=0.5)
            if st.form_submit_button("Guardar/Modificar Horario"):
                # Guardamos en la tabla de horarios_semanales
                supabase.table("horarios_semanales").upsert({"empleado_id": emp, "dia_semana": dia, "hora_inicio": str(horas)}).execute()
                st.success("Horario base actualizado.")

    with col_der:
        st.subheader("🌟 Días Especiales")
        with st.form("dias_esp"):
            emp_e = st.selectbox("Empleado", [2, 3], format_func=lambda x: "Janira" if x==2 else "Iria", key="e2")
            fec_e = st.date_input("Fecha concreta")
            hor_e = st.number_input("Horas para ese día", value=8.0)
            if st.form_submit_button("Añadir Estrella ★"):
                supabase.table("dias_especiales").insert({"empleado_id": emp_e, "fecha": str(fec_e), "horas_contrato": hor_e}).execute()
                st.success("Día especial guardado.")

    st.divider()
    st.write("### 👁️ Consultar Calendarios")
    if st.button("Ver JANIRA", use_container_width=True): 
        st.session_state.page = 'calendario'; st.session_state.user = 'Alex'; st.session_state.ver_id = 2; st.rerun()
    if st.button("Ver IRIA", use_container_width=True): 
        st.session_state.page = 'calendario'; st.session_state.user = 'Alex'; st.session_state.ver_id = 3; st.rerun()

# --- PANTALLA 3: CALENDARIO ---
elif st.session_state.page == 'calendario':
    es_alex = (st.session_state.user == 'Alex')
    id_trab = st.session_state.ver_id if es_alex else st.session_state.emp_id
    nombre_v = "Janira" if id_trab == 2 else "Iria"
    
    # Color de fondo según perfil
    bg_cal = COLOR_JANI_PASTEL if id_trab == 2 else COLOR_IRIA_PASTEL
    st.markdown(f"<style>.stApp {{ background-color: {bg_cal}; }}</style>", unsafe_allow_html=True)

    if st.button("🏠 INICIO"): st.session_state.page = 'inicio'; st.rerun()
    st.markdown(f"<h2 style='text-align:center;'>Horario de {nombre_v.upper()}</h2>", unsafe_allow_html=True)

    # Cargar todos los datos necesarios
    res_f = supabase.table("fichajes").select("*").eq("empleado_id", id_trab).execute()
    df_f = pd.DataFrame(res_f.data) if res_f.data else pd.DataFrame()
    
    res_s = supabase.table("horarios_semanales").select("*").eq("empleado_id", id_trab).execute()
    dict_base = {int(i['dia_semana']): float(i['hora_inicio']) for i in res_s.data} if res_s.data else {}

    res_e = supabase.table("dias_especiales").select("*").eq("empleado_id", id_trab).execute()
    df_e = pd.DataFrame(res_e.data) if res_e.data else pd.DataFrame()

    # Dibujar Calendario
    hoy = datetime.now()
    cal = calendar.monthcalendar(hoy.year, st.session_state.mes_ver)
    
    cols_h = st.columns(7)
    for i, d in enumerate(["LUN", "MAR", "MIE", "JUE", "VIE", "SAB", "DOM"]): cols_h[i].write(f"**{d}**")

    for semana in cal:
        cols = st.columns(7)
        for i, dia in enumerate(semana):
            if dia == 0: continue
            fecha_str = f"{hoy.year}-{st.session_state.mes_ver:02d}-{dia:02d}"
            fecha_dt = datetime(hoy.year, st.session_state.mes_ver, dia)
            
            # Buscar info del día
            f = df_f[df_f['fecha_dia'] == fecha_str].iloc[0] if not df_f.empty and not df_f[df_f['fecha_dia'] == fecha_str].empty else None
            esp = df_e[df_e['fecha'] == fecha_str].iloc[0] if not df_e.empty and not df_e[df_e['fecha'] == fecha_str].empty else None
            h_contrato_dia = esp['horas_contrato'] if esp is not None else dict_base.get(fecha_dt.weekday(), 5.0)

            with cols[i]:
                c_bg = "white"
                txt = f"<b>{dia}{' ★' if esp is not None else ''}</b>"
                if f is not None:
                    c_bg = COLOR_VERDE_FICHAJE
                    txt += f"<br><small>{f['hora_entrada']}-{f['hora_salida']}</small><br><b style='font-size:10px;'>{f['horas_normales']}N/{f['horas_extras']}E</b>"
                
                st.markdown(f"<div class='dia-caja' style='background-color:{c_bg};'>{txt}</div>", unsafe_allow_html=True)
                if not es_alex:
                    if st.button("📝", key=f"ed_{dia}"):
                        st.session_state.fichar = (fecha_str, h_contrato_dia)
                        st.rerun()

    # Formulario Fichar
    if 'fichar' in st.session_state and not es_alex:
        f_s, h_c = st.session_state.fichar
        with st.expander(f"Fichar {f_s} (Contrato: {h_c}h)", expanded=True):
            h_i = st.text_input("Entrada", "22:00")
            h_o = st.text_input("Salida", "03:00")
            if st.button("GUARDAR"):
                # Aquí iría tu lógica de cálculo de horas basada en h_c
                supabase.table("fichajes").insert({"empleado_id": id_trab, "fecha_dia": f_s, "hora_entrada": h_i, "hora_salida": h_o, "horas_normales": h_c, "horas_extras": 0.0}).execute()
                del st.session_state.fichar; st.rerun()
