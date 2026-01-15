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
COLOR_FONDO_BASE = "#4AED5D"
COLOR_ALEX = "#FF4A38"
COLOR_JANI = "#FCD844"
COLOR_IRIA = " #BC7AFA"

# --- ESTILOS CSS ---
# --- ESTILOS CSS ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: {COLOR_FONDO_BASE}; }}
    .big-button button {{ height: 100px !important; font-size: 25px !important; border-radius: 20px !important; border: 4px solid #5D6D7E !important; }}
    .stButton>button, div[data-testid="stFormSubmitButton"]>button {{ color: black !important; background-color: white !important; border: 2px solid #5D6D7E !important; font-weight: bold !important; }}
    .dia-caja {{ border: 1px solid #7FB3D5; padding: 10px; border-radius: 10px; text-align: center; min-height: 125px; background-color: white; color: black; }}
    .resumen-pie {{ background-color: white; padding: 20px; border-radius: 15px; border: 3px solid #5D6D7E; text-align: center; font-size: 20px; font-weight: bold; color: #2C3E50; }}
    
    /* Estilos para Gestión Alex */
    .section-header {{ background-color: white; padding: 15px; border-radius: 10px; border-left: 10px solid #5D6D7E; margin-bottom: 20px; font-size: 24px; font-weight: bold; color: #2C3E50; }}

    /* --- NUEVOS ESTILOS PARA TABS NEGROS Y GRANDES --- */
    /* Pestaña seleccionada (activa) */
    button[data-baseweb="tab"][aria-selected="true"] {{
        color: black !important;
        border-bottom-color: black !important;
    }}

    /* Texto de todas las pestañas más grande */
    button[data-baseweb="tab"] p {{
        font-size: 25px !important;
        font-weight: bold !important;
    }}

    /* Color negro al pasar el ratón por encima */
    button[data-baseweb="tab"]:hover {{
        color: black !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE TIEMPOS MAESTRA ---
def calcular_tiempos_v2(h_ent, h_sal, h_con, es_ultimo_dia):
    fmt = "%H:%M"
    try:
        t_ent = datetime.strptime(h_ent, fmt)
        t_sal = datetime.strptime(h_sal, fmt)
        
        if t_sal <= t_ent:
            total_jornada = ((t_sal + timedelta(days=1)) - t_ent).total_seconds() / 3600
            t_limite = datetime.strptime("23:59", fmt) + timedelta(minutes=1)
            h_antes_12 = (t_limite - t_ent).total_seconds() / 3600
            h_despues_12 = total_jornada - h_antes_12
        else:
            total_jornada = (t_sal - t_ent).total_seconds() / 3600
            if t_ent < datetime.strptime("12:00", fmt):
                h_antes_12 = 0.0
                h_despues_12 = total_jornada
            else:
                h_antes_12 = total_jornada
                h_despues_12 = 0.0

        n_totales = min(total_jornada, h_con)
        e_totales = max(0.0, total_jornada - h_con)
        deuda = max(0.0, h_con - total_jornada)

        if es_ultimo_dia:
            n_dic = min(h_antes_12, n_totales)
            e_dic = max(0.0, h_antes_12 - n_totales)
            n_ene = n_totales - n_dic
            e_ene = e_totales - e_dic
            return round(n_dic, 1), round(e_dic, 1), round(deuda, 1), round(n_ene, 1), round(e_ene, 1)
        else:
            return round(n_totales, 1), round(e_totales, 1), round(deuda, 1), 0.0, 0.0
    except:
        return 0.0, 0.0, 0.0, 0.0, 0.0

# --- NAVEGACIÓN ---
if 'page' not in st.session_state: st.session_state.page = 'inicio'
if 'm' not in st.session_state: st.session_state.m = datetime.now().month
if 'a' not in st.session_state: st.session_state.a = datetime.now().year

# --- PANTALLA INICIO ---
if st.session_state.page == 'inicio':
    st.markdown("<h1 style='text-align:center;'>🍺 HORARIO DESASTRE</h1>", unsafe_allow_html=True)
    _, col_centro, _ = st.columns([0.5, 2, 0.5])
    with col_centro:
        st.markdown('<div class="big-button">', unsafe_allow_html=True)
        if st.button("ALEX", use_container_width=True): st.session_state.page = 'menu_alex'; st.rerun()
        if st.button("JANI", use_container_width=True):
            st.session_state.page = 'calendario'; st.session_state.user = 'Janira'; st.session_state.emp_id = 2; st.rerun()
        if st.button("IRIA", use_container_width=True):
            st.session_state.page = 'calendario'; st.session_state.user = 'Iria'; st.session_state.emp_id = 3; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- PANTALLA ALEX (GESTIÓN VISUAL GRANDE) ---
elif st.session_state.page == 'menu_alex':
    st.markdown(f"<style>.stApp {{ background-color: {COLOR_ALEX}; }}</style>", unsafe_allow_html=True)
    if st.button("◀ VOLVER AL INICIO"): st.session_state.page = 'inicio'; st.rerun()
    st.title("⚙️ PANEL DE CONTROL - ALEX")
    
    tab1, tab2, tab3 = st.tabs(["📅 HORARIOS BASE", "🌟 DÍAS ESTRELLA", "👁️ CALENDARIOS"])
    
    with tab1:
        st.markdown('<div class="section-header">📋 Horarios Semanales Vigentes</div>', unsafe_allow_html=True)
        res_b = supabase.table("horarios_semanales").select("*").execute()
        df_base = pd.DataFrame(res_b.data) if res_b.data else pd.DataFrame()
        dias_n = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        
        c1, c2 = st.columns(2)
        for eid, col, nom in [(2, c1, "JANI"), (3, c2, "IRIA")]:
            with col:
                st.subheader(nom)
                if not df_base.empty:
                    temp_df = df_base[df_base['empleado_id'] == eid].copy()
                    if not temp_df.empty:
                        temp_df['Día'] = temp_df['dia_semana'].apply(lambda x: dias_n[int(x)])
                        # Mostrar tabla más grande y limpia
                        st.table(temp_df.sort_values('dia_semana')[['Día', 'hora_inicio']].set_index('Día'))
                
                with st.expander(f"⚙️ ACTUALIZAR BASE DE {nom.split()[-1]}"):
                    with st.form(f"fb_{eid}"):
                        hb = [st.number_input(f"Horas {d}", value=5.0, step=0.5, key=f"b{eid}{i}") for i, d in enumerate(dias_n)]
                        if st.form_submit_button("GUARDAR NUEVO HORARIO"):
                            supabase.table("horarios_semanales").delete().eq("empleado_id", eid).execute()
                            for i, v in enumerate(hb): supabase.table("horarios_semanales").insert({"empleado_id": eid, "dia_semana": i, "hora_inicio": str(v)}).execute()
                            st.rerun()

    with tab2:
        st.markdown('<div class="section-header">⭐ Listado de Estrellas Activas</div>', unsafe_allow_html=True)
        res_e = supabase.table("dias_especiales").select("*").execute()
        if res_e.data:
            df_e_list = pd.DataFrame(res_e.data)
            df_e_list['Empleado'] = df_e_list['empleado_id'].apply(lambda x: "Janira" if x == 2 else "Iria")
            # Mostrar tabla grande con dataframe
            st.dataframe(df_e_list[['fecha', 'Empleado', 'horas_contrato']].sort_values('fecha', ascending=False), use_container_width=True, height=300)
            
            st.markdown("---")
            c_del1, c_del2 = st.columns([2, 1])
            with c_del1:
                del_id = st.selectbox("Selecciona una fecha para ELIMINAR:", df_e_list['fecha'].unique())
            with c_del2:
                if st.button("🗑️ ELIMINAR SELECCIONADA", use_container_width=True):
                    supabase.table("dias_especiales").delete().eq("fecha", del_id).execute()
                    st.rerun()
        else:
            st.info("No hay días estrella registrados actualmente.")

        st.markdown('<div class="section-header">➕ Registrar Nueva Estrella</div>', unsafe_allow_html=True)
        with st.form("fs_new"):
            c_new1, c_new2, c_new3 = st.columns(3)
            with c_new1: e_id = st.selectbox("Para quién:", [2, 3], format_func=lambda x: "Janira" if x==2 else "Iria")
            with c_new2: f_star = st.date_input("Qué día:")
            with c_new3: h_star = st.number_input("Horas de contrato ese día:", value=6.0, step=0.5)
            if st.form_submit_button("REGISTRAR DÍA ESTRELLA"):
                supabase.table("dias_especiales").upsert({"empleado_id": e_id, "fecha": str(f_star), "horas_contrato": h_star}).execute()
                st.success("¡Día estrella guardado!")
                st.rerun()

    with tab3:
        st.markdown('<div class="section-header">👁️ Acceso Rápido a Calendarios</div>', unsafe_allow_html=True)
        st.markdown('<div class="big-button">', unsafe_allow_html=True)
        cv1, cv2 = st.columns(2)
        if cv1.button("📅 VER MES JANIRA", use_container_width=True): st.session_state.page = 'calendario'; st.session_state.user = 'Alex'; st.session_state.emp_id = 2; st.rerun()
        if cv2.button("📅 VER MES IRIA", use_container_width=True): st.session_state.page = 'calendario'; st.session_state.user = 'Alex'; st.session_state.emp_id = 3; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

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
    if st.button("🏠 MENU"): st.session_state.page = 'inicio'; st.rerun()

    f_ant = datetime(st.session_state.a, st.session_state.m, 1) - timedelta(days=1)
    r_ant = supabase.table("fichajes").select("*").eq("empleado_id", id_t).eq("fecha_dia", f_ant.strftime("%Y-%m-%d")).execute()
    n_rec, e_rec = 0.0, 0.0
    if r_ant.data:
        fa = r_ant.data[0]
        re_a = supabase.table("dias_especiales").select("*").eq("empleado_id", id_t).eq("fecha", f_ant.strftime("%Y-%m-%d")).execute()
        ha = float(re_a.data[0]['horas_contrato']) if re_a.data else 5.0
        _, _, _, n_rec, e_rec = calcular_tiempos_v2(fa['hora_entrada'], fa['hora_salida'], ha, True)
    
    if (n_rec + e_rec) > 0:
        st.info(f"ℹ️ Recibidas del mes pasado: {n_rec}h Normales y {e_rec}h Extras")

    r_f = supabase.table("fichajes").select("*").eq("empleado_id", id_t).gte("fecha_dia", f"{st.session_state.a}-{st.session_state.m:02d}-01").lte("fecha_dia", f"{st.session_state.a}-{st.session_state.m:02d}-{calendar.monthrange(st.session_state.a, st.session_state.m)[1]}").execute()
    df_f = pd.DataFrame(r_f.data) if r_f.data else pd.DataFrame()
    base_h = {int(i['dia_semana']): float(i['hora_inicio']) for i in (supabase.table("horarios_semanales").select("*").eq("empleado_id", id_t).execute()).data}
    df_e = pd.DataFrame((supabase.table("dias_especiales").select("*").eq("empleado_id", id_t).execute()).data)

    t_n_dic, t_e_dic, t_d_dic = 0.0, 0.0, 0.0
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
                    nd, ed, dd, ne, ee = calcular_tiempos_v2(f['hora_entrada'], f['hora_salida'], hc, dia == ult_dia)
                    t_n_dic += nd; t_e_dic += ed; t_d_dic += dd
                    bg = "#AED6F1" if (dia == ult_dia and (ne+ee) > 0) else ("#F5B041" if dd > 0 else ("#D4EFDF" if ed == 0 else "#FADBD8"))
                    txt += f"<br><small>{f['hora_entrada']}-{f['hora_salida']}</small><br>{nd}N / {ed}E"
                    if dd > 0: txt += f"<br><b style='color:#C0392B;'>{dd}h DEBE</b>"
                    if dia == ult_dia and (ne+ee) > 0: txt += f"<br><b style='color:#1B4F72;'>➔ {ne}N + {ee}E</b>"

                st.markdown(f"<div class='dia-caja' style='background-color:{bg};'>{txt}</div>", unsafe_allow_html=True)
                if not es_alex and st.button("📝", key=f"f{dia}"): st.session_state.fichar = (fs, hc, f); st.rerun()

    st.markdown("---")
    r_n = round(t_n_dic + n_rec, 1)
    r_e = round(t_e_dic + e_rec, 1)
    st.markdown(f"""<div class='resumen-pie'>
        TOTAL MES: {r_n}h Realizadas + {t_d_dic}h Debidas = {round(r_n + t_d_dic, 1)}h NORMALES<br>
        EXTRAS: {r_e}h Brutas - {t_d_dic}h Debidas = {round(r_e - t_d_dic, 1)}h NETAS
    </div>""", unsafe_allow_html=True)

    if 'fichar' in st.session_state and not es_alex:
        fd, hc, fa = st.session_state.fichar
        with st.form("ff"):
            st.write(f"Día {fd} (Contrato {hc}h)")
            en = st.text_input("Entrada", fa['hora_entrada'] if fa else "21:30")
            sa = st.text_input("Salida", fa['hora_salida'] if fa else "06:30")
            if st.form_submit_button("GUARDAR"):
                supabase.table("fichajes").delete().eq("empleado_id", id_t).eq("fecha_dia", fd).execute()
                supabase.table("fichajes").insert({"empleado_id": id_t, "fecha_dia": fd, "hora_entrada": en, "hora_salida": sa}).execute()
                del st.session_state.fichar; st.rerun()
            if st.form_submit_button("BORRAR"):
                supabase.table("fichajes").delete().eq("empleado_id", id_t).eq("fecha_dia", fd).execute()
                del st.session_state.fichar; st.rerun()


