import streamlit as st
import datetime
import time
import uuid

# ======= Estilos globales (oculta header blanco y afina layout) =======
st.markdown("""
    <style>
    /* Ocultar completamente el header/menú/footer de Streamlit */
    header { visibility: hidden; }
    [data-testid="stHeader"] { display: none; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    /* Ajuste general del contenedor principal */
    .block-container { padding-top: 1rem; }

    /* Tipografías compactas para títulos */
    h1, h2, h3 { font-size: 1.2rem !important; }

    /* ====== Estilos de confirmación tipo Mercado Pago ====== */
    .mp-full {
        min-height: 88vh;  /* ocupa casi toda la pantalla */
        display: flex; align-items: center; justify-content: center;
    }
    .mp-card {
        width: min(520px, 92vw);
        background: #ffffff;
        border-radius: 16px;
        box-shadow: 0 8px 28px rgba(0,0,0,0.08);
        padding: 28px 24px;
        border: 1px solid rgba(0,0,0,0.06);
        text-align: center;
    }
    .mp-check {
        width: 82px; height: 82px; border-radius: 50%;
        background: #edf7f0; margin: 0 auto 16px auto; display: grid; place-items: center;
        border: 2px solid #2E7D32;
        animation: popIn 300ms ease-out;
    }
    .mp-check svg {
        width: 44px; height: 44px;
        stroke: #2E7D32; fill: none; stroke-width: 3px; stroke-linecap: round; stroke-linejoin: round;
        animation: draw 500ms ease-out forwards;
    }
    @keyframes popIn { 0% { transform: scale(0.9); opacity: 0; } 100% { transform: scale(1); opacity: 1; } }
    @keyframes draw { 0% { stroke-dasharray: 0 100; } 100% { stroke-dasharray: 100 0; } }

    .mp-title { font-size: 1.2rem; font-weight: 700; margin-bottom: 6px; }
    .mp-subtitle { color: #5f6368; font-size: 0.96rem; margin-bottom: 14px; }

    .mp-summary {
        text-align: left;
        background: #fafafa;
        border: 1px solid rgba(0,0,0,0.06);
        border-radius: 12px;
        padding: 12px 14px;
        margin: 14px 0 18px 0;
        font-size: 0.95rem;
        line-height: 1.35rem;
    }
    .mp-kv { display: flex; justify-content: space-between; gap: 12px; margin: 4px 0; }
    .mp-kv .k { color: #616161; }
    .mp-kv .v { font-weight: 600; text-align: right; }

    .mp-actions {
        display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 10px;
    }
    .mp-btn { border-radius: 10px; padding: 10px 14px; border: 1px solid rgba(0,0,0,0.08); }
    .mp-btn-primary { background: #2E7D32; color: white; border: none; }

    .mp-muted { color: #666; font-size: 0.9rem; margin-top: 10px; }
    </style>
""", unsafe_allow_html=True)

# ======= Inicialización de estado robusta =======
def init_state():
    if 'page' not in st.session_state:
        st.session_state.page = 'linea'
    if 'data' not in st.session_state:
        st.session_state.data = {}

def reset_to_home():
    # Limpiar y re-inicializar ambas claves para evitar AttributeError
    st.session_state.clear()
    st.session_state.page = 'linea'
    st.session_state.data = {}

init_state()

def go_to(page):
    st.session_state.page = page

st.title("App Registro de Eventos")

# Página: Seleccionar Línea
if st.session_state.page == "linea":
    st.header("Selecciona una línea")
    for num in [1, 2, 3]:
        if st.button(f"Línea {num}"):
            if 'data' not in st.session_state:
                st.session_state.data = {}
            st.session_state.data['linea'] = f"Línea {num}"
            go_to("user")

# Página: Seleccionar Usuario
elif st.session_state.page == "user":
    st.header("Selecciona tu usuario")
    user = st.selectbox("Usuario", ["", "usuario1", "usuario2", "usuario3"])
    if st.button("Continuar") and user:
        st.session_state.data['user'] = user
        go_to("motivo")

# Página: Seleccionar Motivo (actualizado con dropdown)
elif st.session_state.page == "motivo":
    st.header("Selecciona un motivo")
    motivos = [
        "CAMBIO DE LOTE",
        "ROTURA DE AMPOLLAS",
        "MAL CIERRE DE ESTUCHES",
        "OTROS (GENERAL)",
        "OTROS (CARGADORES)",
        "OTROS (ESTUCHADORA)",
        "CHUPETES",
        "OTROS (KETAN)",
        "BAJADA DE BLISTER",
        "PROBLEMA DE TRAZABILIDAD",
        "BAJADA PROSPECTOS",
        "ERROR SISTEMA LIXIS",
        "SISTEMA DE VISIÓN",
        "CODIFICADO WOLKE",
        "OTROS (BLISTERA)",
        "FUERA DE PASO OPERATIVO B",
        "FALTA DE INSUMOS DE DEPOSITO"
    ]
    selected_motivo = st.selectbox("Motivo", [""] + motivos)
    if selected_motivo and st.button("Continuar"):
        st.session_state.data['motivo'] = selected_motivo
        go_to("submotivo")

# Página: Seleccionar Submotivo
elif st.session_state.page == "submotivo":
    st.header("Selecciona un submotivo")
    for sub in ["Motor", "Sensor", "Panel"]:
        if st.button(sub):
            st.session_state.data['submotivo'] = sub
            go_to("componente")

