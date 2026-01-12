import streamlit as st
from supabase import create_client, Client
from datetime import datetime, timedelta
import calendar
import pandas as pd

# --- CONFIGURACIÓN VISUAL (Tus colores exactos) ---
COLOR_FONDO_GENERAL = "#D5F5E3" 
COLOR_ALEX_BG = "#F2D7D5"      
COLOR_JANI_BG = "#FEF9E7"      
COLOR_IRIA_BG = "#F4ECF7"      
COLOR_VACACIONES_BG = "#A2D9CE"
COLOR_FALTA_BG = "#F1948A"
COLOR_ALEX_TXT = "#C0392B"
COLOR_JANI_TXT = "#D4AC0D"
COLOR_IRIA_TXT = "#8E44AD"
COLOR_BTN_GUARDAR = "#ABEBC6"
COLOR_BTN_ELIMINAR = "#E74C3C"

st.set_page_config(page_title="Horario Desastre", page_icon="🍺", layout="wide")

# --- CONEXIÓN ---
url = "https://kljizxbakvzytmaxqodw.supabase.co"
key = "sb_publishable_aV6LrJVsVo2a_129xBbNdw_TSO_7pDz"
supabase = create_client(url, key)

IDS = {"Alex": 1, "Janira": 2, "Iria": 3}

