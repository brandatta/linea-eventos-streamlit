import streamlit as st
import datetime
import time

# 🔧 CSS para reducir márgenes y fuente
st.markdown("""
    <style>
    .block-container {
        padding-top: 0.5rem !important;
    }
    h1 {
        font-size: 22px !important;
        margin-bottom: 0.3rem !important;
    }
    h2 {
        font-size: 20px !important;
        margin-bottom: 0.2rem !important;
    }
    h3 {
        font-size: 18px !important;
        margin-bottom: 0.2rem !important;
    }
    button[kind="primary"] {
        margin-top: 0.3rem !important;
        margin-bottom: 0.3rem !important;
    }
    textarea, .stTextInput>div>input, .stSelectbox>div {
        margin-bottom: 0.5rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# 🧠 Inicialización del estado
if 'page' not in st.session_state:
    st.session_state.page = 'linea'
    st.session_state.data = {}

def go_to(page):
    st.session_state.page = page

st.title("App Registro de Eventos")

# Página: Seleccionar Línea
if st.session_state.page == "linea":
    st.header("Selecciona una línea")
    for num in [1, 2, 3]:
        if st.button(f"Línea {num}"):
            st.session_state.data['linea'] = f"Línea {num}"
            go_to("user")

# Página: Seleccionar Usuario
elif st.session_state.page == "user":
    st.header("Selecciona tu usuario")
    user = st.selectbox("Usuario", ["", "usuario1", "usuario2", "usuario3"])
    if st.button("Continuar") and user:
        st.session_state.data['user'] = user
        go_to("motivo")

# Página: Seleccionar Motivo
elif st.session_state.page == "motivo":
    st.header("Selecciona un motivo")
    for motivo in ["Avería", "Rotura", "Fallo eléctrico"]:
        if st.button(motivo):
            st.session_state.data['motivo'] = motivo
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
    st.header(f"Selecciona una opción para {st.session_state.data['linea']}")
    if st.button("Interrupción"):
        st.session_state.data["tipo"] = "interrupcion"
        go_to("form")
    if st.button("Novedad"):
        st.session_state.data["tipo"] = "novedad"
        go_to("form")

# Página: Formulario
elif st.session_state.page == "form":
    tipo = st.session_state.data["tipo"]
    st.header(f"{tipo.title()} - {st.session_state.data['linea']}")
    st.markdown(
        f"**Motivo:** {st.session_state.data['motivo']} | "
        f"**Submotivo:** {st.session_state.data['submotivo']} | "
        f"**Componente:** {st.session_state.data['componente']}"
    )

    if tipo == "interrupcion":
        start = st.time_input("Hora de inicio")
        end = st.time_input("Hora de fin")
    else:
        start = end = None

    comentario = st.text_area("Describe el evento")

    if st.button("Confirmar"):
        minutos = None
        if tipo == "interrupcion" and start and end:
            minutos = int((datetime.datetime.combine(datetime.date.today(), end) -
                           datetime.datetime.combine(datetime.date.today(), start)).total_seconds() / 60)
        st.session_state.data.update({
            "start": str(start),
            "end": str(end),
            "minutos": minutos,
            "comentario": comentario,
            "timestamp": str(datetime.datetime.now())
        })
        go_to("ticket")

# Página: Ticket
elif st.session_state.page == "ticket":
    data = st.session_state.data
    st.subheader("Ticket")
    st.write(f"**Fecha y hora:** {data['timestamp']}")
    st.write(f"**Línea:** {data['linea']}")
    st.write(f"**Motivo:** {data['motivo']}")
    st.write(f"**Submotivo:** {data['submotivo']}")
    st.write(f"**Componente:** {data['componente']}")
    st.write(f"**Minutos:** {data.get('minutos', '-')}")
    st.write(f"**Comentario:** {data['comentario']}")
    st.write(f"**Usuario:** {data['user']}")

    if st.button("Confirmar"):
        go_to("splash")
    if st.button("Cancelar"):
        st.session_state.clear()
        st.session_state.page = "linea"
        st.experimental_rerun()

# Página: Splash
elif st.session_state.page == "splash":
    if 'splash_shown' not in st.session_state:
        st.session_state.splash_shown = True
        st.success("✅ Evento registrado correctamente.")
        st.write("Redirigiendo al inicio en 3 segundos...")
        time.sleep(3)
    else:
        st.session_state.clear()
        st.session_state.page = "linea"
        st.experimental_rerun()
