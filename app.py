import streamlit as st
import datetime
import time

# CSS personalizado para achicar títulos y reducir margen superior
st.markdown("""
    <style>
    .title {
        font-size: 24px;
        margin-bottom: 0.5rem;
    }
    .block-container {
        padding-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Inicialización del estado
if 'page' not in st.session_state:
    st.session_state.page = 'linea'
    st.session_state.data = {}

def go_to(page):
    st.session_state.page = page

# Título
st.markdown('<h1 class="title">App Registro de Eventos</h1>', unsafe_allow_html=True)

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

    start_time_str = ""
    end_time_str = ""
    start_dt = end_dt = None

    if tipo == "interrupcion":
        start_time_str = st.text_input("Hora de inicio (HH:MM)", placeholder="ej. 14:30")
        end_time_str = st.text_input("Hora de fin (HH:MM)", placeholder="ej. 15:10")

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
            "start": start_time_str if start_dt else None,
            "end": end_time_str if end_dt else None,
            "minutos": minutos,
            "comentario":
