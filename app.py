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

# --- LÓGICA DE TIEMPOS CORREGIDA ---
def calcular_tiempos_v2(h_ent, h_sal, h_con, es_ultimo_dia):
    fmt = "%H:%M"
    try:
        t_ent = datetime.strptime(h_ent, fmt)
        t_sal = datetime.strptime(h_sal, fmt)
        
        if t_sal <= t_ent:
            total_real = ((t_sal + timedelta(days=1)) - t_ent).total_seconds() / 3600
        else:
            total_real = (t_sal - t_ent).total_seconds() / 3600

        if es_ultimo_dia:
            t_limite = datetime.strptime("23:59", fmt) + timedelta(minutes=1)
            
            # Si el turno empieza de madrugada (ej: 00:30), todo es traspaso
            if t_ent < datetime.strptime("12:00", fmt):
                h_hoy = 0.0
                h_traspaso = total_real
            else:
                h_hoy = (t_limite - t_ent).total_seconds() / 3600
                h_traspaso = max(0.0, total_real - h_hoy)
            
            # ELIMINAMOS EL "DEBE" EN EL ÚLTIMO DÍA SI HAY TRASPASO
            # Si lo trabajado hoy + lo traspasado cubre el contrato, no se debe nada
            n = min(h_hoy, h_con)
            e = max(0.0, h_hoy - h_con)
            
            # Solo calculamos deuda si realmente no se trabajó ni para hoy ni para el traspaso
            if (h_hoy + h_traspaso) < h_con:
                d = h_con - (h_hoy + h_traspaso)
            else:
                d = 0.0
                
            return round(n, 1), round(e, 1), round(d, 1), round(h_traspaso, 1)
        else:
            n = min(total_real, h_con)
            e = max(0.0, total_real - h_con)
            d = max(0.0, h_con - total_real)
            return round(n, 1), round(e, 1), round(d, 1), 0.0
    except:
        return 0.0, 0.0, 0.0, 0.0

# --- NAVEGACIÓN ---
if 'page' not in st.session_state: st.session_state.page = 'inicio'
if 'm' not in st.session_state: st.session_state.m = datetime.now().month
if 'a' not in st.session_state: st.session_state.a = datetime.now().year

# --- PANTALLAS (INICIO Y ALEX) ---
if st.session_state.page == 'inicio':
    st.markdown("<h1 style='text-align:center;'>🍺 HORARIO DESASTRE</h1>", unsafe_allow_html=True)
    _, col_centro, _ = st.columns([0.5, 2, 0.5])
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
    tab1, tab2, tab3 = st.tabs(["📅 Horarios Base", "🌟 Días Estrella", "👁️ Ver Calendarios"])
    
    with tab1:
        dias_n = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        c1, c2 = st.columns(2)
        for eid, col, nom in [(2, c1, "JANIRA"), (3, c2, "IRIA")]:
            with col:
                st.subheader(nom)
                with st.form(f"fb_{eid}"):
                    hb = [st.number_input(f"{d}", value=5.0, step=0.5, key=f"b{eid}{i}") for i, d in enumerate(dias_n)]
                    if st.form_submit_button(f"GUARDAR {nom}"):
                        supabase.table("horarios_semanales").delete().eq("empleado_id", eid).execute()
                        for i, v in enumerate(hb):
                            supabase.table("horarios_semanales").insert({"empleado_id": eid, "dia_semana": i, "hora_inicio": str(v)}).execute()
                        st.success("Guardado")
    with tab2:
        st.subheader("Día Estrella ★")
        with st.form("fs"):
            e_id = st.selectbox("Empleado", [2, 3], format_func=lambda x: "Janira" if x==2 else "Iria")
            f_star = st.date_input("Fecha")
            h_star = st.number_input("Horas Contrato", value=8.0, step=0.5)
            if st.form_submit_button("FIJAR ESTRELLA"):
                supabase.table("dias_especiales").upsert({"empleado_id": e_id, "fecha": str(f_star), "horas_contrato": h_star}).execute()
                st.success("Guardado")
    with tab3:
        cv1, cv2 = st.columns(2)
        if cv1.button("CALENDARIO JANIRA", use_container_width=True):
            st.session_state.page = 'calendario'; st.session_state.user = 'Alex'; st.session_state.emp_id = 2; st.rerun()
        if cv2.button("CALENDARIO IRIA", use_container_width=True):
            st.session_state.page = 'calendario'; st.session_state.user = 'Alex'; st.session_state.emp_id = 3; st.rerun()

