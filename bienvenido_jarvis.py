#!/usr/bin/env python3
"""
Double-clap welcome script for Señor Tatay (Windows 11).

Detects 2 claps → voz AI dice bienvenido → abre YouTube → Claude + Cursor lado a lado.

Dependencias:
    pip install sounddevice numpy pyttsx3 pygetwindow
"""

import os
import sys
import time
import threading
import subprocess
import webbrowser

import speech_recognition as sr
import pyttsx3
import pygetwindow as gw

# ──────────────────────────────────────────────────────────────────────────────
#  Configuración
# ──────────────────────────────────────────────────────────────────────────────
PALABRA_CLAVE = "hola"
YOUTUBE_URL    = "https://www.youtube.com/watch?v=hEIexwwiKKU"
PINTEREST_URL = "https://cl.pinterest.com/"
MENSAJE        = "Bienvenido a casa, señor pocki."
NEW_PROJECT    = os.path.expanduser("~/Desktop/nuevo_proyecto")

# ──────────────────────────────────────────────────────────────────────────────
#  Estado global
# ──────────────────────────────────────────────────────────────────────────────
triggered = False


# ──────────────────────────────────────────────────────────────────────────────
#  Detección de aplausos
# ──────────────────────────────────────────────────────────────────────────────
def escuchar_palabra_clave():
    global triggered

    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True

    with sr.Microphone() as source:
        print("Calibrando ruido ambiental... Por favor espera unos segundos.")
        recognizer.adjust_for_ambient_noise(source, duration=2)
        print("=" * 60)
        print("Escuchando... Di '{PALABRA_CLAVE.upper()}' para activar la secuencia.")
        print(" (Presiona Ctrl+C para salir)")
        print("=" * 60)

        while True:
            if triggered:
                time.sleep(1)
                continue

            try:
                audio = recognizer.listen(source, timeout=None, phrase_time_limit=4)
                texto = recognizer.recognize_google(audio, language="es-ES").lower()
                print(f"Escuchando: \"{texto}\"")

                if PALABRA_CLAVE.lower() in texto:
                    print(f"\n ¡Palabra clave '{PALABRA_CLAVE}' detectada!")
                    triggered = True
                    threading.Thread(target=secuencia_bienvenida, daemon=True).start()

            except sr.UnknownValueError:
                pass
            except sr.RequestError as e:
                print(f"\n Error al conectar con el servicio de reconocimiento: {e}")
                time.sleep(2)


# ──────────────────────────────────────────────────────────────────────────────
#  Secuencia de bienvenida
# ──────────────────────────────────────────────────────────────────────────────
def secuencia_bienvenida():
    global triggered
    print("\n🚀  Iniciando secuencia de bienvenida…\n")

    hablar(MENSAJE)
    abrir_youtube()
    abrir_apps_lado_a_lado()

    print("\n✅  Secuencia completada.\n")
    time.sleep(5)
    triggered = False
    print(f"\n Escuchando de nuevo... (Di '{PALABRA_CLAVE}')\n")


def hablar(texto: str):
    """TTS usando SAPI5 nativo de Windows 11."""
    print(f"  🔊  Diciendo: «{texto}»")
    try:
        engine = pyttsx3.init(driverName="sapi5")
        voices = engine.getProperty("voices")

        # Intenta seleccionar una voz en español (ej. Helena, Sabina o Laura en Windows)
        esp = [v for v in voices if "spanish" in v.name.lower() or "es-" in v.id.lower() or "elena" in v.name.lower()]
        if esp:
            engine.setProperty("voice", esp[0].id)

        engine.setProperty("rate", 160)
        engine.say(texto)
        engine.runAndWait()
    except Exception as e:
        print(f"  ⚠️ Error en TTS: {e}")


def abrir_youtube():
    print(f"  🎵  Abriendo YouTube…")
    webbrowser.open(YOUTUBE_URL)
    time.sleep(1.5)


def abrir_apps_lado_a_lado():
    os.makedirs(NEW_PROJECT, exist_ok=True)

    print("  📌  Abriendo Pinterest en el navegador…")
    webbrowser.open(PINTEREST_URL)
    time.sleep(2.0)

    print("  💻  Abriendo Cursor…")
    # Abre Cursor con la carpeta del proyecto
    subprocess.Popen(["cmd", "/c", "cursor", NEW_PROJECT], shell=True)
    time.sleep(2.5)

    print("  🪟  Organizando ventanas lado a lado…")
    organizar_ventanas_windows()


def organizar_ventanas_windows():
    """Posiciona las ventanas de Claude y Cursor en Windows 11 (pantalla dividida 50/50)."""
    try:
        # Obtiene todas las ventanas activas
        ventanas = gw.getAllWindows()
        
        win_navegador = None
        win_cursor = None

        navegadores = ["chrome", "edge", "firefox", "brave", "opera", "pinterest"]

        for w in ventanas:
            titulo = w.title.lower()
            if any(nav in titulo for nav in navegadores):
                win_navegador = w
            elif "cursor" in titulo:
                win_cursor = w

        # Obtiene la resolución de la pantalla principal (asumiendo 1920x1080 si no se detecta)
        pantalla_ancho = 1920
        pantalla_alto = 1080
        mitad = pantalla_ancho // 2

        if win_navegador:
            win_navegador.restore()
            win_navegador.moveTo(0, 0)
            win_navegador.resizeTo(mitad, pantalla_alto - 40)

        if win_cursor:
            win_cursor.restore()
            win_cursor.moveTo(mitad, 0)
            win_cursor.resizeTo(mitad, pantalla_alto - 40)

    except Exception as e:
        print(f"  ⚠️ No se pudieron organizar automáticamente las ventanas: {e}")


# ──────────────────────────────────────────────────────────────────────────────
#  Main
# ──────────────────────────────────────────────────────────────────────────────
def main():
    try:
        escuchar_palabra_clave()
    except KeyboardInterrupt:
        print("\n\nHasta luego!")
        sys.exit(0)


if __name__ == "__main__":
    main()