# --- ESTILOS CSS PERSONALIZADOS ---
def aplicar_estilo(bg_color):
    st.markdown(f"""
        <style>
        .stApp {{ background-color: {bg_color}; }}
        .stButton>button {{ border-radius: 8px; font-weight: bold; border: 1px solid #ccc; }}
        .dia-caja {{
            border: 1px solid #ddd;
            padding: 5px;
            border-radius: 5px;
            background-color: #F9F9F9;
            min-height: 90px;
            text-align: center;
        }}
        .resumen-caja {{
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            border: 2px solid #2C3E50;
        }}
        </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE NAVEGACIÓN ---
if 'page' not in st.session_state: st.session_state.page = 'inicio'
if 'emp_id' not in st.session_state: st.session_state.emp_id = None

def ir_a(pagina, emp_id=None):
    st.session_state.page = pagina
    if emp_id: st.session_state.emp_id = emp_id
    st.rerun()

# --- PANTALLA 1: INICIO ---
if st.session_state.page == 'inicio':
    aplicar_estilo(COLOR_FONDO_GENERAL)
    st.markdown("<h1 style='text-align: center; color: #555; font-size: 45px; font-weight: bold;'>🍺 HORARIO DESASTRE 🍺</h1>", unsafe_allow_html=True)
    st.write("##")
    
    col_c, col_b, col_a = st.columns([1, 2, 1])
    with col_b:
        if st.button("ALEX", use_container_width=True): ir_a('menu_alex', 1)
        st.write("")
        if st.button("JANIRA", use_container_width=True): ir_a('calendario', 2)
        st.write("")
        if st.button("IRIA", use_container_width=True): ir_a('calendario', 3)
        st.write("##")
        if st.button("❌ CERRAR APP", type="primary", use_container_width=True): st.stop()

# --- PANTALLA 2: MENU ALEX ---
elif st.session_state.page == 'menu_alex':
    aplicar_estilo(COLOR_ALEX_BG)
    if st.button("◀ VOLVER"): ir_a('inicio')
    st.markdown(f"<h1 style='text-align: center; color: {COLOR_ALEX_TXT};'>PANEL DE CONSULTA</h1>", unsafe_allow_html=True)
    
    st.write("##")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("HORARIO JANIRA", use_container_width=True): ir_a('calendario', 2)
        st.write("")
        if st.button("HORARIO IRIA", use_container_width=True): ir_a('calendario', 3)

# --- PANTALLA 3: CALENDARIO ---
elif st.session_state.page == 'calendario':
    emp_id = st.session_state.emp_id
    nombre = "Janira" if emp_id == 2 else "Iria"
    bg = COLOR_JANI_BG if emp_id == 2 else COLOR_IRIA_BG
    txt_c = COLOR_JANI_TXT if emp_id == 2 else COLOR_IRIA_TXT
    
    aplicar_estilo(bg)
    
    # Header navegación
    col_v, col_m, col_n = st.columns([1, 3, 1])
    with col_v:
        if st.button("◀ VOLVER"): ir_a('menu_alex' if st.session_state.emp_id == 1 else 'inicio')
    
    # Selector de mes
    hoy = datetime.now()
    with col_m:
        mes_sel = st.selectbox("", calendar.month_name[1:], index=hoy.month-1)
        mes = list(calendar.month_name).index(mes_sel)
        st.markdown(f"<h2 style='text-align: center; color: {txt_c};'>{nombre.upper()} - {mes_sel.upper()}</h2>", unsafe_allow_html=True)

    # Datos de Supabase
    res = supabase.table("fichajes").select("*").eq("empleado_id", emp_id).execute()
    fichajes_df = pd.DataFrame(res.data) if res.data else pd.DataFrame()
    
    # Dibujar Cuadrícula
    dias_semana = ["LUN", "MAR", "MIE", "JUE", "VIE", "SAB", "DOM"]
    cols_header = st.columns(7)
    for i, d in enumerate(dias_semana): cols_header[i].markdown(f"**{d}**")

    cal = calendar.monthcalendar(hoy.year, mes)
    total_n, total_e, total_d = 0, 0, 0

    for semana in cal:
        cols = st.columns(7)
        for i, dia in enumerate(semana):
            if dia == 0: continue
            fecha_str = f"{hoy.year}-{mes:02d}-{dia:02d}"
            
            # Buscar fichaje
            f = None
            if not fichajes_df.empty:
                match = fichajes_df[fichajes_df['fecha_dia'] == fecha_str]
                if not match.empty: f = match.iloc[0]

            with cols[i]:
                # Estilo de la celda según el tipo
                estilo_dia = "background-color: white;"
                contenido = f"<b>{dia}</b>"
                
                if f is not None:
                    total_n += f['horas_normales']
                    total_e += f['horas_extras']
                    if f['tipo'] == 'vacaciones':
                        estilo_dia = f"background-color: {COLOR_VACACIONES_BG}; color: white;"
                        contenido += "<br><small>☀️ VACS</small>"
                    else:
                        estilo_dia = "background-color: #ABEBC6;" if f['horas_extras'] == 0 else "background-color: #FADBD8;"
                        contenido += f"<br><small>{f['hora_entrada']}-{f['hora_salida']}</small>"

                st.markdown(f"<div class='dia-caja' style='{estilo_dia}'>{contenido}</div>", unsafe_allow_html=True)
                if st.button("📝", key=f"edit_{dia}"):
                    st.session_state.edit_dia = (dia, fecha_str)
                    st.rerun()

    # --- ZONA DE GESTIÓN (Al pulsar el botón del día) ---
    if 'edit_dia' in st.session_state:
        dia_n, fecha_s = st.session_state.edit_dia
        st.divider()
        st.subheader(f"Gestión del día {dia_n}")
        
        # Si ya hay fichaje -> BOTÓN ELIMINAR
        hay_fichaje = not fichajes_df[fichajes_df['fecha_dia'] == fecha_s].empty if not fichajes_df.empty else False
        
        if hay_fichaje:
            if st.button("🗑️ ELIMINAR TURNO", type="primary", use_container_width=True):
                supabase.table("fichajes").delete().eq("empleado_id", emp_id).eq("fecha_dia", fecha_s).execute()
                del st.session_state.edit_dia
                st.rerun()
        else:
            # Si no hay -> FORMULARIO GUARDAR
            with st.form("fichar"):
                c1, c2 = st.columns(2)
                h_e = c1.selectbox("Entrada", [f"{i:02d}:00" for i in range(24)], index=22)
                h_s = c2.selectbox("Salida", [f"{i:02d}:00" for i in range(24)], index=3)
                contrato = st.number_input("Horas Contrato", value=5.0)
                
                col_b1, col_b2 = st.columns(2)
                if col_b1.form_submit_button("💾 GUARDAR"):
                    # Cálculo de horas (puedes añadir tu función aquí)
                    # Por ahora lo simplificamos para el ejemplo
                    supabase.table("fichajes").insert({
                        "empleado_id": emp_id, "fecha_dia": fecha_s, "hora_entrada": h_e,
                        "hora_salida": h_s, "horas_normales": contrato, "horas_extras": 0.0, "tipo": "trabajo"
                    }).execute()
                    del st.session_state.edit_dia
                    st.rerun()
                if col_b2.form_submit_button("🏖️ VACACIONES"):
                    supabase.table("fichajes").insert({
                        "empleado_id": emp_id, "fecha_dia": fecha_s, "hora_entrada": "00:00",
                        "hora_salida": "00:00", "horas_normales": contrato, "horas_extras": 0.0, "tipo": "vacaciones"
                    }).execute()
                    del st.session_state.edit_dia
                    st.rerun()
        
        if st.button("Cerrar"):
            del st.session_state.edit_dia
            st.rerun()

    # --- RESUMEN FINAL (Igual que el tuyo) ---
    st.write("##")
    total_m = round(total_n, 2)
    st.markdown(f"""
        <div class='resumen-caja'>
            <h4>TOTAL MES: {total_m}h Realizadas | EXTRAS: {round(total_e, 2)}h</h4>
        </div>
    """, unsafe_allow_html=True)