# --- PANTALLA CALENDARIO ---
elif st.session_state.page == 'calendario':
    es_alex = (st.session_state.user == 'Alex')
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
    if st.button("🏠"): st.session_state.page = 'inicio'; st.rerun()

    # Traspaso anterior
    f_ant = datetime(st.session_state.a, st.session_state.m, 1) - timedelta(days=1)
    r_ant = supabase.table("fichajes").select("*").eq("empleado_id", id_t).eq("fecha_dia", f_ant.strftime("%Y-%m-%d")).execute()
    trasp_recibido = 0.0
    if r_ant.data:
        fa = r_ant.data[0]
        re_a = supabase.table("dias_especiales").select("*").eq("empleado_id", id_t).eq("fecha", f_ant.strftime("%Y-%m-%d")).execute()
        ha = float(re_a.data[0]['horas_contrato']) if re_a.data else 5.0
        _, _, _, trasp_recibido = calcular_tiempos_v2(fa['hora_entrada'], fa['hora_salida'], ha, True)
    
    if trasp_recibido > 0:
        st.markdown(f"<div class='info-corte'>📅 Sumadas **{trasp_recibido}h** de la noche del mes pasado.</div>", unsafe_allow_html=True)

    r_f = supabase.table("fichajes").select("*").eq("empleado_id", id_t).gte("fecha_dia", f"{st.session_state.a}-{st.session_state.m:02d}-01").lte("fecha_dia", f"{st.session_state.a}-{st.session_state.m:02d}-{calendar.monthrange(st.session_state.a, st.session_state.m)[1]}").execute()
    df_f = pd.DataFrame(r_f.data) if r_f.data else pd.DataFrame()
    r_s = supabase.table("horarios_semanales").select("*").eq("empleado_id", id_t).execute()
    base_h = {int(i['dia_semana']): float(i['hora_inicio']) for i in r_s.data}
    r_e = supabase.table("dias_especiales").select("*").eq("empleado_id", id_t).execute()
    df_e = pd.DataFrame(r_e.data) if r_e.data else pd.DataFrame()

    total_n, total_e, total_d, trasp_enviado = 0.0, 0.0, 0.0, 0.0
    cal = calendar.monthcalendar(st.session_state.a, st.session_state.m)
    ult_dia = calendar.monthrange(st.session_state.a, st.session_state.m)[1]

    for sem in cal:
        cols = st.columns(7)
        for i, dia in enumerate(sem):
            if dia == 0: continue
            fs = f"{st.session_state.a}-{st.session_state.m:02d}-{dia:02d}"
            esp = df_e[df_e['fecha'] == fs].iloc[0] if not df_e.empty and not df_e[df_e['fecha'] == fs].empty else None
            hc = float(esp['horas_contrato']) if esp is not None else base_h.get(datetime(st.session_state.a, st.session_state.m, dia).weekday(), 5.0)
            f = df_f[df_f['fecha_dia'] == fs].iloc[0].to_dict() if not df_f.empty and not df_f[df_f['fecha_dia'] == fs].empty else None
            
            with cols[i]:
                txt = f"<b>{dia}{' ★' if esp is not None else ''}</b>"
                bg = "white"
                if f:
                    es_u = (dia == ult_dia)
                    n, e, d, tr = calcular_tiempos_v2(f['hora_entrada'], f['hora_salida'], hc, es_u)
                    total_n += n; total_e += e; total_d += d
                    if es_u: trasp_enviado = tr
                    
                    # Color azul para el día 31 si hay traspaso, o colores normales
                    bg = "#AED6F1" if (es_u and tr > 0) else ("#F5B041" if d > 0 else ("#D4EFDF" if e == 0 else "#FADBD8"))
                    txt += f"<br><small>{f['hora_entrada']}-{f['hora_salida']}</small><br>{n}N / {e}E"
                    if d > 0: txt += f"<br><b style='color:#C0392B;'>{d}h DEBE</b>"
                    if es_u and tr > 0: txt += f"<br><b style='color:#1B4F72;'>➔ {tr}h ENERO</b>"

                st.markdown(f"<div class='dia-caja' style='background-color:{bg};'>{txt}</div>", unsafe_allow_html=True)
                if not es_alex and st.button("📝", key=f"f{dia}"):
                    st.session_state.fichar = (fs, hc, f); st.rerun()

    # RESUMEN FINAL
    st.markdown("---")
    real = round(total_n + trasp_recibido, 1)
    st.markdown(f"""<div class='resumen-pie'>
        TOTAL MES: {real}h Realizadas + {total_d}h Debidas = {round(real + total_d, 1)}h NORMALES<br>
        EXTRAS: {total_e}h Brutas - {total_d}h Debidas = {round(total_e - total_d, 1)}h NETAS
    </div>""", unsafe_allow_html=True)

    if 'fichar' in st.session_state and not es_alex:
        fd, hc, fa = st.session_state.fichar
        with st.form("ff"):
            st.write(f"Día {fd} (Contrato {hc}h)")
            en = st.text_input("Entrada", fa['hora_entrada'] if fa else "22:00")
            sa = st.text_input("Salida", fa['hora_salida'] if fa else "03:00")
            if st.form_submit_button("GUARDAR"):
                supabase.table("fichajes").delete().eq("empleado_id", id_t).eq("fecha_dia", fd).execute()
                supabase.table("fichajes").insert({"empleado_id": id_t, "fecha_dia": fd, "hora_entrada": en, "hora_salida": sa}).execute()
                del st.session_state.fichar; st.rerun()
            if st.form_submit_button("BORRAR"):
                supabase.table("fichajes").delete().eq("empleado_id", id_t).eq("fecha_dia", fd).execute()
                del st.session_state.fichar; st.rerun()
