import streamlit as st
import datetime

# Inicializar el estado de navegación
if "page" not in st.session_state:
    st.session_state.page = "linea"
    st.session_state.data = {}

# Navegación entre páginas
def go_to(page):
    st.session_state.page = page

# Página: Seleccionar línea
if st.session_state.page == "linea":
    st.title("Selecciona una línea")
    for num in [1, 2, 3]:
        if st.button(f"Línea {num}"):
            st.session_state.data["linea"] = f"Linea {num}"
            go_to("user")

# Página: Seleccionar usuario
elif st.session_state.page == "user":
    st.title("Selecciona tu usuario")
    user = st.selectbox("Usuario", ["", "usuario1", "usuario2", "usuario3"])
    if st.button("Continuar") and user:
        st.session_state.data["user"] = user
        go_to("motivo")

# Página: Seleccionar motivo
elif st.session_state.page == "motivo":
    st.title("Selecciona un motivo")
    for motivo in ["Avería", "Rotura", "Fallo eléctrico"]:
        if st.button(motivo):
            st.session_state.data["motivo"] = motivo
            go_to("submotivo")

# Página: Seleccionar submotivo
elif st.session_state.page == "submotivo":
    st.title("Selecciona un submotivo")
    for sub in ["Motor", "Sensor", "Panel"]:
        if st.button(sub):
            st.session_state.data["submotivo"] = sub
            go_to("componente")

# Página: Seleccionar componente
elif st.session_state.page == "componente":
    st.title("Selecciona un componente")
    for comp in ["PLC", "Tornillo", "Interruptor"]:
        if st.button(comp):
            st.session_state.data["componente"] = comp
            go_to("option")

# Página: Seleccionar tipo
elif st.session_state.page == "option":
    st.title(f"Selecciona una opción para {st.session_state.data['linea']}")
    if st.button("Interrupción"):
        st.session_state.data["tipo"] = "interrupcion"
        go_to("form")
    if st.button("Novedad"):
        st.session_state.data["tipo"] = "novedad"
        go_to("form")

# Página: Formulario evento
elif st.session_state.page == "form":
    tipo = st.session_state.data["tipo"]
    st.title(f"{tipo.title()} - {st.session_state.data['linea']}")

    if tipo == "interrupcion":
        start = st.time_input("Inicio")
        end = st.time_input("Fin")
    else:
        start = end = None

    comentario = st.text_area("Describe el evento")

    if st.button("Confirmar"):
        minutos = None
        if tipo == "interrupcion" and start and end:
            minutos = int((datetime.datetime.combine(datetime.date.today(), end) - datetime.datetime.combine(datetime.date.today(), start)).total_seconds() / 60)

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
    st.title("Ticket")
    st.write(f"**Fecha y hora:** {data['timestamp']}")
    st.write(f"**Línea:** {data['linea']}")
    st.write(f"**Motivo:** {'Interrupción' if data['tipo'] == 'interrupcion' else 'Novedad'}")
    st.write(f"**Minutos:** {data.get('minutos', '-')}")
    st.write(f"**Comentario:** {data['comentario']}")
    st.write(f"**Usuario:** {data['user']}")

    if st.button("Confirmar"):
        go_to("splash")
    if st.button("Cancelar"):
        st.session_state.clear()

# Página: Splash
elif st.session_state.page == "splash":
    st.title("Evento Registrado")
    st.write("Redirigiendo en 5 segundos...")
    if st.button("Volver al inicio"):
       st.session_state.clear()
       st.experimental_rerun()
