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
    .big-button button {{ height: 120px !important; font-size: 30px !important; border-radius: 20px !important; border: 4px solid #5D6D7E !important; }}
    .stButton>button, div[data-testid="stFormSubmitButton"]>button {{ color: black !important; background-color: white !important; border: 2px solid #5D6D7E !important; font-weight: bold !important; }}
    .dia-caja {{ border: 1px solid #7FB3D5; padding: 8px; border-radius: 8px; text-align: center; min-height: 110px; background-color: white; color: black; }}
    .resumen-pie {{ background-color: white; padding: 20px; border-radius: 15px; border: 3px solid #5D6D7E; text-align: center; font-size: 20px; color: black; }}
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE TIEMPOS Y CORTE DE MES ---
def calcular_y_repartir_tiempos(fecha_str, h_ent, h_sal, h_contrato, emp_id):
    fmt = "%H:%M"
    t1 = datetime.strptime(h_ent, fmt)
    t2 = datetime.strptime(h_sal, fmt)
    fecha_dt = datetime.strptime(fecha_str, "%Y-%m-%d")
    
    es_noche = t2 <= t1
    if es_noche:
        t2 += timedelta(days=1)
    
    # Horas totales de este turno
    total_h = (t2 - t1).total_seconds() / 3600
    
    # Si cruza la medianoche y es el último día del mes
    ultimo_dia_mes = calendar.monthrange(fecha_dt.year, fecha_dt.month)[1]
    
    if es_noche and fecha_dt.day == ultimo_dia_mes:
        # Horas antes de las 00:00 (se quedan en este mes)
        t_medianoche = datetime.strptime("23:59", "%H:%M") + timedelta(minutes=1)
        t_medianoche = t_medianoche.replace(year=t1.year, month=t1.month, day=t1.day)
        h_este_mes = (t_medianoche - t1).total_seconds() / 3600
        
        # Horas después de las 00:00 (van al mes siguiente)
        h_prox_mes = total_h - h_este_mes
        fecha_sig = (fecha_dt + timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Guardar resto en el día 1 del mes siguiente
        supabase.table("fichajes").insert({
            "empleado_id": emp_id, "fecha_dia": fecha_sig, "hora_entrada": "00:00",
            "hora_salida": h_sal, "horas_normales": h_prox_mes, "horas_extras": 0.0
        }).execute()
        
        total_h = h_este_mes # Solo procesamos lo de este mes para el registro actual

    n = min(total_h, h_contrato)
    e = max(0.0, total_h - h_contrato)
    return round(n, 2), round(e, 2)

# --- NAVEGACIÓN ---
if 'page' not in st.session_state: st.session_state.page = 'inicio'
if 'm' not in st.session_state: st.session_state.m = datetime.now().month
if 'a' not in st.session_state: st.session_state.a = datetime.now().year

# --- PANTALLA INICIO ---
if st.session_state.page == 'inicio':
    st.markdown("<h1 style='text-align:center; font-size: 55px;'>🍺 HORARIO DESASTRE</h1>", unsafe_allow_html=True)
    _, col_centro, _ = st.columns([0.3, 2.4, 0.3])
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
    st.title("⚙️ Panel de Alex")
    
    # Cargar horarios base actuales para que Alex vea lo que hay
    res_b = supabase.table("horarios_semanales").select("*").execute()
    db_base = pd.DataFrame(res_b.data) if res_b.data else pd.DataFrame()

    dias_n = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    cj, ci = st.columns(2)
    
    with cj:
        st.subheader("👩‍🦰 JANIRA (Base)")
        with st.form("fj"):
            hj = []
            for i, d in enumerate(dias_n):
                val_prev = 5.0
                if not db_base.empty:
                    match = db_base[(db_base['empleado_id']==2) & (db_base['dia_semana']==i)]
                    if not match.empty: val_prev = float(match.iloc[0]['hora_inicio'])
                hj.append(st.number_input(f"{d}", value=val_prev, key=f"j{i}"))
            if st.form_submit_button("GUARDAR JANIRA"):
                for i, v in enumerate(hj): supabase.table("horarios_semanales").upsert({"empleado_id": 2, "dia_semana": i, "hora_inicio": str(v)}).execute()
                st.success("Horario Janira Actualizado")

    with ci:
        st.subheader("👩‍🦳 IRIA (Base)")
        with st.form("fi"):
            hi = []
            for i, d in enumerate(dias_n):
                val_prev = 5.0
                if not db_base.empty:
                    match = db_base[(db_base['empleado_id']==3) & (db_base['dia_semana']==i)]
                    if not match.empty: val_prev = float(match.iloc[0]['hora_inicio'])
                hi.append(st.number_input(f"{d}", value=val_prev, key=f"i{i}"))
            if st.form_submit_button("GUARDAR IRIA"):
                for i, v in enumerate(hi): supabase.table("horarios_semanales").upsert({"empleado_id": 3, "dia_semana": i, "hora_inicio": str(v)}).execute()
                st.success("Horario Iria Actualizado")

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

    # Cargar datos
    res_f = supabase.table("fichajes").select("*").eq("empleado_id", id_t).execute()
    df_f = pd.DataFrame(res_f.data) if res_f.data else pd.DataFrame()
    res_s = supabase.table("horarios_semanales").select("*").eq("empleado_id", id_t).execute()
    base_h = {int(i['dia_semana']): float(i['hora_inicio']) for i in res_s.data}
    res_e = supabase.table("dias_especiales").select("*").eq("empleado_id", id_t).execute()
    df_e = pd.DataFrame(res_e.data) if res_e.data else pd.DataFrame()

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
            
            esp = df_e[df_e['fecha'] == f_s].iloc[0] if not df_e.empty and not df_e[df_e['fecha'] == f_s].empty else None
            h_con = esp['horas_contrato'] if esp is not None else base_h.get(f_dt.weekday(), 5.0)
            f_row = df_f[df_f['fecha_dia'] == f_s]
            f = f_row.iloc[0].to_dict() if not f_row.empty else None
            
            with cols[i]:
                c_bg = "white"
                txt = f"<b>{dia}{' ★' if esp is not None else ''}</b>"
                if f:
                    horas_dia = f['horas_normales'] + f['horas_extras']
                    deuda_dia = max(0.0, h_con - horas_dia)
                    total_n += f['horas_normales']; total_e += f['horas_extras']; total_d += deuda_dia
                    c_bg = "#D4EFDF" if f['horas_extras'] == 0 else "#FADBD8"
                    txt += f"<br><small>{f['hora_entrada']}-{f['hora_salida']}</small><br>{f['horas_normales']}N/{f['horas_extras']}E"
                    if deuda_dia > 0: txt += f"<br><b style='color:red; font-size:10px;'>-{round(deuda_dia,1)}h</b>"
                
                st.markdown(f"<div class='dia-caja' style='background-color:{c_bg};'>{txt}</div>", unsafe_allow_html=True)
                if st.button("📝", key=f"btn{dia}"): st.session_state.fichar = (f_s, h_con, f); st.rerun()

    if 'fichar' in st.session_state:
        f_dia, h_c, f_act = st.session_state.fichar
        with st.form("form_f"):
            ent = st.text_input("Entrada", f_act['hora_entrada'] if f_act else "22:00")
            sal = st.text_input("Salida", f_act['hora_salida'] if f_act else "03:00")
            c1, c2 = st.columns(2)
            if c1.form_submit_button("💾 GUARDAR"):
                n, e = calcular_y_repartir_tiempos(f_dia, ent, sal, h_c, id_t)
                supabase.table("fichajes").delete().eq("empleado_id", id_t).eq("fecha_dia", f_dia).execute()
                supabase.table("fichajes").insert({"empleado_id": id_t, "fecha_dia": f_dia, "hora_entrada": ent, "hora_salida": sal, "horas_normales": n, "horas_extras": e}).execute()
                del st.session_state.fichar; st.rerun()
            if c2.form_submit_button("🗑️ BORRAR"):
                supabase.table("fichajes").delete().eq("empleado_id", id_t).eq("fecha_dia", f_dia).execute()
                del st.session_state.fichar; st.rerun()
        if st.button("Cancelar"): del st.session_state.fichar; st.rerun()

    # --- RESUMEN FINAL MATEMÁTICO ---
    netas_extras = max(0.0, total_e - total_d)
    normales_ajustadas = total_n + (total_e - netas_extras)
    
    st.markdown(f"""<div class='resumen-pie'>
        TOTALES MES: {round(normales_ajustadas, 2)}h Normales | 
        EXTRAS NETAS: {round(netas_extras, 2)}h | 
        <span style='color:red;'>Deuda compensada: {round(total_d, 2)}h</span>
    </div>""", unsafe_allow_html=True)
