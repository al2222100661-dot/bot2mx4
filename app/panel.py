"""
BOT2MX4 - Panel web de conversaciones
"""

import secrets
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from clientes_config import CLIENTES
from app.database import obtener_conversaciones_multi, obtener_mensajes_conversacion, guardar_mensaje
from app.messenger import send_message
from app.whatsapp import send_whatsapp_message

router = APIRouter()

SESIONES = {}  # token: [page_ids del cliente]


def generar_token():
    return secrets.token_urlsafe(24)


@router.get("/panel/login", response_class=HTMLResponse)
async def login_form():
    return """
    <html><body style="font-family:sans-serif; max-width:400px; margin:80px auto;">
    <h2>Bot2MX4 - Panel de conversaciones</h2>
    <form method="post" action="/panel/login">
        <input name="usuario" placeholder="Usuario" style="width:100%;padding:8px;margin:6px 0;"><br>
        <input name="password" type="password" placeholder="Contraseña" style="width:100%;padding:8px;margin:6px 0;"><br>
        <button type="submit" style="width:100%;padding:10px;background:#1877f2;color:white;border:none;border-radius:5px;">Entrar</button>
    </form>
    </body></html>
    """


@router.post("/panel/login")
async def login_submit(request: Request):
    form = await request.form()
    usuario = form.get("usuario")
    password = form.get("password")

    page_ids_cliente = [
        datos["page_id_facebook"]
        for datos in CLIENTES.values()
        if datos.get("panel_usuario") == usuario and datos.get("panel_password") == password
    ]

    if not page_ids_cliente:
        return HTMLResponse("<p>Usuario o contraseña incorrectos. <a href='/panel/login'>Reintentar</a></p>")

    token = generar_token()
    SESIONES[token] = page_ids_cliente

    response = RedirectResponse(url="/panel", status_code=302)
    response.set_cookie(key="panel_token", value=token, httponly=True)
    return response


def validar_sesion(request: Request):
    token = request.cookies.get("panel_token")
    if token and token in SESIONES:
        return SESIONES[token]
    return None


@router.get("/panel", response_class=HTMLResponse)
async def panel(request: Request):
    page_ids = validar_sesion(request)
    if not page_ids:
        return RedirectResponse(url="/panel/login")

    return """
    <html><head>
    <meta charset="utf-8">
    <style>
        body { font-family: sans-serif; margin:0; display:flex; height:100vh; }
        #lista { width:300px; border-right:1px solid #ddd; overflow-y:auto; }
        #chat-container { flex:1; display:flex; flex-direction:column; }
        #chat { flex:1; padding:20px; overflow-y:auto; }
        .conv { padding:12px; border-bottom:1px solid #eee; cursor:pointer; }
        .conv:hover { background:#f5f5f5; }
        .msg-user { background:#e4e6eb; padding:8px 12px; border-radius:12px; margin:6px 0; max-width:70%; }
        .msg-bot { background:#1877f2; color:white; padding:8px 12px; border-radius:12px; margin:6px 0 6px auto; max-width:70%; }
    </style>
    </head><body>
    <div id="lista"><h3 style="padding:12px;">Conversaciones</h3><div id="lista-items">Cargando...</div></div>
    <div id="chat-container">
        <div id="chat"><p>Selecciona una conversación</p></div>
        <div style="padding:12px; border-top:1px solid #ddd; display:flex; gap:8px;">
            <input id="input-msg" placeholder="Escribe un mensaje..." style="flex:1;padding:10px;border-radius:20px;border:1px solid #ccc;">
            <button onclick="enviarMensaje()" style="padding:10px 20px;background:#1877f2;color:white;border:none;border-radius:20px;">Enviar</button>
        </div>
    </div>

    <script>
    let senderActual = null;
    let canalActual = null;
    let clienteActual = null;

    async function cargarLista() {
        const res = await fetch('/panel/api/conversaciones');
        const data = await res.json();
        const cont = document.getElementById('lista-items');
        cont.innerHTML = '';
        data.forEach(c => {
            const div = document.createElement('div');
            div.className = 'conv';
            div.innerHTML = `<b>${c.sender_id}</b><br><small>${c.canal}</small>`;
            div.onclick = () => abrirChat(c.sender_id, c.canal, c.cliente_id);
            cont.appendChild(div);
        });
    }

    async function abrirChat(sender_id, canal, cliente_id) {
        senderActual = sender_id; canalActual = canal; clienteActual = cliente_id;
        await cargarMensajes();
    }

    async function cargarMensajes() {
        if (!senderActual) return;
        const res = await fetch(`/panel/api/mensajes?sender_id=${senderActual}&cliente_id=${clienteActual}`);
        const data = await res.json();
        const cont = document.getElementById('chat');
        cont.innerHTML = data.map(m =>
            `<div class="${m.rol === 'user' ? 'msg-user' : 'msg-bot'}">${m.contenido}</div>`
        ).join('');
        cont.scrollTop = cont.scrollHeight;
    }

    async function enviarMensaje() {
        const input = document.getElementById('input-msg');
        const texto = input.value.trim();
        if (!texto || !senderActual) return;

        await fetch('/panel/api/enviar', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                sender_id: senderActual,
                cliente_id: clienteActual,
                canal: canalActual,
                texto: texto
            })
        });

        input.value = '';
        await cargarMensajes();
    }

    cargarLista();
    setInterval(cargarLista, 8000);
    setInterval(cargarMensajes, 5000);
    </script>
    </body></html>
    """


@router.get("/panel/api/conversaciones")
async def api_conversaciones(request: Request):
    page_ids = validar_sesion(request)
    if not page_ids:
        return []
    resultado = obtener_conversaciones_multi(page_ids)
    return [dict(r) for r in resultado]


@router.get("/panel/api/mensajes")
async def api_mensajes(request: Request, sender_id: str, cliente_id: str):
    page_ids = validar_sesion(request)
    if not page_ids or cliente_id not in page_ids:
        return []
    resultado = obtener_mensajes_conversacion(cliente_id, sender_id)
    return [dict(r) for r in resultado]


@router.post("/panel/api/enviar")
async def api_enviar(request: Request):
    page_ids = validar_sesion(request)
    if not page_ids:
        return {"ok": False}

    data = await request.json()
    sender_id = data.get("sender_id")
    cliente_id = data.get("cliente_id")
    canal = data.get("canal")
    texto = data.get("texto")

    if cliente_id not in page_ids:
        return {"ok": False}

    if canal == "whatsapp":
        send_whatsapp_message(sender_id, texto)
    else:
        send_message(sender_id, texto, cliente_id)

    guardar_mensaje(cliente_id, sender_id, canal, "assistant", texto)

    return {"ok": True}