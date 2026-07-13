from calendar_service import crear_evento

link = crear_evento(
    calendar_id="al2222100661@gmail.com",
    resumen="Prueba Bot2MX4",
    descripcion="Evento creado desde el bot",
    inicio_iso="2026-07-15T10:00:00-06:00",
    fin_iso="2026-07-15T11:00:00-06:00"
)
print("Evento creado:", link)