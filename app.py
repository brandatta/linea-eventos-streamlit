import streamlit as st
import datetime
import base64
import pandas as pd
import mysql.connector
from streamlit.components.v1 import html  # Overlay HTML full-screen

# ================== CONFIG / UI ==================
st.markdown("""
    <style>
    .block-container { padding-top: 2rem; }
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

# ================== UTIL: LOGO ==================
@st.cache_data(show_spinner=False)
def get_logo_b64(path="logorelleno.png"):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception:
        return None

# ================== MYSQL ==================
def get_connection():
    return mysql.connector.connect(
        host=st.secrets["app_bd"]["host"],
        user=st.secrets["app_bd"]["user"],
        password=st.secrets["app_bd"]["password"],
        database=st.secrets["app_bd"]["database"],
        port=int(st.secrets["app_bd"].get("port", 3306)),
    )

@st.cache_data(show_spinner=False)
def fetch_ops():
    """
    Devuelve OP e ItemName desde template_op.
    """
    conn = get_connection()
    try:
        q = 'SELECT DISTINCT OP, ItemName FROM template_op WHERE OP IS NOT NULL AND OP<>"" ORDER BY OP;'
        df = pd.read_sql(q, conn)
        df["OP"] = df["OP"].astype(str)
        df["ItemName"] = df["ItemName"].astype(str)
        return df
    finally:
        conn.close()

def insertar_evento(data: dict):
    """
    Inserta en la tabla 'eventos' incluyendo 'op' y 'cantidad'.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        sql = """
            INSERT INTO eventos
            (linea, usuario, tipo, motivo, submotivo, componente,
             hora_inicio, hora_fin, minutos, cantidad, comentario, registrado_por, op)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
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
            data.get("cantidad"),
            data.get("comentario"),
            data.get("user"),
            data.get("op"),
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
    """Opciones para filtros (línea, usuario, motivo, componente, tipo, op)."""
    conn = get_connection()
    try:
        dfs = {}
        for campo in ["linea", "usuario", "motivo", "componente", "tipo", "op"]:
            q = f"SELECT DISTINCT {campo} AS val FROM eventos WHERE {campo} IS NOT NULL AND {campo}<>'' ORDER BY 1;"
            df = pd.read_sql(q, conn)
            dfs[campo] = df["val"].tolist()
        return dfs
    finally:
        conn.close()

@st.cache_data(show_spinner=False)
def fetch_eventos(fecha_desde=None, fecha_hasta=None,
                  lineas=None, tipos=None, usuarios=None,
                  motivos=None, componentes=None, ops=None,
                  cantidad_min=None, cantidad_max=None,
                  limit=5000):
    """
    Devuelve un DataFrame con eventos filtrados.
    Las fechas filtran por fecha_registro (timestamp de inserción).
    Permite filtrar por OP y por cantidad (mín/máx).
    """
    conn = get_connection()
    try:
        base = """
            SELECT id, fecha_registro, linea, usuario, tipo, motivo, submotivo, componente,
                   hora_inicio, hora_fin, minutos, cantidad, comentario, registrado_por, op
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
        add_in("ops", ops, "op")

        if cantidad_min is not None:
            base += " AND cantidad >= %(cmin)s"
            params["cmin"] = cantidad_min
        if cantidad_max is not None:
            base += " AND cantidad <= %(cmax)s"
            params["cmax"] = cantidad_max

        base += " ORDER BY fecha_registro DESC"
        if limit:
            base += f" LIMIT {int(limit)}"

        df = pd.read_sql(base, conn, params=params)
        return df
    finally:
        conn.close()

# ================== STATE ==================
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

# ================== QUERY PARAM ACTIONS ==================
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

# Título (ocultar en confirmación para no solapar)
if st.session_state.page != "confirmacion":
    st.title("App Registro de Eventos")

# ================== PANTALLAS ==================

# 1) Selección de Línea
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

# 2) Selección de Usuario
elif st.session_state.page == "user":
    clear_overlay()
    st.header("Selecciona tu usuario")
    col_sel, col_btn = st.columns([3, 1])
    with col_sel:
        user = st.selectbox("Usuario", ["", "usuario1", "usuario2", "usuario3"], label_visibility="collapsed")
    with col_btn:
        if st.button("Continuar", use_container_width=True) and user:
            st.session_state.data['user'] = user
            go_to("tipo_evento")  # PASO NUEVO

# 3) Tipo de Registro (Producción o Interrupción)
elif st.session_state.page == "tipo_evento":
    clear_overlay()
    linea_txt = st.session_state.data.get('linea', 'Línea')
    st.header(f"Tipo de registro - {linea_txt}")
    c1, c2 = st.columns(2)
    if c1.button("Interrupción", use_container_width=True):
        st.session_state.data["tipo"] = "interrupcion"
        go_to("motivo")
    if c2.button("Producción", use_container_width=True):
        st.session_state.data["tipo"] = "produccion"
        go_to("produccion")

# 4) Producción (OP, cantidad, observación)
elif st.session_state.page == "produccion":
    clear_overlay()
    st.header("Producción")

    # Cargar OPs desde template_op
    try:
        df_ops = fetch_ops()
        ops = df_ops["OP"].tolist()
    except Exception as e:
        st.error(f"No se pudieron cargar las OP desde MySQL: {e}")
        ops, df_ops = [], pd.DataFrame(columns=["OP","ItemName"])

    # Mostrar "OP - ItemName" en el dropdown para que sea más claro
    label_map = {op: f"{op} - {df_ops.loc[df_ops['OP']==op, 'ItemName'].iloc[0]}" for op in ops} if not df_ops.empty else {}
    op_sel = st.selectbox("OP", [""] + ops, format_func=lambda x: label_map.get(x, x))

    # 👉 Cantidad como texto (el usuario escribe el número)
    cant_str = st.text_input("Cantidad", placeholder="Ej: 2")
    obs = st.text_area("Observación", placeholder="Detalle, lote, etc.", height=100)

    c_sp, c_btn = st.columns([3, 1])
    with c_btn:
        if st.button("Confirmar", use_container_width=True):
            if not op_sel:
                st.error("Elegí una OP para continuar.")
                st.stop()

            # Validar que la cantidad sea número (admite coma o punto)
            try:
                cant = float((cant_str or "").strip().replace(",", "."))
            except Exception:
                st.error("⛔ Cantidad inválida. Escribí un número (ej: 1200 o 1200.5).")
                st.stop()

            # Buscar ItemName correspondiente a la OP seleccionada
            itemname = None
            if not df_ops.empty:
                row = df_ops[df_ops["OP"] == op_sel]
                if not row.empty:
                    itemname = row["ItemName"].iloc[0]

            # Guardamos en el estado, para insertar luego
            st.session_state.data.update({
                "tipo": "produccion",
                "op": op_sel,                  # OP en su columna
                "cantidad": cant,              # cantidad en su columna
                "componente": itemname,        # ItemName -> componente
                "motivo": f"OP: {op_sel}",
                "submotivo": None,
                "start": None,
                "end": None,
                "minutos": None,
                "comentario": obs,             # solo observación
                "timestamp": str(datetime.datetime.now())
            })
            go_to("ticket")

    st.divider()
    if st.button("⬅️ Volver", use_container_width=True):
        go_to("tipo_evento")

# 5) Motivo (Interrupción)
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

# 6) Submotivo (Interrupción)
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

# 7) Componente (Interrupción)
elif st.session_state.page == "componente":
    clear_overlay()
    st.header("Selecciona un componente")
    c1, c2, c3 = st.columns(3)
    if c1.button("PLC", use_container_width=True):
        st.session_state.data['componente'] = "PLC"
        go_to("tipo_interrupcion")
    if c2.button("Tornillo", use_container_width=True):
        st.session_state.data['componente'] = "Tornillo"
        go_to("tipo_interrupcion")
    if c3.button("Interruptor", use_container_width=True):
        st.session_state.data['componente'] = "Interruptor"
        go_to("tipo_interrupcion")

# 8) Tipo de evento (Interrupción vs Novedad dentro de interrupción original)
elif st.session_state.page == "tipo_interrupcion":
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

# 9) Formulario (Interrupción / Novedad)
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

# 10) Ticket (grilla compacta para ambos tipos)
elif st.session_state.page == "ticket":
    clear_overlay()
    data = st.session_state.data
    st.subheader("Ticket")
    cols = st.columns(2)
    with cols[0]:
        st.write(f"**Fecha y hora:** {data.get('timestamp','-')}")
        st.write(f"**Línea:** {data.get('linea','-')}")
        st.write(f"**Tipo:** {data.get('tipo','-')}")
        st.write(f"**OP:** {data.get('op','-')}")
        st.write(f"**Cantidad:** {data.get('cantidad','-')}")
    with cols[1]:
        st.write(f"**Motivo:** {data.get('motivo','-')}")
        st.write(f"**Componente (ItemName):** {data.get('componente','-')}")
        st.write(f"**Minutos:** {data.get('minutos', '-')}")
        st.write(f"**Usuario:** {data.get('user','-')}")
        st.write(f"**Comentario:** {data.get('comentario','-')}")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Confirmar", use_container_width=True):
            # Guardar en MySQL antes de mostrar la confirmación
            try:
                insertar_evento(st.session_state.data)
            except Exception as e:
                st.error(f"Error al guardar en la base de datos: {e}")
                st.stop()
            go_to("confirmacion")
    with c2:
        if st.button("Cancelar", use_container_width=True):
            reset_to_home()

# 11) Dashboard (listar y filtrar eventos en pestañas)
elif st.session_state.page == "dashboard":
    clear_overlay()
    st.header("📊 Dashboard de eventos")

    # Fechas + límite (filtros comunes a ambas pestañas)
    colf1, colf2, colf3 = st.columns(3)
    with colf1:
        fecha_desde = st.date_input("Desde", value=None, format="DD/MM/YYYY")
    with colf2:
        fecha_hasta = st.date_input("Hasta", value=None, format="DD/MM/YYYY")
    with colf3:
        limit = st.number_input("Límite de filas", 100, 100000, 5000, step=100)

    # Cargar datos base (sin filtros de dimensión todavía)
    try:
        df_base = fetch_eventos(
            fecha_desde=fecha_desde if isinstance(fecha_desde, datetime.date) else None,
            fecha_hasta=fecha_hasta if isinstance(fecha_hasta, datetime.date) else None,
            limit=limit,
        )
    except Exception as e:
        st.error(f"Error consultando la base: {e}")
        df_base = pd.DataFrame()

    if df_base.empty:
        st.info("No hay datos para los filtros de fecha/límite actuales.")
        st.stop()

    # ===== Helper de normalización para 'tipo' =====
    def _norm_tipo(series):
        # Convierte a str, baja a minúsculas, quita acentos y espacios
        s = series.astype(str).str.strip().str.lower()
        # Quitar acentos de forma segura (sin libs extra)
        try:
            s = (s.str.normalize("NFKD")
                   .str.encode("ascii", "ignore")
                   .str.decode("ascii"))
        except Exception:
            # Si el pandas de tu runtime no soporta normalize(), fallback simple
            repl = (("á","a"),("é","e"),("í","i"),("ó","o"),("ú","u"),("ü","u"),("ñ","n"))
            for a,b in repl:
                s = s.str.replace(a,b,regex=False)
        return s

    # Muestra rápida de tipos detectados para debug
    if "tipo" in df_base.columns:
        tipos_detectados = sorted(_norm_tipo(df_base["tipo"]).dropna().unique().tolist())
        st.caption(f"Tipos detectados (normalizados): {', '.join(tipos_detectados) if tipos_detectados else '—'}")
    else:
        st.caption("La columna 'tipo' no está en el dataset.")

    # Tabs
    tab_int, tab_prod = st.tabs(["⛔ Interrupciones", "🏭 Producción"])

    # ====== pestaña: Interrupciones ======
    with tab_int:
        dfi = df_base.copy()
        if "tipo" in dfi.columns:
            tipo_norm = _norm_tipo(dfi["tipo"])
            dfi = dfi[tipo_norm.str.contains("interrup", na=False)]

        # Filtros específicos de interrupciones (se arman desde el propio subset)
        cold1, cold2, cold3 = st.columns(3)
        with cold1:
            lineas_i = st.multiselect("Líneas", sorted(dfi["linea"].dropna().unique().tolist()) if "linea" in dfi else [])
            tipos_i  = st.multiselect("Tipos",  sorted(dfi["tipo"].dropna().unique().tolist())  if "tipo"  in dfi else [])
        with cold2:
            usuarios_i = st.multiselect("Usuarios", sorted(dfi["usuario"].dropna().unique().tolist()) if "usuario" in dfi else [])
            motivos_i  = st.multiselect("Motivos",  sorted(dfi["motivo"].dropna().unique().tolist())  if "motivo"  in dfi else [])
        with cold3:
            componentes_i = st.multiselect("Componentes", sorted(dfi["componente"].dropna().unique().tolist()) if "componente" in dfi else [])

        def _apply_in(df, col, vals):
            if vals and col in df.columns:
                return df[df[col].isin(vals)]
            return df

        dfi = _apply_in(dfi, "linea", lineas_i)
        dfi = _apply_in(dfi, "tipo", tipos_i)
        dfi = _apply_in(dfi, "usuario", usuarios_i)
        dfi = _apply_in(dfi, "motivo", motivos_i)
        dfi = _apply_in(dfi, "componente", componentes_i)

        # KPIs interrupciones
        total_eventos_i = int(dfi.shape[0])
        total_minutos_i = int(pd.to_numeric(dfi.get("minutos", pd.Series(dtype=float)), errors="coerce").fillna(0).sum())
        c_k1, c_k2 = st.columns(2)
        with c_k1:
            st.markdown('<div class="kpi-card"><div class="kpi-title">Interrupciones</div>'
                        f'<div class="kpi-value">{total_eventos_i}</div></div>', unsafe_allow_html=True)
        with c_k2:
            st.markdown('<div class="kpi-card"><div class="kpi-title">Minutos (suma)</div>'
                        f'<div class="kpi-value">{total_minutos_i}</div></div>', unsafe_allow_html=True)

        # Pie
        st.subheader("Minutos de paro por línea")
        if dfi.empty:
            st.info("No hay datos para graficar con los filtros actuales.")
        else:
            dfi_g = dfi.copy()
            dfi_g["minutos"] = pd.to_numeric(dfi_g["minutos"], errors="coerce").fillna(0)
            df_pie = dfi_g.groupby("linea", as_index=False)["minutos"].sum()
            if df_pie.empty or df_pie["minutos"].sum() == 0:
                st.info("No hay minutos de interrupción para graficar con los filtros actuales.")
            else:
                import plotly.express as px
                fig = px.pie(
                    df_pie, names="linea", values="minutos", hole=0.4,
                    title="Distribución de minutos de paro por línea"
                )
                fig.update_traces(textposition="inside", texttemplate="%{label}<br>%{percent:.1%} (%{value}m)")
                fig.update_layout(margin=dict(l=0, r=0, t=40, b=0), height=300, width=300)
                c_left, c_mid, c_right = st.columns([1, 1, 1])
                with c_mid:
                    st.plotly_chart(fig, use_container_width=False)

        # Tabla interrupciones
        st.subheader("Tabla de interrupciones")
        if dfi.empty:
            st.info("No hay interrupciones para los filtros actuales.")
        else:
            cols_i = ["id", "fecha_registro", "linea", "usuario", "tipo",
                      "motivo", "submotivo", "componente", "hora_inicio",
                      "hora_fin", "minutos", "comentario", "registrado_por"]
            cols_i = [c for c in cols_i if c in dfi.columns]
            st.dataframe(dfi[cols_i], use_container_width=True, height=420)
            csv_i = dfi[cols_i].to_csv(index=False).encode("utf-8-sig")
            st.download_button("⬇️ Descargar CSV (Interrupciones)", data=csv_i,
                               file_name="interrupciones.csv", mime="text/csv",
                               use_container_width=True)

    # ====== pestaña: Producción (OP) ======
    with tab_prod:
        dfp = df_base.copy()
        if "tipo" in dfp.columns:
            tipo_norm_p = _norm_tipo(dfp["tipo"])
            # match 'produccion' y 'producción' ya normalizados => 'produccion'
            dfp = dfp[tipo_norm_p.str.contains(r"\bproduccion\b", na=False)]

        # Filtros específicos de producción
        colp1, colp2, colp3 = st.columns(3)
        with colp1:
            lineas_p = st.multiselect("Líneas", sorted(dfp["linea"].dropna().unique().tolist()) if "linea" in dfp else [])
            ops_sel  = st.multiselect("OP",     sorted(dfp["op"].dropna().unique().tolist())     if "op"     in dfp else [])
        with colp2:
            usuarios_p   = st.multiselect("Usuarios", sorted(dfp["usuario"].dropna().unique().tolist()) if "usuario" in dfp else [])
            componentes_p= st.multiselect("Componente (ItemName)", sorted(dfp["componente"].dropna().unique().tolist()) if "componente" in dfp else [])
        with colp3:
            cmin_str = st.text_input("Cantidad mínima", value="")
            cmax_str = st.text_input("Cantidad máxima", value="")

        def _apply_in(df, col, vals):
            if vals and col in df.columns:
                return df[df[col].isin(vals)]
            return df

        # Parse cantidad
        def _num_or_none(s):
            s = (s or "").strip().replace(",", ".")
            if not s:
                return None
            try:
                return float(s)
            except Exception:
                return None
        cmin = _num_or_none(cmin_str)
        cmax = _num_or_none(cmax_str)
        if (cmin_str and cmin is None) or (cmax_str and cmax is None):
            st.warning("Cantidad mínima/máxima inválida. Usá números (ej: 100 o 100.5).")

        # Aplicar filtros producción
        dfp = _apply_in(dfp, "linea", lineas_p)
        dfp = _apply_in(dfp, "usuario", usuarios_p)
        dfp = _apply_in(dfp, "componente", componentes_p)
        dfp = _apply_in(dfp, "op", ops_sel)

        if cmin is not None and "cantidad" in dfp.columns:
            dfp = dfp[pd.to_numeric(dfp["cantidad"], errors="coerce") >= cmin]
        if cmax is not None and "cantidad" in dfp.columns:
            dfp = dfp[pd.to_numeric(dfp["cantidad"], errors="coerce") <= cmax]

        # KPIs producción
        total_ops = int(dfp.shape[0])
        total_cantidad = float(pd.to_numeric(dfp.get("cantidad", pd.Series(dtype=float)), errors="coerce").fillna(0).sum())
        pk1, pk2 = st.columns(2)
        with pk1:
            st.markdown('<div class="kpi-card"><div class="kpi-title">Registros de Producción</div>'
                        f'<div class="kpi-value">{total_ops}</div></div>', unsafe_allow_html=True)
        with pk2:
            st.markdown('<div class="kpi-card"><div class="kpi-title">Cantidad total</div>'
                        f'<div class="kpi-value">{total_cantidad:.2f}</div></div>', unsafe_allow_html=True)

        # Tabla producción
        st.subheader("Tabla de producción (OP)")
        if dfp.empty:
            st.warning("No hay registros de Producción para los filtros actuales. "
                       "Arriba podés ver los 'tipos' detectados para validar que estén llegando como 'Producción/produccion'.")
        else:
            cols_p = ["id", "fecha_registro", "linea", "usuario", "tipo", "op",
                      "cantidad", "componente", "motivo", "comentario", "registrado_por"]
            cols_p = [c for c in cols_p if c in dfp.columns]
            st.dataframe(dfp[cols_p], use_container_width=True, height=420)
            csv_p = dfp[cols_p].to_csv(index=False).encode("utf-8-sig")
            st.download_button("⬇️ Descargar CSV (Producción)", data=csv_p,
                               file_name="produccion.csv", mime="text/csv",
                               use_container_width=True)

    st.divider()
    col_bk1, col_bk2 = st.columns(2)
    with col_bk1:
        if st.button("⬅️ Volver al inicio", use_container_width=True):
            go_to("linea")

# 12) Confirmación (overlay arriba, sin fondo gris)
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
          background: transparent;
          z-index: 9999;
          display: flex;
          justify-content: center;
          align-items: flex-start;
          padding-top: 1.5vh;
        }}
        .mp-card {{
          width: 540px;
          max-width: 95vw;
          background: #fff;
          border-radius: 14px;
          box-shadow: 0 6px 20px rgba(0,0,0,0.12);
          padding: 14px 16px;
          text-align: center;
          border: 1px solid #eaeaea;
          animation: cardIn 1000ms ease-out both;
        }}

        .mp-logo {{
          width: 45px;
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

        /* Una sola acción centrada */
        .mp-actions {{
          display: flex;
          justify-content: center;
          margin-top: 8px;
        }}
        .btn {{
          display: inline-block; text-decoration: none; text-align: center;
          border-radius: 10px; padding: 8px 12px;
          border: 1px solid rgba(0,0,0,0.08);
          background: #fff; color: #111; font-size: 0.9rem;
          min-width: 160px;
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
            <div class="mp-kv"><div class="k">Tipo</div><div class="v">{d.get('tipo','-')}</div></div>
            <div class="mp-kv"><div class="k">OP</div><div class="v">{d.get('op','-')}</div></div>
            <div class="mp-kv"><div class="k">Cantidad</div><div class="v">{d.get('cantidad','-')}</div></div>
            <div class="mp-kv"><div class="k">Motivo</div><div class="v">{d.get('motivo','-')}</div></div>
            <div class="mp-kv"><div class="k">Componente</div><div class="v">{d.get('componente','-')}</div></div>
            <div class="mp-kv"><div class="k">Minutos</div><div class="v">{d.get('minutos','-')}</div></div>
            <div class="mp-kv"><div class="k">Usuario</div><div class="v">{d.get('user','-')}</div></div>
            <div class="mp-kv"><div class="k">Comentario</div><div class="v">{d.get('comentario','-')}</div></div>
          </div>
          <div class="mp-actions">
            <a class="btn btn-primary"
               href="?action=home"
               onclick="try{{document.querySelector('.mp-overlay').style.display='none';}}catch(e){{}}">Registrar otro</a>
          </div>
          <div class="mp-muted">Podés cerrar esta ventana o continuar con las opciones.</div>
        </div>
      </div>
    </body>
    </html>
    """

    with st.session_state.overlay_slot:
        html(overlay_html, height=600, scrolling=False)
