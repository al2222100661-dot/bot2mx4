from dotenv import load_dotenv
load_dotenv()

from app.database import crear_tablas

crear_tablas()
print("Tablas creadas correctamente ✅")
