"""
BOT2MX4 - Configuración multi-cliente
Cada cliente tiene su propia configuración identificada por su PAGE_ID
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ─── TOKENS POR PÁGINA ────────────────────────────────────────────────────────
PAGE_TOKENS = {
    "1157126437494359": os.getenv("PAGE_ACCESS_TOKEN"),           # Bot2MX4
    "1108077452386563": os.getenv("PAGE_TOKEN_MEMEMX"),           # Mememx
}

# ─── CONFIGURACIÓN POR CLIENTE ────────────────────────────────────────────────
CLIENTS = {
    "1157126437494359": {
        "name":     "Bot2MX4",
        "type":     "agencia de automatización",
        "phone":    "7223048125",
        "address":  "Toluca, Estado de México",
        "hours":    "Lunes a Viernes 9am-6pm",
         "numero para trasferencia":"72212345678901011",
        "services": [
            {"nombre": "Bot para Messenger", "precio": "$1,500 MXN instalación + $500/mes", "duracion": "Entrega en 5 días"},
            {"nombre": "Casa inteligente",   "precio": "Desde $3,000 MXN",                  "duracion": "Instalación en 1 día"},
        ],
        "faq": {
            "formas de pago": "Transferencia bancaria (SPEI) o efectivo.",
            "garantía":       "20 días de soporte incluidos.",
        }
    },

    "1108077452386563": {
        "name":     "Mememx",
        "type":     "servicio de memes",
        "phone":    "7223048125",
        "address":  "México",
        "hours":"Todos los días 12pm a 8pm",
        "services": [
            {"nombre": "Meme personalizado", "precio": "$100 MXN", "duracion": "Entrega en 24hrs"},
        ],
        "faq": {
            "formas de pago": "Transferencia bancaria (SPEI) o efectivo.",
            "tiempo de entrega": "24 horas después de confirmar el pedido.",
            "cancelaciones": "Sin reembolso una vez iniciado el trabajo.",
        }
    }
}


def get_client_config(page_id: str) -> dict:
    """Regresa la configuración del cliente según el PAGE_ID."""
    return CLIENTS.get(page_id, CLIENTS["1157126437494359"])


def get_page_token(page_id: str) -> str:
    """Regresa el token de acceso según el PAGE_ID."""
    return PAGE_TOKENS.get(page_id, os.getenv("PAGE_ACCESS_TOKEN"))


def get_system_prompt(page_id: str) -> str:
    """Genera el system prompt personalizado para cada cliente."""
    c = get_client_config(page_id)

    servicios_texto = "\n".join([
        f"  - {s['nombre']}: {s['precio']} ({s['duracion']})"
        for s in c["services"]
    ])

    faq_texto = "\n".join([
        f"  - {k.capitalize()}: {v}"
        for k, v in c["faq"].items()
    ])

    return f"""
Eres el asistente de {c['name']}, un {c['type']}.

Tu nombre es Luca y eres amigable, cercano y profesional.

HORARIO: {c['hours']}
TELÉFONO: {c['phone']}
UBICACIÓN: {c['address']}
NÚMERO PARA TRANSFERENCIAS/ADELANTOS: {c.get('numero_transferencia', 'Contactar directamente para coordinar el pago')}

SERVICIOS:
{servicios_texto}

PREGUNTAS FRECUENTES:
{faq_texto}

REGLAS:
1. Saluda de forma cálida la primera vez.
2. Responde breve y claro — el cliente escribe desde su celular.
3. Si quieren ordenar o agendar, pide: nombre completo y detalles del pedido.
4. Confirma siempre antes de cerrar: "¿Confirmas tu pedido de [detalle]?"
5. Si no sabes algo di "Déjame verificarlo y te respondo pronto".
6. Usa emojis con moderación 😊
7. Responde siempre en español mexicano.
8. Para urgencias da el teléfono: {c['phone']}
9. Si el cliente pregunta a qué número transferir el pago o adelanto, dale el NÚMERO PARA TRANSFERENCIAS indicado arriba.
""".strip()
