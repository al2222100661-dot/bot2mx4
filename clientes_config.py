CLIENTES = {
    "bot2mx4": {
        "calendar_id": "al2222100661@gmail.com",
        "page_id_facebook": "1157126437494359",
    },


"bot2mx4_whatsapp": {
        "calendar_id": "al2222100661@gmail.com",
        "page_id_facebook": "1182360801633256",  # Phone Number ID de WhatsApp
    },
}
def obtener_calendar_id(page_id):
    for datos in CLIENTES.values():
        if datos["page_id_facebook"] == page_id:
            return datos["calendar_id"]
    return None