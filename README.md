# 🤖 Bot2MX4 (con Google Gemini — GRATIS)

Bot inteligente para negocios vía Facebook Messenger.
Potenciado por **Google Gemini Flash** (gratuito).

---

## ⚡ Instalación rápida

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar variables
cp .env.example .env
# Edita .env con tu GEMINI_API_KEY
```

---

## 🔑 Cómo obtener tu API Key de Gemini GRATIS

1. Ve a: **aistudio.google.com/app/apikey**
2. Inicia sesión con tu cuenta de Google
3. Clic en **"Create API Key"**
4. Copia la key y pégala en tu `.env`:
```
GEMINI_API_KEY=AIzaxxxxxxxxxxxxxxxx
```

---

## 🧪 Probar el bot en terminal

```bash
python test_local.py
```

---

## 🚀 Correr el servidor

```bash
uvicorn main:app --reload --port 8000
```

---

## 📁 Estructura

```
bot2mx4/
├── main.py              → Servidor FastAPI
├── test_local.py        → Prueba en terminal
├── requirements.txt     → Dependencias
├── .env.example         → Variables de entorno
├── app/
│   ├── brain.py         → Gemini API + memoria
│   └── messenger.py     → Facebook Messenger
└── config/
    └── business.py      → Config del negocio cliente ← edita esto por cliente
```

---

## 🔧 Configurar para cada cliente

Edita `config/business.py` con:
- Nombre del negocio
- Servicios y precios
- Horarios
- FAQs

---

## 💡 Límites gratuitos de Gemini Flash

- ✅ 15 requests por minuto
- ✅ 1,000,000 tokens por día
- ✅ Completamente gratis

Para un negocio chico con 100-200 mensajes al día, **nunca llegarás al límite**.

---

**Bot2MX4** — Automatiza tu atención al cliente 🚀
