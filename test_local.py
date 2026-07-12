"""
BOT2MX4 - Prueba local del bot en terminal
Corre esto para probar el bot antes de conectarlo a Facebook.

Uso:
    python test_local.py
"""

from app.brain import get_response, clear_history

print("=" * 55)
print("  🤖 BOT2MX4 - Modo prueba local")
print("  Escribe 'salir' para terminar")
print("  Escribe 'reset' para reiniciar la conversación")
print("=" * 55)

TEST_USER = "usuario_prueba"

while True:
    try:
        user_input = input("\n🧑 Tú: ").strip()

        if not user_input:
            continue

        if user_input.lower() == "salir":
            print("👋 ¡Hasta luego!")
            break

        if user_input.lower() == "reset":
            clear_history(TEST_USER)
            print("🔄 Conversación reiniciada")
            continue

        response = get_response(TEST_USER, user_input)
        print(f"\n🤖 Bot2MX4: {response}")

    except KeyboardInterrupt:
        print("\n\n👋 Bot detenido")
        break
