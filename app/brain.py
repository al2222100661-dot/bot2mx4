"""
BOT2MX4 - Cerebro del bot (Groq API - Multi-cliente)
"""

import requests
import os
from dotenv import load_dotenv
from config.business import get_system_prompt
from agenda_ia import detectar_intencion_agenda
from calendar_service import crear_evento, horario_disponible
from clientes_config import obtener_calendar_id

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

conversation_history: dict[str, list] = {}
MAX_HISTORY = 20


def intentar_agendar(user_message: str, page_id: str) -> str | None:
    """
    Devuelve un mensaje de respuesta si se procesó una solicitud de agenda,
    o None si el mensaje no tiene que ver con agendar (sigue el flujo normal).
    """
    resultado = detectar_intencion_agenda(user_message)

    if not resultado.get("agendar"):
        return None

    if not resultado.get("fecha_hora_inicio"):
        return resultado.get("falta_info") or "¿Para qué fecha y hora te gustaría agendar?"

    calendar_id = obtener_calendar_id(page_id)
    if not calendar_id:
        return None  # esta página no tiene calendario configurado, sigue flujo normal

    inicio = resultado["fecha_hora_inicio"]
    fin = resultado.get("fecha_hora_fin") or inicio

    # --- Verificar disponibilidad ---
    disponible = horario_disponible(calendar_id, inicio, fin)
    if not disponible:
        return (
            "Ese horario ya está ocupado 😕. "
            "¿Tienes otra fecha u hora disponible para tu cita?"
        )

    # --- Crear el evento ---
    resumen = f"{resultado.get('tipo_servicio', 'Cita')} - {resultado.get('nombre', 'Cliente')}"
    descripcion = (
        f"Teléfono: {resultado.get('telefono', 'No proporcionado')}\n"
        f"Notas: {resultado.get('notas', '')}"
    )

    try:
        crear_evento(calendar_id, resumen, descripcion, inicio, fin)
        return f"¡Listo! Tu cita quedó agendada para el {inicio.replace('T', ' a las ')}. 📅✅"
    except Exception as e:
        print(f"[ERROR al crear evento] {e}")
        return "Tuve un problema al agendar tu cita, ¿lo intentamos de nuevo?"


def get_response(sender_id: str, user_message: str, page_id: str = "") -> str:
    # --- Intentar agendar primero ---
    respuesta_agenda = intentar_agendar(user_message, page_id)
    if respuesta_agenda:
        return respuesta_agenda

    # --- Si no es agenda, sigue el flujo conversacional normal ---
    if sender_id not in conversation_history:
        conversation_history[sender_id] = []

    conversation_history[sender_id].append({
        "role": "user",
        "content": user_message
    })

    history = conversation_history[sender_id][-MAX_HISTORY:]
    messages = [{"role": "system", "content": get_system_prompt(page_id)}] + history

    try:
        response = requests.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": messages,
                "max_tokens": 500,
                "temperature": 0.7
            },
            timeout=30
        )

        data = response.json()

        if response.status_code != 200:
            print(f"[ERROR Groq] {response.status_code}: {data}")
            return "Lo siento, tuve un problema técnico. Intenta en un momento 😊"

        bot_reply = data["choices"][0]["message"]["content"]

        conversation_history[sender_id].append({
            "role": "assistant",
            "content": bot_reply
        })

        return bot_reply

    except Exception as e:
        print(f"[ERROR] {e}")
        return "Lo siento, tuve un problema técnico. Intenta en un momento 😊"


def clear_history(sender_id: str):
    if sender_id in conversation_history:
        del conversation_history[sender_id]
        return True
    return False