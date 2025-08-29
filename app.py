import streamlit as st
import datetime
import base64
import pandas as pd
import mysql.connector
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
    [data-testid="stVerticalBlock"] > div:has(> .stColumn) { margin-bottom: 0.5rem; }
    .kpi-card {
        border: 1px solid #eee; border-radius: 10px; padding: 10px 12px;
        background: #fff;
    }
    .kpi-title { color: #666; font-size: 0.85rem; margin-bottom: 4px; }
    .kpi-value { font-size: 1.2rem; font-weight: 700; }
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

# ======= MySQL: conexión y utils =======
def get_connection():
    return mysql.connector.connect(
        host=st.secrets["app_bd"]["host"],
        user=st.secrets["app_bd"]["user"],
        password=st.secrets["app_bd"]["password"],
        database=st.secrets["app_bd"]["database"],
        port=int(st.secrets["app_bd"].get("port", 3306)),
    )

def insertar_evento(data: dict):
    conn = get_connection()
    try:
        cur = conn.cursor()
        sql = """
            INSERT INTO eventos
            (linea, usuario, tipo, motivo, submotivo, componente,
             hora_inicio, hora_fin, minutos, comentario, registrado_por)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        valores = (
            data.get("linea"),
            data.get("user"),
            data.get("tipo"),
            data.get("motivo"),
            data.get("submotivo"),
            data.get("componente"),
            data.get("start") if data.get("start") else None,
            data.get("end") if data.get("end") else None,
            data.get("minutos"),
            data.get("comentario"),
            data.get("user"),
        )
        cur.execute(sql, valores)
        conn.commit()
    finally:
        try:
            cur.close()
        except Exception:
            pass
        conn.close()

@st.cache_data(show_spinner=False)
def fetch_distinct_campos():
    """Trae opciones para filtros (línea, usuario, motivo, componente, tipo)."""
    conn = get_connection()
    try:
        dfs = {}
        for campo in ["linea", "usuario", "motivo", "componente", "tipo"]:
            q = f"SELECT DISTINCT {campo} AS val FROM eventos WHERE {campo} IS NOT NULL AND {campo}<>'' ORDER BY 1;"
            dfs[campo] = pd.read_sql(q, conn)["val"].tolist()
        return dfs
    finally:
        conn.close()

@st.cache_data(show_spinner=False)
def fetch_eventos(fecha_desde=None, fecha_hasta=None,
                  lineas=None, tipos=None, usuarios=None,
                  motivos=None, componentes=None, limit=5000):
    conn = get_connection()
    try:
        base = """
            SELECT id, fecha_registro, linea, usuario, tipo, motivo, submotivo, componente,
                   hora_inicio, hora_fin, minutos, comentario, registrado_por
            FROM eventos
            WHERE 1=1
        """
        params = {}
        if fecha_desde:
            base += " AND fecha_registro >= %(fdesde)s"
            params["fdesde"] = datetime.datetime.combine(fecha_desde, datetime.time.min)
        if fecha_hasta:
            base += " AND fecha_registro < %(fhasta)s"
            params["fhasta"] = datetime.datetime.combine(fecha_hasta, datetime.time.max)

        def add_in(clave, valores, col):
            nonlocal base, params
            if valores:
                ph = ", ".join([f"%({clave}{i})s" for i in range(len(valores))])
                base += f" AND {col} IN ({ph})"
                for i, v in enumerate(valores):
                    params[f"{clave}{i}"] = v

        add_in("linea", lineas, "linea")
        add_in("tipo", tipos, "tipo")
        add_in("usuario", usuarios, "usuario")
        add_in("motivo", motivos, "motivo")
        add_in("comp", componentes, "componente")

        base += " ORDER BY fecha_registro DESC"
        if limit:
            base += f" LIMIT {int(limit)}"

        df = pd.read_sql(base, conn, params=params)
        return df
    finally:
        conn.close()

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

# 👉 No mostrar título cuando estoy en la confirmación
if st.session_state.page != "confirmacion":
    st.title("App Registro de Eventos")

# ======= Página: Seleccionar Línea =======
if st.session_state.page == "linea":
    clear_overlay()
    st.header("Selecciona una línea")
    c1, c2 = st.columns(2)
    if c1.button("Línea 5", use_container_width=True):
        st.session_state.data['linea'] = "Línea 5"
        go_to("user")
    if c2.button("Línea 6", use_container_width=True):
        st.session_state.data['linea'] = "Línea 6"
        go_to("user")

    st.divider()
    if st.button("📊 Ver dashboard", use_container_width=True):
        go_to("dashboard")
