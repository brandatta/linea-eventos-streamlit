import streamlit as st
import datetime
import base64
from streamlit.components.v1 import html  # Overlay HTML full-screen

# ======= Estilos compactos (menos scroll) =======
st.markdown("""
    <style>
    .block-container { padding-top: 2rem; } /* un poco + bajo pero sin cortar título */
    h1, h2, h3 { font-size: 1.1rem !important; margin-bottom: 0.35rem !important; }
    .stMarkdown p { margin-bottom: 0.25rem; }
    .stButton>button { padding: 0.45rem 0.8rem; }
    .stSelectbox, .stTextInput, .stTextArea { margin-bottom: 0.5rem; }
    .kpi { font-weight: 600; }
    /* achicar espacios verticales entre bloques */
    [data-testid="stVerticalBlock"] > div:has(> .stColumn) { margin-bottom: 0.5rem; }
    </style>
""", unsafe_allow_html=True)

# ======= Util: cargar logo como base64 =======
@st.cache_data(show_spinner=False)
def get_logo_b64(path="logorelleno.png"):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception:
        return None

# ======= Inicialización de estado =======
def init_state():
    if 'page' not in st.session_state:
        st.session_state.page = 'linea'
    if 'data' not in st.session_state:
        st.session_state.data = {}
    if 'overlay_slot' not in st.session_state:
        st.session_state.overlay_slot = st.empty()

def clear_overlay():
    try:
        st.session_state.overlay_slot.empty()
    except Exception:
        pass

def reset_to_home():
    clear_overlay()
    st.session_state.clear()
    st.session_state.page = 'linea'
    st.session_state.data = {}
    st.session_state.overlay_slot = st.empty()

init_state()

# ======= Handler de acciones via query params =======
params = st.query_params
if "action" in params:
    act = params.get("action")
    if act == "home":
        reset_to_home()
        st.query_params.clear()
    elif act == "ticket":
        clear_overlay()
        st.session_state.page = "ticket"
        st.query_params.clear()

def go_to(page):
    if page != "confirmacion":
        clear_overlay()
    st.session_state.page = page

# 👉 No mostrar título cuando estoy en la confirmación (evita solapado)
if st.session_state.page != "confirmacion":
    st.title("App Registro de Eventos")

# ======= Página: Seleccionar Línea =======
if st.session_state.page == "linea":
    clear_overlay()
    st.header("Selecciona una línea")
    c1, c2, c3 = st.columns(3)
    if c1.button("Línea 1", use_container_width=True):
        st.session_state.data['linea'] = "Línea 1"
        go_to("user")
    if c2.button("Línea 2", use_container_width=True):
        st.session_state.data['linea'] = "Línea 2"
        go_to("user")
    if c3.button("Línea 3", use_container_width=True):
        st.session_state.data['linea'] = "Línea 3"
        go_to("user")

# ======= Página: Seleccionar Usuario =======
elif st.session_state.page == "user":
    clear_overlay()
    st.header("Selecciona tu usuario")
    col_sel, col_btn = st.columns([3, 1])
    with col_sel:
        user = st.selectbox("Usuario", ["", "usuario1", "usuario2", "usuario3"], label_visibility="collapsed")
    with col_btn:
        if st.button("Continuar", use_container_width=True) and user:
            st.session_state.data['user'] = user
            go_to("motivo")

