# backend/server.py
# VERSIÓN FINAL: Integra Google Speech-to-Text y Gemini para una experiencia completa.

import os
import subprocess
import json
import difflib
import google.generativeai as genai
from flask import Flask
from flask_cors import CORS
from flask_sock import Sock
from google.cloud import speech
from google.api_core import exceptions as google_exceptions

# --- CONFIGURACIÓN DE APIS ---

# 1. API Key de Gemini (Consíguela en Google AI Studio)
# Pega tu clave aquí. ¡Mantenla en secreto!
GEMINI_API_KEY = "AIzaSyAoiYjLKFBF80sC34B7oDSnMe-yLM0w1z0"
genai.configure(api_key=GEMINI_API_KEY)

# 2. Credenciales de Google Cloud Speech-to-Text
CREDENTIALS_PATH = 'google_credentials.json'
if not os.path.exists(CREDENTIALS_PATH):
    print("="*50)
    print(f"¡ERROR CRÍTICO! No se encontró el archivo de credenciales: {CREDENTIALS_PATH}")
    print("El servidor no podrá conectarse a Google Cloud.")
    print("="*50)
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = CREDENTIALS_PATH

# --- INICIALIZACIÓN DE LA APP ---
app = Flask(__name__)
CORS(app)
sock = Sock(app)

# --- MODELO DE GEMINI Y MEMORIA DE CHAT ---
model = genai.GenerativeModel('gemini-1.5-flash-latest')
chat_session = model.start_chat(history=[])

def load_commands():
    """Carga la lista de comandos desde el archivo commands.json."""
    try:
        json_path = os.path.join(os.path.dirname(__file__), 'commands.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            print(f"Cargando comandos desde {json_path}...")
            return json.load(f)
    except FileNotFoundError:
        print("ADVERTENCIA: No se encontró 'commands.json'. Las funciones para abrir apps no estarán disponibles.")
        return {}
    except json.JSONDecodeError:
        print("ERROR: El archivo 'commands.json' está mal formado.")
        return {}

COMMANDS = load_commands()

@sock.route('/audio')
def audio_socket(ws):
    """Maneja la conexión WebSocket para recibir audio y procesarlo."""
    print("Cliente conectado. Inicializando Google Speech-to-Text...")
    try:
        client = speech.SpeechClient()
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="es-ES",
            enable_automatic_punctuation=True
        )
        streaming_config = speech.StreamingRecognitionConfig(config=config, interim_results=False)
        print("Cliente de Google Speech-to-Text inicializado correctamente.")
    except google_exceptions.DefaultCredentialsError as e:
        error_msg = f"¡ERROR DE CREDENCIALES DE GOOGLE! Verifica tu archivo '{CREDENTIALS_PATH}'. Detalles: {e}"
        print(f"\n{'='*50}\n{error_msg}\n{'='*50}\n")
        return
    except Exception as e:
        print(f"Error al inicializar Google Speech-to-Text: {e}")
        return

    try:
        def audio_generator():
            while True:
                message = ws.receive()
                if message:
                    yield speech.StreamingRecognizeRequest(audio_content=message)

        responses = client.streaming_recognize(streaming_config, audio_generator())

        for response in responses:
            if not response.results or not response.results[0].alternatives: continue
            transcript = response.results[0].alternatives[0].transcript.strip()
            print(f"Texto recibido de Google: '{transcript}'")

            # Prioriza comandos de acción antes de chatear
            if transcript.lower().startswith("abre"):
                intent, data = "open_app", transcript[4:].strip()
                action = {"intent": intent, "data": data}
                final_response = execute_action(action)
            elif transcript.lower().startswith("busca"):
                intent, data = "search", transcript[5:].strip()
                action = {"intent": intent, "data": data}
                final_response = execute_action(action)
            else:
                # Si no es un comando, es una conversación para Gemini
                print("Enviando a Gemini para respuesta de chat...")
                gemini_response = chat_session.send_message(transcript)
                print(f"Respuesta de Gemini: '{gemini_response.text}'")
                final_response = {
                    "intent": "chat",
                    "message": gemini_response.text,
                    "data": transcript
                }
            
            ws.send(json.dumps(final_response))

    except Exception as e:
        print(f"Error durante la transmisión WebSocket: {e}")
    finally:
        print("Cliente desconectado.")


def execute_action(action):
    """Ejecuta la acción determinada y devuelve una respuesta para el frontend."""
    intent, target = action.get("intent"), action.get("data")
    response_message = ""
    
    if intent == "open_app":
        best_matches = difflib.get_close_matches(target, list(COMMANDS.keys()), n=1, cutoff=0.6)
        if best_matches:
            found_key = best_matches[0]
            command_to_run = COMMANDS[found_key]
            try:
                subprocess.Popen(command_to_run, shell=True)
                response_message = f"Entendido. Abriendo {found_key}."
            except Exception:
                response_message = f"Encontré {found_key}, pero hubo un error al abrirlo."
        else:
            response_message = f"Lo siento, no encontré un comando similar a '{target}'."
    elif intent == "search":
        response_message = f"Buscando '{target}' en Google."
    
    return {"intent": intent, "message": response_message, "data": target}

if __name__ == '__main__':
    # --- CORREGIDO: Compara con el texto de ejemplo, no con tu clave ---
    if GEMINI_API_KEY == "PEGA_TU_API_KEY_DE_GEMINI_AQUÍ":
        print("="*50)
        print("¡ADVERTENCIA! No has configurado tu API Key de Gemini en server.py.")
        print("El chat no funcionará hasta que edites el archivo.")
        print("="*50)
    
    print("Servidor JARVIS (Google Cloud STT + Gemini) iniciado en http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