# Página: Seleccionar Componente
elif st.session_state.page == "componente":
    st.header("Selecciona un componente")
    for comp in ["PLC", "Tornillo", "Interruptor"]:
        if st.button(comp):
            st.session_state.data['componente'] = comp
            go_to("tipo")

# Página: Tipo de Evento
elif st.session_state.page == "tipo":
    linea_txt = st.session_state.data.get('linea', 'Línea')
    st.header(f"Selecciona una opción para {linea_txt}")
    if st.button("Interrupción"):
        st.session_state.data["tipo"] = "interrupcion"
        go_to("form")
    if st.button("Novedad"):
        st.session_state.data["tipo"] = "novedad"
        go_to("form")

# Página: Formulario
elif st.session_state.page == "form":
    tipo = st.session_state.data.get("tipo", "interrupcion")
    linea_txt = st.session_state.data.get('linea', 'Línea')
    st.header(f"{tipo.title()} - {linea_txt}")
    st.markdown(
        f"**Motivo:** {st.session_state.data.get('motivo','-')} | "
        f"**Submotivo:** {st.session_state.data.get('submotivo','-')} | "
        f"**Componente:** {st.session_state.data.get('componente','-')}"
    )

    if tipo == "interrupcion":
        start_time_str = st.text_input("Hora de inicio (HH:MM)", placeholder="Ej: 08:30")
        end_time_str = st.text_input("Hora de fin (HH:MM)", placeholder="Ej: 09:15")
    else:
        start_time_str = end_time_str = None

    comentario = st.text_area("Describe el evento")

    if st.button("Confirmar"):
        minutos = None
        # Validación de horario si es interrupción
        if tipo == "interrupcion":
            try:
                start_dt = datetime.datetime.strptime(start_time_str, "%H:%M")
                end_dt = datetime.datetime.strptime(end_time_str, "%H:%M")
                minutos = int((end_dt - start_dt).total_seconds() / 60)
            except Exception:
                st.error("⛔ Formato de hora inválido. Usá HH:MM.")
                st.stop()

        # Generar ID de ticket simple (opcional)
        ticket_id = uuid.uuid4().hex[:8].upper()

        st.session_state.data.update({
            "start": start_time_str if tipo == "interrupcion" else None,
            "end": end_time_str if tipo == "interrupcion" else None,
            "minutos": minutos,
            "comentario": comentario,
            "timestamp": str(datetime.datetime.now()),
            "ticket_id": ticket_id
        })
        go_to("ticket")

# Página: Ticket
elif st.session_state.page == "ticket":
    data = st.session_state.data
    st.subheader("Ticket")
    st.write(f"**Fecha y hora:** {data.get('timestamp','-')}")
    st.write(f"**Línea:** {data.get('linea','-')}")
    st.write(f"**Motivo:** {data.get('motivo','-')}")
    st.write(f"**Submotivo:** {data.get('submotivo','-')}")
    st.write(f"**Componente:** {data.get('componente','-')}")
    st.write(f"**Minutos:** {data.get('minutos', '-')}")
    st.write(f"**Comentario:** {data.get('comentario','-')}")
    st.write(f"**Usuario:** {data.get('user','-')}")
    st.write(f"**ID Ticket:** `{data.get('ticket_id','-')}`")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Confirmar"):
            go_to("confirmacion")   # 👈 ahora va a la nueva página de confirmación
    with col2:
        if st.button("Cancelar"):
            reset_to_home()

# Página: Confirmación (estilo Mercado Pago, sin bloques de Streamlit)
elif st.session_state.page == "confirmacion":
    data = st.session_state.data

    # Contenedor full-screen centrado
    st.markdown('<div class="mp-full"><div class="mp-card">', unsafe_allow_html=True)

    # Ícono de check
    st.markdown("""
        <div class="mp-check">
            <svg viewBox="0 0 52 52"><path d="M14 27 L22 35 L38 17"></path></svg>
        </div>
    """, unsafe_allow_html=True)

    # Título + subtítulo
    st.markdown(f"""
        <div class="mp-title">Evento registrado</div>
        <div class="mp-subtitle">ID Ticket: <b>{data.get('ticket_id','-')}</b></div>
    """, unsafe_allow_html=True)

    # Resumen
    st.markdown('<div class="mp-summary">', unsafe_allow_html=True)
    def kv(k, v):
        st.markdown(f"""<div class="mp-kv"><div class="k">{k}</div><div class="v">{v}</div></div>""", unsafe_allow_html=True)
    kv("Fecha y hora", data.get('timestamp','-'))
    kv("Línea", data.get('linea','-'))
    kv("Motivo", data.get('motivo','-'))
    kv("Submotivo", data.get('submotivo','-'))
    kv("Componente", data.get('componente','-'))
    kv("Minutos", data.get('minutos','-'))
    kv("Usuario", data.get('user','-'))
    st.markdown("</div>", unsafe_allow_html=True)

    # Botones de acción
    colA, colB = st.columns(2)
    with colA:
        if st.button("Registrar otro evento", key="btn_otro", use_container_width=True):
            reset_to_home()
    with colB:
        if st.button("Ver detalle del ticket", key="btn_detalle", use_container_width=True):
            go_to("ticket")

    st.markdown('</div></div>', unsafe_allow_html=True)

# (Opcional) Página: Splash — ya no se usa, podés borrarla
elif st.session_state.page == "splash":
    st.success("✅ Evento registrado correctamente.")
    st.write("Volver al inicio:")
    if st.button("Volver"):
        reset_to_home()
