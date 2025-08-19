Asistente de Escritorio JARVIS (v2 - Google Cloud)
Esta versión utiliza la API de Google Cloud Speech-to-Text para un reconocimiento de voz de alta precisión.

Requisitos Previos
Python 3 y pip.

Cuenta de Google Cloud con facturación habilitada.

Archivo de credenciales de Google Cloud (ver guía).

Navegador Moderno (Chrome/Firefox/Edge).

Pasos para la Instalación y Ejecución
Paso 1: Configurar el Backend
Coloca tus credenciales: Renombra tu archivo de credenciales JSON a google_credentials.json y ponlo dentro de la carpeta backend.

Abre una terminal en la carpeta backend.

(Recomendado) Crea y activa un entorno virtual:

python -m venv venv

En Windows: venv\Scripts\activate

Instala las nuevas dependencias:

pip install -r requirements.txt

Esto instalará las librerías de Google Cloud, Flask y WebSockets.

(Opcional) Escanea tus aplicaciones: Si quieres que JARVIS abra programas locales, ejecuta el escáner para generar el archivo commands.json:

python scan_apps.py

Paso 2: Ejecutar el Servidor Backend
En la misma terminal (dentro de backend), inicia el servidor principal:

python server.py

Verás un mensaje indicando que el servidor está listo. Mantén esta terminal abierta.

Paso 3: Ejecutar el Servidor Frontend
Abre una SEGUNDA terminal.

Navega a la carpeta frontend:

cd ../frontend

Inicia el servidor web simple de Python:

python -m http.server

Mantén esta segunda terminal abierta también.

Paso 4: Usar JARVIS
Abre tu navegador y ve a la dirección: http://localhost:8000.

Haz clic en el orbe para iniciar la conversación.

¡Listo! Ahora estás usando una versión mucho más potente y precisa de JARVIS.