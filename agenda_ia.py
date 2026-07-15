import os
import json
import requests
from datetime import datetime
import pytz

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def detectar_intencion_agenda(mensaje_usuario: str, historial: str = "") -> dict:
    zona_mexico = pytz.timezone('America/Mexico_City')
    ahora_mexico = datetime.now(zona_mexico)

    prompt_sistema = f"""Eres un asistente que detecta si un usuario quiere agendar un servicio y extrae los datos necesarios de TODA la conversación (no solo el último mensaje).

Fecha y hora actuales: {ahora_mexico.strftime('%Y-%m-%dT%H:%M:%S')} (zona horaria: America/Mexico_City)

Hay DOS tipos de servicio, cada uno requiere datos distintos:

1. "bot" (chatbot para negocio) — requiere estos datos antes de poder agendar:
   - nombre_completo
   - telefono
   - nombre_negocio
   - giro_negocio
   - descripcion_bot (qué debe hacer el bot)
   IMPORTANTE: para este tipo de servicio, fecha_hora_inicio SIEMPRE debe ser la fecha y hora ACTUALES (la de "Fecha y hora actuales" arriba). NUNCA preguntes por una fecha al cliente para este servicio, ya que representa el momento de la SOLICITUD, no una cita programada.


2. "casa_inteligente" — requiere TODOS estos datos antes de poder agendar:
   - nombre_completo
   - telefono
   - direccion (dónde se hará la instalación/visita)
   - fecha_hora_inicio (día y hora de la cita)

Analiza el mensaje actual Y el historial para juntar todos los datos que el usuario ya ha dado a lo largo de la conversación.
Si el historial muestra que ya se estaba pidiendo una fecha/hora para agendar, y el mensaje actual es solo una hora o fecha suelta (ej. "3:30", "a las 4", "mañana"), interpreta eso como la respuesta a esa pregunta y continúa el mismo tipo de servicio que se venía procesando en el historial.


Si detectas que el usuario quiere alguno de estos dos servicios, responde SOLO con un JSON (sin texto adicional):
{{
  "tipo_servicio": "bot" o "casa_inteligente",
  "datos_completos": true o false,
  "nombre_completo": "valor o null",
  "telefono": "valor o null",
  "nombre_negocio": "valor o null (solo para bot)",
  "giro_negocio": "valor o null (solo para bot)",
  "descripcion_bot": "valor o null (solo para bot)",
  "direccion": "valor o null (solo para casa_inteligente)",
  "fecha_hora_inicio": "YYYY-MM-DDTHH:MM:SS (para 'bot' siempre usa la fecha/hora actual, para 'casa_inteligente' usa la fecha que el cliente indique)",
  "fecha_hora_fin": "YYYY-MM-DDTHH:MM:SS o null (1 hora despues del inicio si no se especifica)",
  "falta_info": "pregunta breve y natural pidiendo el SIGUIENTE dato que falta (solo uno a la vez, el más importante primero)"
}}

Si el usuario NO está pidiendo ninguno de estos dos servicios, responde:
{{"tipo_servicio": null, "datos_completos": false}}

No inventes datos que el usuario no haya dado explícitamente. Responde ÚNICAMENTE el JSON."""

    try:
        response = requests.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": prompt_sistema},
                    {"role": "user", "content": f"Historial de la conversación:\n{historial}\n\nMensaje actual: {mensaje_usuario}"}
                ],
                "max_tokens": 500,
                "temperature": 0.1
            },
            timeout=30
        )
        data = response.json()
        contenido = data["choices"][0]["message"]["content"].strip()
        contenido = contenido.replace("```json", "").replace("```", "").strip()

        return json.loads(contenido)

    except Exception as e:
        print(f"[ERROR detectar_intencion_agenda] {e}")
        return {"tipo_servicio": None, "datos_completos": False}