# ======= Página: Motivo =======
elif st.session_state.page == "motivo":
    clear_overlay()
    st.header("Selecciona un motivo")
    motivos = [
        "CAMBIO DE LOTE", "ROTURA DE AMPOLLAS", "MAL CIERRE DE ESTUCHES",
        "OTROS (GENERAL)", "OTROS (CARGADORES)", "OTROS (ESTUCHADORA)",
        "CHUPETES", "OTROS (KETAN)", "BAJADA DE BLISTER",
        "PROBLEMA DE TRAZABILIDAD", "BAJADA PROSPECTOS",
        "ERROR SISTEMA LIXIS", "SISTEMA DE VISIÓN", "CODIFICADO WOLKE",
        "OTROS (BLISTERA)", "FUERA DE PASO OPERATIVO B",
        "FALTA DE INSUMOS DE DEPOSITO"
    ]
    col_sel, col_btn = st.columns([3, 1])
    with col_sel:
        selected_motivo = st.selectbox("Motivo", [""] + motivos, label_visibility="collapsed")
    with col_btn:
        if st.button("Continuar", use_container_width=True) and selected_motivo:
            st.session_state.data['motivo'] = selected_motivo
            go_to("submotivo")

# ======= Página: Submotivo =======
elif st.session_state.page == "submotivo":
    clear_overlay()
    st.header("Selecciona un submotivo")
    c1, c2, c3 = st.columns(3)
    if c1.button("Motor", use_container_width=True):
        st.session_state.data['submotivo'] = "Motor"
        go_to("componente")
    if c2.button("Sensor", use_container_width=True):
        st.session_state.data['submotivo'] = "Sensor"
        go_to("componente")
    if c3.button("Panel", use_container_width=True):
        st.session_state.data['submotivo'] = "Panel"
        go_to("componente")

# ======= Página: Componente =======
elif st.session_state.page == "componente":
    clear_overlay()
    st.header("Selecciona un componente")
    c1, c2, c3 = st.columns(3)
    if c1.button("PLC", use_container_width=True):
        st.session_state.data['componente'] = "PLC"
        go_to("tipo")
    if c2.button("Tornillo", use_container_width=True):
        st.session_state.data['componente'] = "Tornillo"
        go_to("tipo")
    if c3.button("Interruptor", use_container_width=True):
        st.session_state.data['componente'] = "Interruptor"
        go_to("tipo")

# ======= Página: Tipo de Evento =======
elif st.session_state.page == "tipo":
    clear_overlay()
    linea_txt = st.session_state.data.get('linea', 'Línea')
    st.header(f"Selecciona una opción para {linea_txt}")
    c1, c2 = st.columns(2)
    if c1.button("Interrupción", use_container_width=True):
        st.session_state.data["tipo"] = "interrupcion"
        go_to("form")
    if c2.button("Novedad", use_container_width=True):
        st.session_state.data["tipo"] = "novedad"
        go_to("form")

# ======= Página: Formulario =======
elif st.session_state.page == "form":
    clear_overlay()
    tipo = st.session_state.data.get("tipo", "interrupcion")
    linea_txt = st.session_state.data.get('linea', 'Línea')

    st.header(f"{tipo.title()} - {linea_txt}")
    st.markdown(
        f"**Motivo:** {st.session_state.data.get('motivo','-')}  |  "
        f"**Submotivo:** {st.session_state.data.get('submotivo','-')}  |  "
        f"**Componente:** {st.session_state.data.get('componente','-')}"
    )

    if tipo == "interrupcion":
        col_a, col_b = st.columns(2)
        with col_a:
            start_time_str = st.text_input("Inicio (HH:MM)", placeholder="08:30")
        with col_b:
            end_time_str = st.text_input("Fin (HH:MM)", placeholder="09:15")
    else:
        start_time_str = end_time_str = None

    comentario = st.text_area("Describe el evento", height=100)

    c_sp, c_btn = st.columns([3, 1])
    with c_btn:
        if st.button("Confirmar", use_container_width=True):
            minutos = None
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

