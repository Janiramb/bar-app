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

# --- COLORES ORIGINALES ---
COLORS = {
    "fondo": "#D5F5E3", "alex_bg": "#F2D7D5", "jani_bg": "#FEF9E7", "iria_bg": "#F4ECF7",
    "jani_btn": "#F9E79F", "iria_btn": "#D7BDE2", "alex_btn": "#E6B0AA",
    "txt_alex": "#C0392B", "txt_jani": "#D4AC0D", "txt_iria": "#8E44AD"
}

# --- ESTILOS (Arreglado el color del texto) ---
def aplicar_estilos(bg_color):
    st.markdown(f"""
        <style>
        .stApp {{ background-color: {bg_color}; }}
        .stButton>button {{
            color: black !important;
            font-weight: bold !important;
            border: 2px solid #555 !important;
            border-radius: 10px;
            height: 60px;
        }}
        .dia-caja {{
            border: 1px solid #ccc; padding: 10px; border-radius: 8px;
            text-align: center; min-height: 100px; background-color: white; color: black;
        }}
        .resumen {{
            background-color: white; padding: 15px; border-radius: 10px;
            border: 2px solid #2C3E50; text-align: center; font-weight: bold; color: black;
        }}
        </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE NAVEGACIÓN ---
if 'page' not in st.session_state: st.session_state.page = 'inicio'

# --- PANTALLA INICIO ---
if st.session_state.page == 'inicio':
    aplicar_estilos(COLORS["fondo"])
    st.markdown("<h1 style='text-align:center; color:#555;'>🍺 HORARIO DESASTRE 🍺</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.write("##")
        if st.button("ALEX (Jefe)", use_container_width=True): 
            st.session_state.page = 'menu_alex'; st.rerun()
        
        st.markdown(f'<style>div[row-id="j"] button {{background-color: {COLORS["jani_btn"]} !important;}}</style>', unsafe_allow_html=True)
        if st.button("JANIRA", key="j", use_container_width=True):
            st.session_state.page = 'calendario'; st.session_state.user = 'Janira'; st.session_state.emp_id = 2; st.rerun()
        
        st.markdown(f'<style>div[row-id="i"] button {{background-color: {COLORS["iria_btn"]} !important;}}</style>', unsafe_allow_html=True)
        if st.button("IRIA", key="i", use_container_width=True):
            st.session_state.page = 'calendario'; st.session_state.user = 'Iria'; st.session_state.emp_id = 3; st.rerun()

# --- PANTALLA MENU ALEX ---
elif st.session_state.page == 'menu_alex':
    aplicar_estilos(COLORS["alex_bg"])
    if st.button("◀ VOLVER"): st.session_state.page = 'inicio'; st.rerun()
    st.markdown(f"<h1 style='text-align:center; color:{COLORS['txt_alex']};'>PANEL DE CONTROL (ALEX)</h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Consultar Horarios", "⚙️ Configurar Contratos/Días"])
    
    with tab1:
        st.write("### Ver Fichajes de:")
        c1, c2 = st.columns(2)
        if c1.button("HORARIO JANIRA", use_container_width=True):
            st.session_state.page = 'calendario'; st.session_state.user = 'Alex'; st.session_state.ver_id = 2; st.rerun()
        if c2.button("HORARIO IRIA", use_container_width=True):
            st.session_state.page = 'calendario'; st.session_state.user = 'Alex'; st.session_state.ver_id = 3; st.rerun()

    with tab2:
        st.write("### Añadir Día Especial / Contrato")
        with st.form("config_alex"):
            emp = st.selectbox("Empleado", [2, 3], format_func=lambda x: "Janira" if x==2 else "Iria")
            fecha_esp = st.date_input("Fecha")
            horas_c = st.number_input("Horas Contrato para ese día", value=5.0)
            motivo = st.text_input("Motivo (Ej: Navidad, Refuerzo)")
            if st.form_submit_button("Añadir Día Especial"):
                supabase.table("dias_especiales").insert({"empleado_id": emp, "fecha": str(fecha_esp), "horas_contrato": horas_c, "motivo": motivo}).execute()
                st.success("Configuración guardada")

# --- PANTALLA CALENDARIO ---
elif st.session_state.page == 'calendario':
    es_alex = (st.session_state.user == 'Alex')
    emp_id = st.session_state.ver_id if es_alex else st.session_state.emp_id
    nombre_emp = "Janira" if emp_id == 2 else "Iria"
    bg = COLORS["alex_bg"] if es_alex else (COLORS["jani_bg"] if emp_id == 2 else COLORS["iria_bg"])
    
    aplicar_estilos(bg)
    if st.button("◀ VOLVER"): 
        st.session_state.page = 'menu_alex' if es_alex else 'inicio'; st.rerun()

    st.markdown(f"<h1 style='text-align:center;'>Calendario de {nombre_emp}</h1>", unsafe_allow_html=True)
    
    # Cargar Fichajes y Días Especiales
    res_f = supabase.table("fichajes").select("*").eq("empleado_id", emp_id).execute()
    f_df = pd.DataFrame(res_f.data) if res_f.data else pd.DataFrame()
    
    res_e = supabase.table("dias_especiales").select("*").eq("empleado_id", emp_id).execute()
    e_df = pd.DataFrame(res_e.data) if res_e.data else pd.DataFrame()

    hoy = datetime.now()
    cal = calendar.monthcalendar(hoy.year, hoy.month)
    
    cols_h = st.columns(7)
    for i, d in enumerate(["LUN", "MAR", "MIE", "JUE", "VIE", "SAB", "DOM"]): cols_h[i].write(f"**{d}**")

    for semana in cal:
        cols = st.columns(7)
        for i, dia in enumerate(semana):
            if dia == 0: continue
            f_str = f"{hoy.year}-{hoy.month:02d}-{dia:02d}"
            
            # Buscar info
            fichaje = f_df[f_df['fecha_dia'] == f_str].iloc[0] if not f_df.empty and not f_df[f_df['fecha_dia'] == f_str].empty else None
            especial = e_df[e_df['fecha'] == f_str].iloc[0] if not e_df.empty and not e_df[e_df['fecha'] == f_str].empty else None
            
            with cols[i]:
                color_celda = "white"
                info = f"<b>{dia}</b>"
                if especial is not None: info += " ★"; color_celda = "#FFF9C4"
                if fichaje is not None:
                    info += f"<br><small>{fichaje['hora_entrada']}-{fichaje['hora_salida']}</small>"
                    color_celda = "#ABEBC6" if fichaje['horas_extras'] == 0 else "#FADBD8"
                
                st.markdown(f"<div class='dia-caja' style='background-color:{color_celda};'>{info}</div>", unsafe_allow_html=True)
                
                # SOLO Janira o Iria ven el botón de editar
                if not es_alex:
                    if st.button("📝", key=f"ed_{dia}"):
                        st.session_state.edit_fichaje = f_str
                        st.rerun()

    # FORMULARIO PARA FICHAR (Solo para ellas)
    if 'edit_fichaje' in st.session_state and not es_alex:
        with st.expander(f"Fichar día {st.session_state.edit_fichaje}", expanded=True):
            c1, c2 = st.columns(2)
            h_in = c1.text_input("Entrada (HH:MM)", "22:00")
            h_out = c2.text_input("Salida (HH:MM)", "03:00")
            tipo = st.selectbox("Tipo", ["trabajo", "vacaciones"])
            if st.button("Guardar Fichaje"):
                supabase.table("fichajes").insert({"empleado_id": emp_id, "fecha_dia": st.session_state.edit_fichaje, "hora_entrada": h_in, "hora_salida": h_out, "horas_normales": 5.0, "horas_extras": 0.0, "tipo": tipo}).execute()
                del st.session_state.edit_fichaje; st.rerun()
            if st.button("🗑️ ELIMINAR"):
                supabase.table("fichajes").delete().eq("empleado_id", emp_id).eq("fecha_dia", st.session_state.edit_fichaje).execute()
                del st.session_state.edit_fichaje; st.rerun()
