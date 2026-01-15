import streamlit as st
from supabase import create_client
from datetime import datetime, timedelta
import calendar
import pandas as pd

# --- CONFIG ---
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

# --- CSS ---
st.markdown(f"""
<style>
.stApp {{ background-color: {COLOR_FONDO_BASE}; }}
.dia-caja {{ border:1px solid #7FB3D5; padding:10px; border-radius:10px; background:white; }}
.resumen-pie {{ background:white; padding:20px; border-radius:15px; border:3px solid #5D6D7E;
font-size:20px; font-weight:bold; text-align:center; }}
</style>
""", unsafe_allow_html=True)

# --- FUNCIÓN CLAVE ---
def calcular_tiempos_finales(h_ent, h_sal, h_con, es_ultimo_dia):
    fmt = "%H:%M"
    t1 = datetime.strptime(h_ent, fmt)
    t2 = datetime.strptime(h_sal, fmt)

    paso_medianoche = t2 <= t1
    if paso_medianoche:
        t2 += timedelta(days=1)

    total = (t2 - t1).total_seconds() / 3600

    if es_ultimo_dia and paso_medianoche:
        medianoche = (t1 + timedelta(days=1)).replace(hour=0, minute=0)
        h_mes = (medianoche - t1).total_seconds() / 3600
        h_sig = total - h_mes

        normales = min(h_mes, h_con)
        extras = max(0, h_mes - h_con)
        deuda = max(0, h_con - h_mes)

        return round(normales,1), round(extras,1), round(deuda,1), round(h_sig,1)

    normales = min(total, h_con)
    extras = max(0, total - h_con)
    deuda = max(0, h_con - total)

    return round(normales,1), round(extras,1), round(deuda,1), 0.0

# --- SESSION ---
if 'page' not in st.session_state: st.session_state.page = 'inicio'
if 'm' not in st.session_state: st.session_state.m = datetime.now().month
if 'a' not in st.session_state: st.session_state.a = datetime.now().year

# --- INICIO ---
if st.session_state.page == 'inicio':
    st.title("🍺 HORARIO DESASTRE")
    if st.button("🧔 ALEX"): st.session_state.page = 'menu_alex'; st.rerun()
    if st.button("👩‍🦰 JANIRA"):
        st.session_state.page = 'calendario'
        st.session_state.user = 'Janira'
        st.session_state.emp_id = 2
        st.rerun()
    if st.button("👩‍🦳 IRIA"):
        st.session_state.page = 'calendario'
        st.session_state.user = 'Iria'
        st.session_state.emp_id = 3
        st.rerun()

# --- CALENDARIO ---
elif st.session_state.page == 'calendario':

    id_t = st.session_state.emp_id
    es_alex = st.session_state.user == 'Alex'

    st.subheader(f"{calendar.month_name[st.session_state.m].upper()} {st.session_state.a}")

    # --- TRASPASO DEL MES ANTERIOR ---
    traspaso_recibido = 0.0
    fecha_ant = datetime(st.session_state.a, st.session_state.m, 1) - timedelta(days=1)

    res_ant = supabase.table("fichajes").select("*") \
        .eq("empleado_id", id_t) \
        .eq("fecha_dia", fecha_ant.strftime("%Y-%m-%d")).execute()

    if res_ant.data:
        f = res_ant.data[0]
        _, _, _, traspaso_recibido = calcular_tiempos_finales(
            f['hora_entrada'], f['hora_salida'], 5.0, True
        )

    if traspaso_recibido > 0:
        st.info(f"Tienes {traspaso_recibido}h correspondientes al mes anterior.")

    # --- DATOS ---
    res_f = supabase.table("fichajes").select("*") \
        .eq("empleado_id", id_t) \
        .gte("fecha_dia", f"{st.session_state.a}-{st.session_state.m:02d}-01") \
        .execute()

    df_f = pd.DataFrame(res_f.data) if res_f.data else pd.DataFrame()

    total_normales = 0.0
    total_extras = 0.0
    total_contrato = 0.0
    traspaso_saliente = 0.0

    ult_dia = calendar.monthrange(st.session_state.a, st.session_state.m)[1]

    for semana in calendar.monthcalendar(st.session_state.a, st.session_state.m):
        cols = st.columns(7)
        for i, dia in enumerate(semana):
            if dia == 0: continue

            fecha = f"{st.session_state.a}-{st.session_state.m:02d}-{dia:02d}"
            fich = df_f[df_f['fecha_dia'] == fecha]

            with cols[i]:
                txt = f"<b>{dia}</b>"
                bg = "white"

                total_contrato += 5.0

                if not fich.empty:
                    f = fich.iloc[0]
                    n, e, d, t = calcular_tiempos_finales(
                        f['hora_entrada'], f['hora_salida'], 5.0, dia == ult_dia
                    )

                    total_normales += n
                    total_extras += e
                    traspaso_saliente += t

                    txt += f"<br>{f['hora_entrada']} - {f['hora_salida']}"
                    txt += f"<br>{n}N / {e}E"

                    if dia == ult_dia and t > 0:
                        txt += f"<br>➜ {t}h SIG"
                        bg = "#AED6F1"
                    elif d > 0:
                        txt += f"<br><b>DEBES {d}h</b>"
                        bg = "#F5B7B1"
                    elif e > 0:
                        bg = "#FADBD8"
                    else:
                        bg = "#D4EFDF"

                st.markdown(
                    f"<div class='dia-caja' style='background:{bg};'>{txt}</div>",
                    unsafe_allow_html=True
                )

    # --- RESUMEN FINAL ---
    real_mes = total_normales + total_extras
    real_total = real_mes + traspaso_recibido
    balance = real_total - total_contrato

    if balance >= 0:
        deuda_final = 0.0
        extras_netas = total_extras + balance
    else:
        deuda = abs(balance)
        if total_extras >= deuda:
            deuda_final = 0.0
            extras_netas = total_extras - deuda
        else:
            deuda_final = deuda - total_extras
            extras_netas = 0.0

    st.markdown("---")
    st.markdown(f"""
    <div class='resumen-pie'>
    CONTRATO: {round(total_contrato,1)}h<br>
    TRABAJADAS: {round(real_total,1)}h<br>
    RESULTADO: {round(deuda_final,1)}h Debidas | {round(extras_netas,1)}h Extras
    </div>
    """, unsafe_allow_html=True)
