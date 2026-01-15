# --- DATOS DEL MES Y CÁLCULOS ---
    total_realizadas_mes = 0.0  # Horas físicas trabajadas dentro del mes
    total_contrato_mes = 0.0    # Suma de todas las horas que debería trabajar según contrato
    total_extras_brutas = 0.0   # Horas que superan el contrato diario
    traspaso_saliente = 0.0     # Horas que pasan al mes siguiente (post-medianoche)

    # ... (Dentro del bucle de semanas y días) ...
    for sem in cal:
        cols = st.columns(7)
        for i, dia in enumerate(sem):
            if dia == 0: continue
            f_s = f"{st.session_state.a}-{st.session_state.m:02d}-{dia:02d}"
            esp = df_e[df_e['fecha'] == f_s].iloc[0] if not df_e.empty and not df_e[df_e['fecha'] == f_s].empty else None
            h_con = esp['horas_contrato'] if esp is not None else base_h.get(datetime(st.session_state.a, st.session_state.m, dia).weekday(), 5.0)
            
            # Acumulamos el contrato total del mes
            total_contrato_mes += h_con
            
            f = df_f[df_f['fecha_dia'] == f_s].iloc[0].to_dict() if not df_f.empty and not df_f[df_f['fecha_dia'] == f_s].empty else None
            
            with cols[i]:
                txt = f"<b>{dia}{' ★' if esp is not None else ''}</b>"
                c_bg = "white"
                if f:
                    n, b, d, trasp = calcular_tiempos_finales(f['hora_entrada'], f['hora_salida'], h_con, dia == ult_dia_m)
                    
                    # n son las horas que computan para el contrato de este día
                    total_realizadas_mes += n 
                    total_extras_brutas += b
                    traspaso_saliente += trasp
                    
                    if dia == ult_dia_m and trasp > 0:
                        c_bg = "#AED6F1"
                        txt += f"<br><small>{f['hora_entrada']}-{f['hora_salida']}</small><br>Corte: {n}h<br><b style='color:#1B4F72;'>➔ {trasp}h SIG</b>"
                    else:
                        c_bg = "#F5B041" if d > 0 else ("#D4EFDF" if b == 0 else "#FADBD8")
                        txt += f"<br><small>{f['hora_entrada']}-{f['hora_salida']}</small><br>{n}N/{b}E"
                        if d > 0: txt += f"<br><b style='color:#C0392B;'>DEBES {d}h</b>"
                else:
                    # Si no hay fichaje, se deben todas las horas de ese contrato
                    pass 

                st.markdown(f"<div class='dia-caja' style='background-color:{c_bg};'>{txt}</div>", unsafe_allow_html=True)
                if not es_alex and st.button("📝", key=f"d{dia}"): st.session_state.fichar = (f_s, h_con, f); st.rerun()

    # --- LÓGICA DE COMPENSACIÓN REAL ---
    # 1. Sumamos lo que viene del mes pasado a las realizadas
    realizadas_con_traspaso = total_realizadas_mes + traspaso_recibido
    
    # 2. Calculamos la diferencia global del mes
    # Si realizadas < contrato, hay deuda.
    balance_normal = realizadas_con_traspaso - total_contrato_mes
    
    if balance_normal >= 0:
        # Ha cumplido el contrato: deuda es 0 y lo que sobra son extras netas
        deuda_final = 0.0
        extras_netas = total_extras_brutas + balance_normal
    else:
        # No ha llegado al contrato: lo que falta es deuda.
        # Intentamos pagar esa deuda con las extras brutas que tenga
        deuda_pendiente = abs(balance_normal)
        if total_extras_brutas >= deuda_pendiente:
            deuda_final = 0.0
            extras_netas = total_extras_brutas - deuda_pendiente
        else:
            deuda_final = deuda_pendiente - total_extras_brutas
            extras_netas = 0.0

    # --- RESUMEN FINAL ---
    st.markdown("---")
    if traspaso_saliente > 0:
        st.info(f"📅 Se han detectado {traspaso_saliente}h que pasan al mes siguiente.")

    st.markdown(f"""
        <div class='resumen-pie'>
            CONTRATO MES: {round(total_contrato_mes, 1)}h | TRABAJADAS: {round(realizadas_con_traspaso, 1)}h<br>
            <b>RESULTADO: {round(deuda_final, 1)}h Debidas Finales | {round(extras_netas, 1)}h Extras Netas</b>
        </div>
    """, unsafe_allow_html=True)
