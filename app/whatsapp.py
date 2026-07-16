"""
BOT2MX4 - Funciones para enviar mensajes por WhatsApp Cloud API
"""

import os
import requests

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")
WHATSAPP_API_URL = f"https://graph.facebook.com/v21.0/{WHATSAPP_PHONE_ID}/messages"


def send_whatsapp_message(recipient_number: str, text: str) -> bool:
    """
    Envía un mensaje de texto por WhatsApp.
    recipient_number: número del destinatario en formato internacional, sin '+' (ej. '5217221234567')
    """
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_number,
        "type": "text",
        "text": {"body": text}
    }

    response = requests.post(WHATSAPP_API_URL, headers=headers, json=payload)

    if response.status_code != 200:
        print(f"[ERROR WhatsApp] {response.status_code}: {response.text}")
        return False
    return True