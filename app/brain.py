"""
BOT2MX4 - Cerebro del bot (Groq API - Multi-cliente)
"""

import requests
import os
from dotenv import load_dotenv
from config.business import get_system_prompt

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

conversation_history: dict[str, list] = {}
MAX_HISTORY = 20


def get_response(sender_id: str, user_message: str, page_id: str = "") -> str:
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
