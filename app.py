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
    .big-button button {{
        height: 120px !important;
        font-size: 30px !important;
        margin-bottom: 25px !important;
        border: 4px solid #5D6D7E !important;
        border-radius: 20px !important;
    }}
    .stButton>button, div[data-testid="stFormSubmitButton"]>button {{
        color: black !important;
        background-color: white !important;
        border: 2px solid #5D6D7E !important;
        border-radius: 12px;
        font-weight: bold !important;
    }}
    .dia-caja {{
        border: 1px solid #7FB3D5;
        padding: 8px;
        border-radius: 8px;
        text-align: center;
        min-height: 110px;
        background-color: white;
        color: black;
    }}
    .resumen-pie {{
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        border: 3px solid #5D6D7E;
        text-align: center;
        font-size: 22px;
        color: black;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE CÁLCULO ---
def calcular_tiempos_exactos(h_ent, h_sal, h_contrato_decimal):
    fmt = "%H:%M"
    try:
        t1 = datetime.strptime(h_ent, fmt)
        t2 = datetime.strptime(h_sal, fmt)
        if t2 <= t1: t2 += timedelta(days=1)
        
        horas_trabajadas = (t2 - t1).total_seconds() / 3600
        contrato = float(h_contrato_decimal)
        
        if horas_trabajadas >= contrato:
            n, e, d = contrato, horas_trabajadas - contrato, 0.0
        else:
            n, e, d = horas_trabajadas, 0.0, contrato - horas_trabajadas
            
        return round(n, 2), round(e, 2), round(d, 2)
    except:
        return 0.0, 0.0, 0.0

# --- NAVEGACIÓN ---
if 'page' not in st.session_state: st.session_state.page = 'inicio'
if 'm' not in st.session_state: st.session_state.m = datetime.now().month
if 'a' not in st.session_state: st.session_state.a = datetime.now().year

# --- PANTALLAS ---
if st.session_state.page == 'inicio':
    st.markdown("<h1 style='text-align:center;'>🍺 HORARIO DESASTRE</h1>", unsafe_allow_html=True)
    _, col_centro, _ = st.columns([0.3, 2.4, 0.3])
    with col_centro:
        st.markdown('<div class="big-button">', unsafe_allow_html=True)
        if st.button("🧔 PERFIL ALEX", key="alx", use_container_width=True): 
            st.session_state.page = 'menu_alex'; st.rerun()
        if st.button("👩‍🦰 PERFIL JANIRA", key="jan", use_container_width=True):
            st.session_state.page = 'calendario'; st.session_state.user = 'Janira'; st.session_state.emp_id = 2; st.rerun()
        if st.button("👩‍🦳 PERFIL IRIA", key="iri", use_container_width=True):
            st.session_state.page = 'calendario'; st.session_state.user = 'Iria'; st.session_state.emp_id = 3; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == 'menu_alex':
    st.markdown(f"<style>.stApp {{ background-color: {COLOR_ALEX}; }}</style>", unsafe_allow_html=True)
    if st.button("◀ VOLVER"): st.session_state.page = 'inicio'; st.rerun()
    st.title("⚙️ Gestión de Alex")
    dias_n = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    cj, ci = st.columns(2)
    with cj:
        st.subheader("👩‍🦰 JANIRA")
        with st.form("fj"):
            hj = [st.number_input(f"{d}", value=5.0, step=0.1, key=f"j{i}") for i, d in enumerate(dias_n)]
            if st.form_submit_button("GUARDAR JANIRA"):
                for i, v in enumerate(hj):
                    supabase.table("horarios_semanales").upsert({"empleado_id": 2, "dia_semana": i, "hora_inicio": str(v)}).execute()
                st.success("Guardado")
    with ci:
        st.subheader("👩‍🦳 IRIA")
        with st.form("fi"):
            hi = [st.number_input(f"{d}", value=5.0, step=0.1, key=f"i{i}") for i, d in enumerate(dias_n)]
            if st.form_submit_button("GUARDAR IRIA"):
                for i, v in enumerate(hi):
                    supabase.table("horarios_semanales").upsert({"empleado_id": 3, "dia_semana": i, "hora_inicio": str(v)}).execute()
                st.success("Guardado")

elif st.session_state.page == 'calendario':
    id_t = st.session_state.emp_id
    st.markdown(f"<style>.stApp {{ background-color: {COLOR_JANI if id_t==2 else COLOR_IRIA}; }}</style>", unsafe_allow_html=True)
    
    # Navegación
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

    # Cargar datos
    res_f = supabase.table("fichajes").select("*").eq("empleado_id", id_t).execute()
    df_f = pd.DataFrame(res_f.data) if res_f.data else pd.DataFrame()
    res_s = supabase.table("horarios_semanales").select("*").eq("empleado_id", id_t).execute()
    base_h = {int(i['dia_semana']): float(i['hora_inicio']) for i in res_s.data}

    total_n, total_e, total_d = 0.0, 0.0, 0.0
    cal = calendar.monthcalendar(st.session_state.a, st.session_state.m)
    cols_h = st.columns(7)
    for i, d in enumerate(["LUN", "MAR", "MIE", "JUE", "VIE", "SAB", "DOM"]): cols_h[i].write(f"**{d}**")

    for sem in cal:
        cols = st.columns(7)
        for i, dia in enumerate(sem):
            if dia == 0: continue
            f_s = f"{st.session_state.a}-{st.session_state.m:02d}-{dia:02d}"
            f_dt = datetime(st.session_state.a, st.session_state.m, dia)
            h_con = base_h.get(f_dt.weekday(), 5.0)
            
            # Buscar fichaje existente
            f_row = df_f[df_f['fecha_dia'] == f_s]
            f = f_row.iloc[0].to_dict() if not f_row.empty else None
            
            with cols[i]:
                c_bg = "white"
                txt = f"<b>{dia}</b>"
                if f:
                    n, e, d = calcular_tiempos_exactos(f['hora_entrada'], f['hora_salida'], h_con)
                    total_n += n; total_e += e; total_d += d
                    c_bg = "#D4EFDF" if e == 0 else "#FADBD8"
                    txt += f"<br><small>{f['hora_entrada']}-{f['hora_salida']}</small><br>{round(n,1)}N/{round(e,1)}E"
                    if d > 0: txt += f"<br><b style='color:red; font-size:10px;'>-{round(d,1)}h</b>"
                
                st.markdown(f"<div class='dia-caja' style='background-color:{c_bg};'>{txt}</div>", unsafe_allow_html=True)
                if st.button("📝", key=f"btn{dia}"):
                    st.session_state.fichar = (f_s, h_con, f)
                    st.rerun()

    # Formulario
    if 'fichar' in st.session_state:
        f_dia, h_c, f_act = st.session_state.fichar
        st.write(f"### Gestionar día {f_dia}")
        
        with st.form("form_fichaje"):
            # Arreglo de la línea que fallaba:
            ent_def = f_act['hora_entrada'] if f_act else "22:00"
            sal_def = f_act['hora_salida'] if f_act else "03:00"
            
            ent = st.text_input("Hora Entrada", ent_def)
            sal = st.text_input("Hora Salida", sal_def)
            
            c1, c2 = st.columns(2)
            btn_save = c1.form_submit_button("💾 GUARDAR")
            btn_del = c2.form_submit_button("🗑️ BORRAR")

            if btn_save:
                n, e, d = calcular_tiempos_exactos(ent, sal, h_c)
                supabase.table("fichajes").delete().eq("empleado_id", id_t).eq("fecha_dia", f_dia).execute()
                supabase.table("fichajes").insert({
                    "empleado_id": id_t, "fecha_dia": f_dia, "hora_entrada": ent, 
                    "hora_salida": sal, "horas_normales": n, "horas_extras": e
                }).execute()
                del st.session_state.fichar; st.rerun()
                
            if btn_del:
                supabase.table("fichajes").delete().eq("empleado_id", id_t).eq("fecha_dia", f_dia).execute()
                del st.session_state.fichar; st.rerun()
        
        if st.button("Cancelar"):
            del st.session_state.fichar; st.rerun()

    st.markdown(f"""<div class='resumen-pie'>
        <b>TOTAL {calendar.month_name[st.session_state.m].upper()}:</b><br>
        {round(total_n, 1)}h Normales | {round(total_e, 1)}h Extras | <span style='color:red;'>Deuda: {round(total_d, 1)}h</span>
    </div>""", unsafe_allow_html=True)
