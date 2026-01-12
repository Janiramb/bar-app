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

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #D5F5E3; }
    .stButton>button {
        color: black !important;
        background-color: white;
        border: 2px solid #555 !important;
        font-weight: bold !important;
    }
    .dia-caja {
        border: 1px solid #ccc;
        padding: 8px;
        border-radius: 8px;
        text-align: center;
        min-height: 85px;
        background-color: white;
        color: black;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN DE MEMORIA (Session State) ---
if 'page' not in st.session_state: st.session_state.page = 'inicio'
if 'mes_ver' not in st.session_state: st.session_state.mes_ver = datetime.now().month
if 'anio_ver' not in st.session_state: st.session_state.anio_ver = datetime.now().year

# --- PANTALLA 1: INICIO ---
if st.session_state.page == 'inicio':
    st.markdown("<h1 style='text-align:center;'>🍺 HORARIO DESASTRE 🍺</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("ALEX", use_container_width=True):
            st.session_state.page = 'menu_alex'; st.rerun()
        st.write("")
        if st.button("JANI", use_container_width=True):
            st.session_state.page = 'calendario'; st.session_state.user = 'Janira'; st.session_state.emp_id = 2; st.rerun()
        st.write("")
        if st.button("IRIA", use_container_width=True):
            st.session_state.page = 'calendario'; st.session_state.user = 'Iria'; st.session_state.emp_id = 3; st.rerun()

# --- PANTALLA 2: MENU ALEX ---
elif st.session_state.page == 'menu_alex':
    if st.button("◀ VOLVER"): st.session_state.page = 'inicio'; st.rerun()
    st.title("Panel de Control - Alex")
    tab1, tab2 = st.tabs(["📊 Consultar Horarios", "⚙️ Configurar Días"])
    with tab1:
        if st.button("Consultar a JANIRA"):
            st.session_state.page = 'calendario'; st.session_state.user = 'Alex'; st.session_state.ver_id = 2; st.rerun()
        if st.button("Consultar a IRIA"):
            st.session_state.page = 'calendario'; st.session_state.user = 'Alex'; st.session_state.ver_id = 3; st.rerun()
    with tab2:
        with st.form("esp"):
            e_id = st.selectbox("Empleado", [2, 3], format_func=lambda x: "Janira" if x==2 else "Iria")
            f_esp = st.date_input("Fecha")
            h_esp = st.number_input("Horas Contrato", value=5.0)
            if st.form_submit_button("Guardar"):
                supabase.table("dias_especiales").insert({"empleado_id": e_id, "fecha": str(f_esp), "horas_contrato": h_esp}).execute()
                st.success("Día guardado")

# --- PANTALLA 3: CALENDARIO (Con Cambio de Mes) ---
elif st.session_state.page == 'calendario':
    es_alex = (st.session_state.user == 'Alex')
    id_trab = st.session_state.ver_id if es_alex else st.session_state.emp_id
    nombre_v = "Janira" if id_trab == 2 else "Iria"

    # --- BARRA DE NAVEGACIÓN DE MES ---
    col_atras, col_mes, col_adelante = st.columns([1, 3, 1])
    
    with col_atras:
        if st.button("◀ Mes Anterior"):
            st.session_state.mes_ver -= 1
            if st.session_state.mes_ver < 1:
                st.session_state.mes_ver = 12
                st.session_state.anio_ver -= 1
            st.rerun()
            
    with col_mes:
        nombre_mes = calendar.month_name[st.session_state.mes_ver]
        st.markdown(f"<h2 style='text-align:center;'>{nombre_mes.upper()} {st.session_state.anio_ver}</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center;'>Horario de {nombre_v}</p>", unsafe_allow_html=True)

    with col_adelante:
        if st.button("Mes Siguiente ▶"):
            st.session_state.mes_ver += 1
            if st.session_state.mes_ver > 12:
                st.session_state.mes_ver = 1
                st.session_state.anio_ver += 1
            st.rerun()

    if st.button("🏠 INICIO"): st.session_state.page = 'inicio'; st.rerun()

    # Cargar datos del mes seleccionado
    res = supabase.table("fichajes").select("*").eq("empleado_id", id_trab).execute()
    df_f = pd.DataFrame(res.data) if res.data else pd.DataFrame()

    cal = calendar.monthcalendar(st.session_state.anio_ver, st.session_state.mes_ver)
    
    # Dibujar días de la semana
    semana_dias = ["LUN", "MAR", "MIE", "JUE", "VIE", "SAB", "DOM"]
    cols_h = st.columns(7)
    for i, d in enumerate(semana_dias): cols_h[i].write(f"**{d}**")

    for semana in cal:
        cols = st.columns(7)
        for i, dia in enumerate(semana):
            if dia == 0: continue
            fecha_s = f"{st.session_state.anio_ver}-{st.session_state.mes_ver:02d}-{dia:02d}"
            
            f = df_f[df_f['fecha_dia'] == fecha_s].iloc[0] if not df_f.empty and not df_f[df_f['fecha_dia'] == fecha_s].empty else None
            
            with cols[i]:
                color = "white"
                txt = f"<b>{dia}</b>"
                if f is not None:
                    color = "#ABEBC6" if f['tipo'] == 'trabajo' else "#AED6F1"
                    txt += f"<br><small>{f['hora_entrada']}-{f['hora_salida']}</small>"
                
                st.markdown(f"<div class='dia-caja' style='background-color:{color};'>{txt}</div>", unsafe_allow_html=True)
                
                if not es_alex:
                    if st.button("📝", key=f"btn_{dia}"):
                        st.session_state.fichar_dia = fecha_s
                        st.rerun()

    # Formulario para fichar
    if 'fichar_dia' in st.session_state and not es_alex:
        with st.expander(f"Gestionar día {st.session_state.fichar_dia}", expanded=True):
            h_i = st.text_input("Entrada", "22:00")
            h_o = st.text_input("Salida", "03:00")
            if st.button("Guardar Turno"):
                supabase.table("fichajes").insert({"empleado_id": id_trab, "fecha_dia": st.session_state.fichar_dia, "hora_entrada": h_i, "hora_salida": h_o, "horas_normales": 5.0, "horas_extras": 0.0, "tipo": "trabajo"}).execute()
                del st.session_state.fichar_dia; st.rerun()
            if st.button("🗑️ Eliminar"):
                supabase.table("fichajes").delete().eq("empleado_id", id_trab).eq("fecha_dia", st.session_state.fichar_dia).execute()
                del st.session_state.fichar_dia; st.rerun()
