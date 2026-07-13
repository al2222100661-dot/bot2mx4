from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime

SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = 'bot2mx4-da1510566782.json'

def get_calendar_service():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
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
    Devuelve True si está libre, False si ya hay algo agendado.
    """
    service = get_calendar_service()
    eventos_result = service.events().list(
        calendarId=calendar_id,
        timeMin=inicio_iso,
        timeMax=fin_iso,
        singleEvents=True
    ).execute()

    eventos = eventos_result.get('items', [])
    return len(eventos) == 0