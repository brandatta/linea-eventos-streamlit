import streamlit as st
import datetime
import time
from streamlit.components.v1 import html  # 👈 para overlay full-screen

# ======= Estilos (evita que se corte el título) =======
st.markdown("""
    <style>
    .block-container {
        padding-top: 3rem;  /* margen superior suficiente */
    }
    h1, h2, h3 {
        font-size: 1.2rem !important;
    }
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

# ======= Handler de acciones via query params (desde el overlay) =======
params = st.query_params
if "action" in params:
    act = params.get("action")
    if act == "home":
        reset_to_home()
        st.query_params.clear()
    elif act == "ticket":
        st.session_state.page = "ticket"
        st.query_params.clear()

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

        st.session_state.data.update({
            "start": start_time_str if tipo == "interrupcion" else None,
            "end": end_time_str if tipo == "interrupcion" else None,
            "minutos": minutos,
            "comentario": comentario,
            "timestamp": str(datetime.datetime.now())
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

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Confirmar"):
            go_to("confirmacion")   # 👉 ahora vamos al overlay HTML
    with col2:
        if st.button("Cancelar"):
            reset_to_home()

# Página: Confirmación (overlay HTML full-screen, sin bloques de Streamlit)
elif st.session_state.page == "confirmacion":
    d = st.session_state.data
    # Armamos el HTML del overlay. Usa position:fixed y cubre todo (nada de Streamlit se ve).
    overlay_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <style>
        :root {{
          --ok: #2E7D32;           /* verde sobrio */
          --ok-bg: #edf7f0;
          --text-muted: #5f6368;
          --card-bg: #fff;
          --border: rgba(0,0,0,0.06);
          --shadow: 0 8px 28px rgba(0,0,0,0.08);
        }}
        html, body {{
          margin: 0; padding: 0; background: #f6f7f9; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, "Helvetica Neue", Arial;
        }}
        .mp-overlay {{
          position: fixed; inset: 0; background: #f6f7f9; z-index: 9999;
          display: grid; place-items: center;
        }}
        .mp-card {{
          width: min(520px, 92vw); background: var(--card-bg); border-radius: 16px;
          box-shadow: var(--shadow); padding: 28px 24px; border: 1px solid var(--border); text-align: center;
        }}
        .mp-check {{
          width: 82px; height: 82px; border-radius: 50%; background: var(--ok-bg); margin: 0 auto 16px auto;
          display: grid; place-items: center; border: 2px solid var(--ok); animation: popIn 300ms ease-out;
        }}
        .mp-check svg {{
          width: 44px; height: 44px; stroke: var(--ok); fill: none; stroke-width: 3px;
          stroke-linecap: round; stroke-linejoin: round; animation: draw 500ms ease-out forwards;
        }}
        @keyframes popIn {{ 0% {{ transform: scale(0.9); opacity: 0; }} 100% {{ transform: scale(1); opacity: 1; }} }}
        @keyframes draw {{ 0% {{ stroke-dasharray: 0 100; }} 100% {{ stroke-dasharray: 100 0; }} }}
        .mp-title {{ font-size: 1.2rem; font-weight: 700; margin-bottom: 6px; }}
        .mp-subtitle {{ color: var(--text-muted); font-size: 0.96rem; margin-bottom: 14px; }}
        .mp-summary {{
          text-align: left; background: #fafafa; border: 1px solid var(--border); border-radius: 12px;
          padding: 12px 14px; margin: 14px 0 18px 0; font-size: 0.95rem; line-height: 1.35rem;
        }}
        .mp-kv {{ display: flex; justify-content: space-between; gap: 12px; margin: 4px 0; }}
        .mp-kv .k {{ color: #616161; }}
        .mp-kv .v {{ font-weight: 600; text-align: right; }}
        .mp-actions {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 10px; }}
        .btn {{
          display: inline-block; text-decoration: none; text-align: center;
          border-radius: 10px; padding: 10px 14px; border: 1px solid rgba(0,0,0,0.08); color: #111;
          background: #fff;
        }}
        .btn-primary {{ background: var(--ok); color: #fff; border: none; }}
        .mp-muted {{ color: #666; font-size: 0.9rem; margin-top: 10px; }}
      </style>
    </head>
    <body>
      <div class="mp-overlay">
        <div class="mp-card">
          <div class="mp-check">
            <svg viewBox="0 0 52 52"><path d="M14 27 L22 35 L38 17"></path></svg>
          </div>
          <div class="mp-title">Evento registrado</div>
          <div class="mp-subtitle">Ticket generado correctamente</div>

          <div class="mp-summary">
            <div class="mp-kv"><div class="k">Fecha y hora</div><div class="v">{d.get('timestamp','-')}</div></div>
            <div class="mp-kv"><div class="k">Línea</div><div class="v">{d.get('linea','-')}</div></div>
            <div class="mp-kv"><div class="k">Motivo</div><div class="v">{d.get('motivo','-')}</div></div>
            <div class="mp-kv"><div class="k">Submotivo</div><div class="v">{d.get('submotivo','-')}</div></div>
            <div class="mp-kv"><div class="k">Componente</div><div class="v">{d.get('componente','-')}</div></div>
            <div class="mp-kv"><div class="k">Minutos</div><div class="v">{d.get('minutos','-')}</div></div>
            <div class="mp-kv"><div class="k">Usuario</div><div class="v">{d.get('user','-')}</div></div>
          </div>

          <div class="mp-actions">
            <a class="btn" href="?action=ticket">Ver detalle</a>
            <a class="btn btn-primary" href="?action=home">Registrar otro</a>
          </div>

          <div class="mp-muted">Podés cerrar esta ventana o continuar con las opciones.</div>
        </div>
      </div>
    </body>
    </html>
    """
    # Render del overlay (altura completa). No hay widgets de Streamlit visibles.
    html(overlay_html, height=800, scrolling=False)

# Página: Splash (no usada, solo por compatibilidad)
elif st.session_state.page == "splash":
    st.success("✅ Evento registrado correctamente.")
    st.write("Volver al inicio:")
    if st.button("Volver"):
        reset_to_home()