# ======= Página: Ticket (grilla compacta) =======
elif st.session_state.page == "ticket":
    clear_overlay()
    data = st.session_state.data
    st.subheader("Ticket")
    cols = st.columns(2)
    with cols[0]:
        st.write(f"**Fecha y hora:** {data.get('timestamp','-')}")
        st.write(f"**Línea:** {data.get('linea','-')}")
        st.write(f"**Motivo:** {data.get('motivo','-')}")
        st.write(f"**Submotivo:** {data.get('submotivo','-')}")
    with cols[1]:
        st.write(f"**Componente:** {data.get('componente','-')}")
        st.write(f"**Minutos:** {data.get('minutos', '-')}")
        st.write(f"**Usuario:** {data.get('user','-')}")
        st.write(f"**Comentario:** {data.get('comentario','-')}")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Confirmar", use_container_width=True):
            go_to("confirmacion")
    with c2:
        if st.button("Cancelar", use_container_width=True):
            reset_to_home()

# ======= Página: Confirmación (modal clásico, sin scroll) =======
elif st.session_state.page == "confirmacion":
    d = st.session_state.data
    logo_b64 = get_logo_b64("logorelleno.png")
    logo_img = f"<img src='data:image/png;base64,{logo_b64}' class='mp-logo' alt='Logo'>" if logo_b64 else ""

    overlay_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <style>
        html, body {{
          margin: 0; padding: 0;
          font-family: system-ui, -apple-system, Segoe UI, Roboto, "Helvetica Neue", Arial;
        }}
        .mp-overlay {{
          position: fixed; inset: 0;
          background: rgba(0,0,0,0.35);   /* gris translúcido */
          z-index: 9999;
          display: grid; place-items: center;
        }}
        .mp-card {{
          width: 540px;
          max-width: 95vw;
          background: #fff;
          border-radius: 14px;
          box-shadow: 0 6px 20px rgba(0,0,0,0.12);
          padding: 14px 16px;              /* menos padding */
          text-align: center;
          border: 1px solid #eaeaea;
          animation: cardIn 1000ms ease-out both;
        }}

        .mp-logo {{
          width: 70px;                   /* logo chico */
          margin: 0 auto 12px auto;
          display: block;
          animation: logoIn 1000ms ease-out both,
                     logoPulse 3000ms ease-in-out 1000ms infinite;
          transform-origin: center;
        }}
        @keyframes cardIn {{
          0%   {{ opacity: 0; transform: translateY(12px) scale(0.96); }}
          100% {{ opacity: 1; transform: translateY(0)   scale(1); }}
        }}
        @keyframes logoIn {{
          0%   {{ opacity: 0; transform: scale(0.8) translateY(8px); }}
          100% {{ opacity: 1; transform: scale(1)   translateY(0);  }}
        }}
        @keyframes logoPulse {{
          0%, 100% {{ transform: scale(1); }}
          50%      {{ transform: scale(1.04); }}
        }}

        .mp-title {{ font-size: 1.1rem; font-weight: 700; margin-bottom: 4px; }}
        .mp-subtitle {{ color: #5f6368; font-size: 0.9rem; margin-bottom: 12px; }}

        .mp-summary {{
          text-align: left;
          background: #fafafa;
          border: 1px solid #e0e0e0;
          border-radius: 12px;
          padding: 10px 12px;
          margin: 10px 0 14px 0;
          font-size: 0.9rem;
        }}
        .mp-kv {{ display: flex; justify-content: space-between; gap: 8px; margin: 3px 0; }}
        .mp-kv .k {{ color: #616161; }} .mp-kv .v {{ font-weight: 600; text-align: right; }}

        .mp-actions {{
          display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 8px;
        }}
        .btn {{
          display: inline-block; text-decoration: none; text-align: center;
          border-radius: 10px; padding: 8px 12px;
          border: 1px solid rgba(0,0,0,0.08);
          background: #fff; color: #111; font-size: 0.9rem;
        }}
        .btn-primary {{ background: #2E7D32; color: #fff; border: none; }}
        .mp-muted {{ color: #666; font-size: 0.85rem; margin-top: 8px; }}
      </style>
    </head>
    <body>
      <div class="mp-overlay">
        <div class="mp-card">
          {logo_img}
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

    with st.session_state.overlay_slot:
        html(overlay_html, height=600, scrolling=False)
