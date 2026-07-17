CLIENTES = {
    "mememx": {
        "calendar_id": "al2222100661@gmail.com",
        "page_id_facebook": "1157126437494359",
        "panel_usuario": "bot2mx4",
        "panel_password": "123456789",
    },
    "bot2mx4_whatsapp": {
        "calendar_id": "al2222100661@gmail.com",
        "page_id_facebook": "1182360801633256",
        "panel_usuario": "bot2mx4",
        "panel_password": "Chewbacca0107#",
    },
}

def obtener_calendar_id(page_id):
    for datos in CLIENTES.values():
        if datos["page_id_facebook"] == page_id:
            return datos["calendar_id"]
    return None

def obtener_cliente_por_login(usuario, password):
    """Busca un cliente que coincida con ese usuario/password, regresa su page_id."""
    for datos in CLIENTES.values():
        if datos.get("panel_usuario") == usuario and datos.get("panel_password") == password:
            return datos["page_id_facebook"]
    return None