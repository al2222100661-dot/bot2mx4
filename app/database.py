"""
BOT2MX4 - Conexión y funciones de base de datos (Supabase/Postgres)
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


def crear_tablas():
    """Crea las tablas necesarias si no existen. Correr una sola vez."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS mensajes (
            id SERIAL PRIMARY KEY,
            cliente_id TEXT NOT NULL,
            sender_id TEXT NOT NULL,
            canal TEXT NOT NULL,
            rol TEXT NOT NULL,
            contenido TEXT NOT NULL,
            fecha TIMESTAMP DEFAULT NOW()
        )
    """)
    conn.commit()
    cur.close()
    conn.close()


def guardar_mensaje(cliente_id: str, sender_id: str, canal: str, rol: str, contenido: str):
    """
    cliente_id: identificador del cliente dueño del bot (page_id o phone_number_id)
    sender_id: quién escribió (el usuario final)
    canal: 'messenger' o 'whatsapp'
    rol: 'user' o 'assistant'
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO mensajes (cliente_id, sender_id, canal, rol, contenido)
               VALUES (%s, %s, %s, %s, %s)""",
            (cliente_id, sender_id, canal, rol, contenido)
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[ERROR guardando mensaje en BD] {e}")


def obtener_conversaciones(cliente_id: str):
    """Devuelve la lista de conversaciones únicas (por sender_id) de un cliente."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """SELECT DISTINCT sender_id, canal, MAX(fecha) as ultima_fecha
           FROM mensajes
           WHERE cliente_id = %s
           GROUP BY sender_id, canal
           ORDER BY ultima_fecha DESC""",
        (cliente_id,)
    )
    resultado = cur.fetchall()
    cur.close()
    conn.close()
    return resultado


def obtener_conversaciones_multi(cliente_ids: list):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """SELECT DISTINCT sender_id, canal, cliente_id, MAX(fecha) as ultima_fecha
           FROM mensajes
           WHERE cliente_id = ANY(%s)
           GROUP BY sender_id, canal, cliente_id
           ORDER BY ultima_fecha DESC""",
        (cliente_ids,)
    )
    resultado = cur.fetchall()
    cur.close()
    conn.close()
    return resultado

def obtener_mensajes_conversacion(cliente_id: str, sender_id: str):
    """Devuelve todos los mensajes de una conversación específica, ordenados por fecha."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """SELECT rol, contenido, fecha FROM mensajes
           WHERE cliente_id = %s AND sender_id = %s
           ORDER BY fecha ASC""",
        (cliente_id, sender_id)
    )
    resultado = cur.fetchall()
    cur.close()
    conn.close()
    return resultado