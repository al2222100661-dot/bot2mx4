from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime

import json
import os

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    creds_json = os.environ.get('GOOGLE_CREDENTIALS_JSON')
    if creds_json:
        # En Render: lee desde variable de entorno
        info = json.loads(creds_json)
        credentials = service_account.Credentials.from_service_account_info(
            info, scopes=SCOPES
        )
    else:
        # En tu máquina local: lee desde el archivo
        credentials = service_account.Credentials.from_service_account_file(
            'bot2mx4-da1510566782.json', scopes=SCOPES
        )
    service = build('calendar', 'v3', credentials=credentials)
    return service

def crear_evento(calendar_id, resumen, descripcion, inicio_iso, fin_iso):
    service = get_calendar_service()
    evento = {
        'summary': resumen,
        'description': descripcion,
        'start': {'dateTime': inicio_iso, 'timeZone': 'America/Mexico_City'},
        'end': {'dateTime': fin_iso, 'timeZone': 'America/Mexico_City'},
    }
    evento_creado = service.events().insert(calendarId=calendar_id, body=evento).execute()
    return evento_creado.get('htmlLink')

def listar_eventos(calendar_id, max_resultados=10):
    service = get_calendar_service()
    ahora = datetime.utcnow().isoformat() + 'Z'
    eventos_result = service.events().list(
        calendarId=calendar_id, timeMin=ahora,
        maxResults=max_resultados, singleEvents=True,
        orderBy='startTime'
    ).execute()
    return eventos_result.get('items', [])


def resumen_citas(calendar_id, max_resultados=10):
    """
    Devuelve un texto legible con las próximas citas, listo para mandar por Messenger.
    """
    eventos = listar_eventos(calendar_id, max_resultados)

    if not eventos:
        return "No tienes citas próximas agendadas. 📅"

    lineas = ["📅 Tus próximas citas:\n"]
    for i, evento in enumerate(eventos, 1):
        inicio = evento['start'].get('dateTime', evento['start'].get('date'))
        resumen = evento.get('summary', 'Sin título')
        descripcion = evento.get('description', '')

        try:
            fecha_obj = datetime.fromisoformat(inicio.replace('Z', '+00:00'))
            fecha_legible = fecha_obj.strftime('%d/%m/%Y a las %I:%M %p')
        except Exception:
            fecha_legible = inicio

        lineas.append(f"{i}. {resumen}\n   🕐 {fecha_legible}")
        if descripcion:
            lineas.append(f"   📝 {descripcion}")
        lineas.append("")

    return "\n".join(lineas)

def horario_disponible(calendar_id, inicio_iso, fin_iso):
    """
    Revisa si ya existe algún evento que se cruce con el horario solicitado.
    """
    service = get_calendar_service()

    # Asegura que las fechas tengan zona horaria (Ciudad de México = -06:00)
    if 'T' in inicio_iso and '+' not in inicio_iso and 'Z' not in inicio_iso:
        inicio_iso = inicio_iso + '-06:00'
    if 'T' in fin_iso and '+' not in fin_iso and 'Z' not in fin_iso:
        fin_iso = fin_iso + '-06:00'

    eventos_result = service.events().list(
        calendarId=calendar_id,
        timeMin=inicio_iso,
        timeMax=fin_iso,
        singleEvents=True
    ).execute()

    eventos = eventos_result.get('items', [])
    return len(eventos) == 0

def crear_evento_servicio(calendar_id, tipo_servicio, datos, inicio_iso, fin_iso):
    """
    Crea un evento con todos los detalles del servicio, incluyendo
    la fecha en que se solicitó (fecha de creación del evento).
    """
    fecha_solicitud = datetime.now().strftime('%d/%m/%Y %H:%M')

    if tipo_servicio == "bot":
        resumen = f"🤖 Bot - {datos.get('nombre_negocio', 'Sin nombre')} ({datos.get('nombre_completo', '')})"
        descripcion = (
            f"📅 Solicitado el: {fecha_solicitud}\n"
            f"👤 Cliente: {datos.get('nombre_completo', 'N/D')}\n"
            f"📞 Teléfono: {datos.get('telefono', 'N/D')}\n"
            f"🏢 Negocio: {datos.get('nombre_negocio', 'N/D')}\n"
            f"📋 Giro: {datos.get('giro_negocio', 'N/D')}\n"
            f"📝 Descripción del bot: {datos.get('descripcion_bot', 'N/D')}\n"
            f"💰 Adelanto (25%): {'✅ Comprobante recibido' if datos.get('comprobante_recibido') else '⚠️ Pendiente'}"
        )
    else:  # casa_inteligente
        resumen = f"🏠 Casa Inteligente - {datos.get('nombre_completo', 'Sin nombre')}"
        descripcion = (
            f"📅 Solicitado el: {fecha_solicitud}\n"
            f"👤 Cliente: {datos.get('nombre_completo', 'N/D')}\n"
            f"📞 Teléfono: {datos.get('telefono', 'N/D')}\n"
            f"📍 Dirección: {datos.get('direccion', 'N/D')}"
        )

    service = get_calendar_service()
    evento = {
        'summary': resumen,
        'description': descripcion,
        'start': {'dateTime': inicio_iso, 'timeZone': 'America/Mexico_City'},
        'end': {'dateTime': fin_iso, 'timeZone': 'America/Mexico_City'},
    }
    evento_creado = service.events().insert(calendarId=calendar_id, body=evento).execute()
    return evento_creado.get('htmlLink')