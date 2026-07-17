"""
BOT2MX4 - Cerebro del bot (Groq API - Multi-cliente)
"""

import requests
import os
from dotenv import load_dotenv
from config.business import get_system_prompt
from agenda_ia import detectar_intencion_agenda
from calendar_service import crear_evento_servicio, horario_disponible
from clientes_config import obtener_calendar_id
from app.database import guardar_mensaje
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

conversation_history: dict[str, list] = {}
esperando_comprobante: dict[str, bool] = {}
MAX_HISTORY = 20


def intentar_agendar(sender_id: str, user_message: str, page_id: str) -> str | None:
    # Si ya agendó y está esperando el comprobante, no vuelvas a detectar agenda
    if esperando_comprobante.get(sender_id):
        return None

    historial_texto = ""
    if sender_id in conversation_history:
        for msg in conversation_history[sender_id][-10:]:
            rol = "Usuario" if msg["role"] == "user" else "Bot"
            historial_texto += f"{rol}: {msg['content']}\n"

    resultado = detectar_intencion_agenda(user_message, historial_texto)

    if not resultado.get("tipo_servicio"):
        return None

    if not resultado.get("datos_completos"):
        return resultado.get("falta_info") or "Necesito un dato más para continuar, ¿me lo compartes?"

    calendar_id = obtener_calendar_id(page_id)
    if not calendar_id:
        return None

    inicio = resultado.get("fecha_hora_inicio")
    fin = resultado.get("fecha_hora_fin") or inicio

    if not inicio:
        return "¿Para qué día y hora te gustaría agendar?"

    tipo_servicio = resultado["tipo_servicio"]

    # Solo verificar disponibilidad para citas reales (casa inteligente), no para solicitudes de bot
    if tipo_servicio == "casa_inteligente":
        disponible = horario_disponible(calendar_id, inicio, fin)
        if not disponible:
            return "Ese horario ya está ocupado 😕. ¿Tienes otra fecha u hora disponible?"

    try:
        crear_evento_servicio(calendar_id, tipo_servicio, resultado, inicio, fin)

        if tipo_servicio == "bot":
            esperando_comprobante[sender_id] = True
            return (
                f"¡Perfecto {resultado.get('nombre_completo', '')}! Tu solicitud de bot quedó registrada. "
                f"Para confirmar tu cita, por favor envía la foto del comprobante de tu adelanto del 25%. 📸"
            )
        else:
            return (
                f"¡Listo {resultado.get('nombre_completo', '')}! Tu cita para casa inteligente quedó agendada "
                f"el {inicio.replace('T', ' a las ')}. 📅✅"
            )
    except Exception as e:
        print(f"[ERROR al crear evento] {e}")
        return "Tuve un problema al agendar, ¿lo intentamos de nuevo?"


def get_response(sender_id: str, user_message: str, page_id: str = "", canal: str = "messenger") -> str:
    if sender_id not in conversation_history:
        conversation_history[sender_id] = []

    conversation_history[sender_id].append({
        "role": "user",
        "content": user_message
    })
    guardar_mensaje(page_id, sender_id, canal, "user", user_message)

    respuesta_agenda = intentar_agendar(sender_id, user_message, page_id)
    if respuesta_agenda:
        conversation_history[sender_id].append({
            "role": "assistant",
            "content": respuesta_agenda
        })
        guardar_mensaje(page_id, sender_id, canal, "assistant", respuesta_agenda)
        return respuesta_agenda

    history = conversation_history[sender_id][-MAX_HISTORY:]

    contexto_extra = ""
    if esperando_comprobante.get(sender_id):
        contexto_extra = (
            "\nIMPORTANTE: Este cliente YA agendó su servicio y YA se le pidieron todos sus datos. "
            "Está esperando únicamente enviar la foto del comprobante de pago del 25%. "
            "NO le pidas nombre, teléfono ni detalles de nuevo, y NO le vuelvas a preguntar si confirma el pedido. "
            "Si pregunta a qué número transferir, dale el NÚMERO PARA TRANSFERENCIAS indicado arriba. "
            "Solo responde dudas y recuérdale amablemente que mande la foto del comprobante cuando pueda."
        )

    messages = [{"role": "system", "content": get_system_prompt(page_id, contexto_extra)}] + history

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
        guardar_mensaje(page_id, sender_id, canal, "assistant", bot_reply)

        return bot_reply

    except Exception as e:
        print(f"[ERROR] {e}")
        return "Lo siento, tuve un problema técnico. Intenta en un momento 😊"


def clear_history(sender_id: str):
    if sender_id in conversation_history:
        del conversation_history[sender_id]
        return True
    return False