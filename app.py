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
    .big-button button {{ height: 100px !important; font-size: 25px !important; border-radius: 20px !important; border: 4px solid #5D6D7E !important; }}
    .stButton>button, div[data-testid="stFormSubmitButton"]>button {{ color: black !important; background-color: white !important; border: 2px solid #5D6D7E !important; font-weight: bold !important; }}
    .dia-caja {{ border: 1px solid #7FB3D5; padding: 10px; border-radius: 10px; text-align: center; min-height: 125px; background-color: white; color: black; }}
    .info-corte {{ background-color: #D6EAF8; padding: 15px; border-radius: 10px; border: 2px solid #3498DB; text-align: center; margin-bottom: 15px; font-size: 18px; color: #1B4F72; }}
    .resumen-pie {{ background-color: white; padding: 20px; border-radius: 15px; border: 3px solid #5D6D7E; text-align: center; font-size: 20px; font-weight: bold; color: #2C3E50; }}
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE TIEMPOS MEJORADA ---
def calcular_tiempos_v2(h_ent, h_sal, h_con, es_ultimo_dia):
    fmt = "%H:%M"
    try:
        t_ent = datetime.strptime(h_ent, fmt)
        t_sal = datetime.strptime(h_sal, fmt)
        
        # Caso: Pasa de las 00:00
        pasa_medianoche = t_sal <= t_ent
        
        if not pasa_medianoche:
            total_h = (t_sal - t_ent).total_seconds() / 3600
            h_hoy = total_h
            h_traspaso = 0.0
        else:
            # Horas hasta las 00:00
            t_medianoche = datetime.strptime("23:59", fmt) + timedelta(minutes=1)
            h_hoy = (t_medianoche - t_ent).total_seconds() / 3600
            # Horas después de las 00:00
            h_traspaso = (t_sal - datetime.strptime("00:00", fmt)).total_seconds() / 3600

        # Si NO es el último día, sumamos todo hoy
        if not es_ultimo_dia:
            total_final = h_hoy + h_traspaso
            h_traspaso = 0.0
        else:
            # Si ES último día, solo cuenta h_hoy para este mes
            total_final = h_hoy

        n = min(total_final, h_con)
        e = max(0.0, total_final - h_con)
        d = max(0.0, h_con - total_final)
        
        return round(n, 1), round(e, 1), round(d, 1), round(h_traspaso, 1)
    except:
        return 0.0, 0.0, 0.0, 0.0

# --- NAVEGACIÓN ---
if 'page' not in st.session_state: st.session_state.page = 'inicio'
if 'm' not in st.session_state: st.session_state.m = datetime.now().month
if 'a' not in st.session_state: st.session_state.a = datetime.now().year

# --- LÓGICA DE PANTALLAS (INICIO Y ALEX SE MANTIENEN IGUAL) ---
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

elif st.session_state.page == 'menu_alex':
    st.markdown(f"<style>.stApp {{ background-color: {COLOR_ALEX}; }}</style>", unsafe_allow_html=True)
    if st.button("◀ VOLVER"): st.session_state.page = 'inicio'; st.rerun()
    st.title("⚙️ Gestión de Alex")
    tab1, tab2, tab3 = st.tabs(["📅 Horarios Base", "🌟 Días Estrella", "👁️ Ver Calendarios"])
    
    with tab1:
        # Gestión de horarios base (sin cambios)
        st.info("Configura las horas de contrato estándar por día.")
        res_b = supabase.table("horarios_semanales").select("*").execute()
        db_base = pd.DataFrame(res_b.data) if res_b.data else pd.DataFrame()
        dias_n = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        cj, ci = st.columns(2)
        with cj:
            st.subheader("👩‍🦰 JANIRA")
            with st.form("fj"):
                hj = [st.number_input(f"Base {d}", value=5.0, step=0.5, key=f"j{i}") for i, d in enumerate(dias_n)]
                if st.form_submit_button("ACTUALIZAR JANIRA"):
                    supabase.table("horarios_semanales").delete().eq("empleado_id", 2).execute()
                    for i, v in enumerate(hj): supabase.table("horarios_semanales").insert({"empleado_id": 2, "dia_semana": i, "hora_inicio": str(v)}).execute()
                    st.rerun()
        with ci:
            st.subheader("👩‍🦳 IRIA")
            with st.form("fi"):
                hi = [st.number_input(f"Base {d}", value=5.0, step=0.5, key=f"i{i}") for i, d in enumerate(dias_n)]
                if st.form_submit_button("ACTUALIZAR IRIA"):
                    supabase.table("horarios_semanales").delete().eq("empleado_id", 3).execute()
                    for i, v in enumerate(hi): supabase.table("horarios_semanales").insert({"empleado_id": 3, "dia_semana": i, "hora_inicio": str(v)}).execute()
                    st.rerun()

    with tab2:
        st.subheader("Añadir Día Estrella ★")
        st.write("El valor introducido aquí anulará el horario base de ese día.")
        with st.form("f_star"):
            e_id = st.selectbox("Empleado", [2, 3], format_func=lambda x: "Janira" if x==2 else "Iria")
            f_star = st.date_input("Fecha Especial")
            h_star = st.number_input("Horas Contrato para este día", value=8.0, step=0.5)
            if st.form_submit_button("ESTABLECER DÍA ESTRELLA"):
                supabase.table("dias_especiales").upsert({"empleado_id": e_id, "fecha": str(f_star), "horas_contrato": h_star}).execute()
                st.success("Estrella guardada correctamente")

    with tab3:
        st.subheader("👁️ Visualizar Calendarios")
        c_v1, c_v2 = st.columns(2)
        if c_v1.button("Ver Calendario JANIRA", use_container_width=True):
            st.session_state.page = 'calendario'; st.session_state.user = 'Alex'; st.session_state.emp_id = 2; st.rerun()
        if c_v2.button("Ver Calendario IRIA", use_container_width=True):
            st.session_state.page = 'calendario'; st.session_state.user = 'Alex'; st.session_state.emp_id = 3; st.rerun()

elif st.session_state.page == 'calendario':
    es_alex = (st.session_state.user == 'Alex')
    id_t = st.session_state.emp_id
    st.markdown(f"<style>.stApp {{ background-color: {COLOR_JANI if id_t==2 else COLOR_IRIA}; }}</style>", unsafe_allow_html=True)
    
    # Cabecera Navegación
    c1, c2, c3 = st.columns([1, 2, 1])
    if c1.button("◀ MES ANTERIOR"):
        st.session_state.m -= 1
        if st.session_state.m < 1: st.session_state.m = 12; st.session_state.a -= 1
        st.rerun()
    if c3.button("MES SIGUIENTE ▶"):
        st.session_state.m += 1
        if st.session_state.m > 12: st.session_state.m = 1; st.session_state.a += 1
        st.rerun()
    with c2: st.markdown(f"<h2 style='text-align:center;'>{calendar.month_name[st.session_state.m].upper()} {st.session_state.a}</h2>", unsafe_allow_html=True)
    if st.button("🏠 VOLVER AL MENÚ"): st.session_state.page = 'inicio'; st.rerun()

    # --- CÁLCULO TRASPASO MES ANTERIOR ---
    fecha_ayer = datetime(st.session_state.a, st.session_state.m, 1) - timedelta(days=1)
    res_ayer = supabase.table("fichajes").select("*").eq("empleado_id", id_t).eq("fecha_dia", fecha_ayer.strftime("%Y-%m-%d")).execute()
    traspaso_recibido = 0.0
    
    if res_ayer.data:
        f_ayer = res_ayer.data[0]
        # Mirar si ayer fue estrella para saber su contrato
        res_e_ayer = supabase.table("dias_especiales").select("*").eq("empleado_id", id_t).eq("fecha", fecha_ayer.strftime("%Y-%m-%d")).execute()
        if res_e_ayer.data:
            h_con_ayer = float(res_e_ayer.data[0]['horas_contrato'])
        else:
            res_s_ayer = supabase.table("horarios_semanales").select("*").eq("empleado_id", id_t).eq("dia_semana", fecha_ayer.weekday()).execute()
            h_con_ayer = float(res_s_ayer.data[0]['hora_inicio']) if res_s_ayer.data else 5.0
        
        _, _, _, traspaso_recibido = calcular_tiempos_v2(f_ayer['hora_entrada'], f_ayer['hora_salida'], h_con_ayer, True)
    
    if traspaso_recibido > 0: 
        st.markdown(f"<div class='info-corte'>📅 Tienes **{traspaso_recibido}h** procedentes de la noche del mes anterior.</div>", unsafe_allow_html=True)

    # Carga de datos
    r_f = supabase.table("fichajes").select("*").eq("empleado_id", id_t).gte("fecha_dia", f"{st.session_state.a}-{st.session_state.m:02d}-01").lte("fecha_dia", f"{st.session_state.a}-{st.session_state.m:02d}-{calendar.monthrange(st.session_state.a, st.session_state.m)[1]}").execute()
    df_f = pd.DataFrame(r_f.data) if r_f.data else pd.DataFrame(columns=['fecha_dia', 'hora_entrada', 'hora_salida'])
    
    r_s = supabase.table("horarios_semanales").select("*").eq("empleado_id", id_t).execute()
    base_h = {int(i['dia_semana']): float(i['hora_inicio']) for i in r_s.data}
    
    r_e = supabase.table("dias_especiales").select("*").eq("empleado_id", id_t).execute()
    df_e = pd.DataFrame(r_e.data) if r_e.data else pd.DataFrame(columns=['fecha', 'horas_contrato'])

    total_n_mes, total_e_mes, total_d_mes, traspaso_enviado = 0.0, 0.0, 0.0, 0.0
    cal = calendar.monthcalendar(st.session_state.a, st.session_state.m)
    ult_dia_m = calendar.monthrange(st.session_state.a, st.session_state.m)[1]

    for sem in cal:
        cols = st.columns(7)
        for i, dia in enumerate(sem):
            if dia == 0: continue
            f_s = f"{st.session_state.a}-{st.session_state.m:02d}-{dia:02d}"
            
            # PRIORIDAD: Día estrella sobre base semanal
            esp = df_e[df_e['fecha'] == f_s].iloc[0] if not df_e.empty and not df_e[df_e['fecha'] == f_s].empty else None
            h_con = esp['horas_contrato'] if esp is not None else base_h.get(datetime(st.session_state.a, st.session_state.m, dia).weekday(), 5.0)
            
            f = df_f[df_f['fecha_dia'] == f_s].iloc[0].to_dict() if not df_f.empty and not df_f[df_f['fecha_dia'] == f_s].empty else None
            
            with cols[i]:
                txt = f"<b>{dia}{' ★' if esp is not None else ''}</b>"
                c_bg = "white"
                if f:
                    es_ultimo = (dia == ult_dia_m)
                    n, e, d, trasp = calcular_tiempos_v2(f['hora_entrada'], f['hora_salida'], h_con, es_ultimo)
                    
                    total_n_mes += n
                    total_e_mes += e
                    total_d_mes += d
                    if es_ultimo: traspaso_enviado = trasp
                    
                    if es_ultimo and trasp > 0:
                        c_bg = "#AED6F1"
                        txt += f"<br><small>{f['hora_entrada']}-{f['hora_salida']}</small><br>➜ {trasp}h a Prox Mes"
                    else:
                        c_bg = "#F5B041" if d > 0 else ("#D4EFDF" if e == 0 else "#FADBD8")
                        txt += f"<br><small>{f['hora_entrada']}-{f['hora_salida']}</small><br>{n}N / {e}E"
                        if d > 0: txt += f"<br><b style='color:#C0392B;'>DEBES {d}h</b>"
                
                st.markdown(f"<div class='dia-caja' style='background-color:{c_bg};'>{txt}</div>", unsafe_allow_html=True)
                if not es_alex and st.button("📝", key=f"d{dia}"): st.session_state.fichar = (f_s, h_con, f); st.rerun()

    # --- RESUMEN FINAL ---
    st.markdown("---")
    # Las horas normales totales son las realizadas este mes + las que vinieron del pasado
    res_real = round(total_n_mes + traspaso_recibido, 1)
    st.markdown(f"""<div class='resumen-pie'>
        TOTAL MES: {res_real}h Realizadas + {total_d_mes}h Debidas = {round(res_real + total_d_mes, 1)}h NORMALES<br>
        EXTRAS: {total_e_mes}h Brutas - {total_d_mes}h Debidas = {round(total_e_mes - total_d_mes, 1)}h NETAS
    </div>""", unsafe_allow_html=True)
    
    if traspaso_enviado > 0:
        st.info(f"👉 Nota: Se han excluido {traspaso_enviado}h de este resumen porque pertenecen al mes siguiente.")

    # Formulario de fichaje (sin cambios)
    if 'fichar' in st.session_state and not es_alex:
        f_dia, h_c, f_act = st.session_state.fichar
        with st.form("form_f"):
            st.write(f"Fichaje para el día {f_dia} (Contrato: {h_c}h)")
            ent = st.text_input("Entrada (HH:MM)", f_act['hora_entrada'] if f_act else "22:00")
            sal = st.text_input("Salida (HH:MM)", f_act['hora_salida'] if f_act else "03:00")
            c1, c2 = st.columns(2)
            if c1.form_submit_button("💾 GUARDAR"):
                supabase.table("fichajes").delete().eq("empleado_id", id_t).eq("fecha_dia", f_dia).execute()
                supabase.table("fichajes").insert({"empleado_id": id_t, "fecha_dia": f_dia, "hora_entrada": ent, "hora_salida": sal}).execute()
                del st.session_state.fichar; st.rerun()
            if c2.form_submit_button("🗑️ BORRAR"):
                supabase.table("fichajes").delete().eq("empleado_id", id_t).eq("fecha_dia", f_dia).execute()
                del st.session_state.fichar; st.rerun()
