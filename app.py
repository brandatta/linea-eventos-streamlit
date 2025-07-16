# Página: Formulario
elif st.session_state.page == "form":
    tipo = st.session_state.data["tipo"]
    st.header(f"{tipo.title()} - {st.session_state.data['linea']}")
    st.markdown(
        f"**Motivo:** {st.session_state.data['motivo']} | "
        f"**Submotivo:** {st.session_state.data['submotivo']} | "
        f"**Componente:** {st.session_state.data['componente']}"
    )

    fecha_evento = st.date_input("Fecha del evento", value=datetime.date.today())

    def parse_time(text):
        try:
            return datetime.datetime.strptime(text.strip(), "%H:%M").time()
        except ValueError:
            return None

    if tipo == "interrupcion":
        start_text = st.text_input("Hora de inicio (HH:MM)", value="")
        end_text = st.text_input("Hora de fin (HH:MM)", value="")

        start = parse_time(start_text)
        end = parse_time(end_text)

        if start_text and not start:
            st.warning("⛔ Hora de inicio inválida. Usa el formato HH:MM.")
        if end_text and not end:
            st.warning("⛔ Hora de fin inválida. Usa el formato HH:MM.")
    else:
        start = end = None

    comentario = st.text_area("Describe el evento")

    if st.button("Confirmar"):
        minutos = None
        if tipo == "interrupcion":
            if not start or not end:
                st.error("⚠️ Debes ingresar horarios válidos antes de continuar.")
            else:
                minutos = int((datetime.datetime.combine(fecha_evento, end) -
                               datetime.datetime.combine(fecha_evento, start)).total_seconds() / 60)

        if tipo != "interrupcion" or (start and end):
            st.session_state.data.update({
                "fecha": str(fecha_evento),
                "start": start_text,
                "end": end_text,
                "minutos": minutos,
                "comentario": comentario,
                "timestamp": str(datetime.datetime.now())
            })
            go_to("ticket")
