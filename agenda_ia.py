import os
import json
import requests
from datetime import datetime

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def detectar_intencion_agenda(mensaje_usuario: str) -> dict:
    prompt_sistema = f"""Eres un asistente que detecta si un usuario quiere agendar una cita, consulta o llamada.
Fecha y hora actuales: {datetime.now().isoformat()} (zona horaria: America/Mexico_City)

Si detectas intención de agendar, responde SOLO con un JSON (sin texto adicional, sin explicaciones) con este formato exacto:
{{
  "agendar": true,
  "nombre": "nombre del cliente o null si no lo dio",
  "telefono": "teléfono o null si no lo dio",
  "tipo_servicio": "descripción breve de lo que pide",
  "notas": "detalles adicionales o vacío",
  "fecha_hora_inicio": "YYYY-MM-DDTHH:MM:SS o null si falta información",
  "fecha_hora_fin": "YYYY-MM-DDTHH:MM:SS (asume 1 hora después del inicio si no se especifica) o null"
}}

Si NO detectas intención de agendar, o falta información crítica como la fecha/hora, responde:
{{"agendar": false, "falta_info": "pregunta breve y natural para pedir lo que falta"}}

No inventes datos que el usuario no haya dado. Responde ÚNICAMENTE el JSON."""

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
                    {"role": "user", "content": mensaje_usuario}
                ],
                "max_tokens": 400,
                "temperature": 0.1
            },
            timeout=30
        )
        data = response.json()
        contenido = data["choices"][0]["message"]["content"].strip()

        # Por si Groq envuelve el JSON en ```json ... ```
        contenido = contenido.replace("```json", "").replace("```", "").strip()

        return json.loads(contenido)

    except Exception as e:
        print(f"[ERROR detectar_intencion_agenda] {e}")
        return {"agendar": False, "falta_info": ""}