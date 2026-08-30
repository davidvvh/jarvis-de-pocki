import os
import subprocess
import pyttsx3
import speech_recognition as sr
from google import genai

#configuracion de API y voz
API_KEY = "AQ.Ab8RN6LIWzmHWipIgClYKsOQdEN5GLmRkAtv1CueQZgmpXDA0w"
client = genai.Client(api_key=API_KEY)

PALABRA_CLAVE = ["despierta deki"]

engine = pyttsx3.init()
voices = engine.getProperty('voices')

for voice in voices:
    if "spanish" in voice.name.lower() or "es" in voice.id.lower():
        engine.setProperty('voice', voice.id)
        break

engine.setProperty('rate', 160)

def hablar(texto):
    print(f"Asistente: {texto}")
    engine.say(texto)
    engine.runAndWait()

def escuchar():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.8)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
            texto = recognizer.recognize_google(audio, language="es-ES")
            return texto.lower()
        except (sr.UnknownValueError, sr.WaitTimeoutError):
            return ""
        except sr.RequestError:
            return ""

#control del telefono mediante ADB
def ejecutar_comando_adb(comando):
    try:
        resultado = subprocess.run(f"adb {comando}", shell=True, capture_output=True, text=True)
        return resultado.stdout
    except Exception as e:
        print(f"Error ADB: {e}")
        return None

def encender_pantalla_telefono():
    ejecutar_comando_adb("shell input keyevent 224")

def buscar_en_telefono(texto_busqueda):
    encender_pantalla_telefono()
    query_formateada = texto_busqueda.replace(" ", "+")
    url = f"https://www.google.com/search?q={query_formateada}"
    #envia el comando al telefono para abrir la url
    ejecutar_comando_adb(f'shell am start -a android.intent.action.VIEW -d "{url}"')

def consultar_gemini(prompt):
    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )
        return response.text
    except Exception:
        return "Tuve un problema al procesar la solicitud."

#bucle principal del asistente
def iniciar_asistente():
    print(">>> Asistente activo con soporte para teléfono (ADB)...")
    while True:
        oído = escuchar()
        if any(palabra in oído for palabra in PALABRA_CLAVE):
            hablar("Te escucho, ¿qué necesitas?")
            orden = escuchar()
            if not orden:
                continue
            if "apagar asistente" in orden or "cerrar programa" in orden:
                hablar("Desactivando asistente.")
                break
            #comando especifico para interactuar con el telefono
            if "busca en mi teléfono" in orden or "busca en el celular" in orden:
                termino = orden.replace("busca en mi teléfono", "").replace("busca en el celular", "").strip()
                if termino:
                    hablar(f"Buscando {termino} en tu teléfono.")
                    buscar_en_telefono(termino)
                else:
                    hablar("¿Qué te gustaría que busque en el teléfono?")
            else:
                respuesta = consultar_gemini(orden)
                hablar(respuesta)

if __name__ == "__main__":
    iniciar_asistente()