// frontend/script.js
// VERSIÓN FINAL: Captura audio, lo envía al servidor y maneja errores.

const BACKEND_URL = 'ws://127.0.0.1:5000/audio';

const jarvisOrb = document.getElementById('jarvisOrb');
const startButton = document.getElementById('startButton');
const statusEl = document.getElementById('status');
const transcriptEl = document.getElementById('transcript');
const responseEl = document.getElementById('response');

let isListening = false;
let socket;
let audioContext;
let processor;
let input;
let stream;

function toggleListening() {
    isListening ? stopListening() : startListening();
}

async function startListening() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        alert('Tu navegador no soporta la captura de audio.');
        return;
    }

    isListening = true;
    startButton.textContent = "Detener Reconocimiento";
    statusEl.textContent = 'Estado: Conectando...';
    jarvisOrb.classList.add('listening');

    socket = new WebSocket(BACKEND_URL);

    socket.onopen = async () => {
        statusEl.textContent = 'Estado: Escuchando...';
        try {
            stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
            audioContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 44100 });
            input = audioContext.createMediaStreamSource(stream);
            processor = audioContext.createScriptProcessor(4096, 1, 1);

            processor.onaudioprocess = (e) => {
                if (socket.readyState === WebSocket.OPEN) {
                    const audioData = e.inputBuffer.getChannelData(0);
                    const pcmData = downsampleBuffer(audioData, audioContext.sampleRate, 16000);
                    socket.send(pcmData);
                }
            };
            input.connect(processor);
            processor.connect(audioContext.destination);
        } catch (err) {
            console.error("Error al iniciar el audio:", err);
            statusEl.textContent = "Error: No se pudo acceder al micrófono.";
            stopListening();
        }
    };

    socket.onmessage = (event) => {
        const response = JSON.parse(event.data);
        console.log("Respuesta recibida:", response);

        if (response.error) {
            console.error("Error del servidor:", response.error);
            responseEl.textContent = `JARVIS: Error - ${response.error}`;
            speak(`He encontrado un error en el servidor: ${response.error}`);
            stopListening();
            return;
        }

        transcriptEl.textContent = `Tú: (Voz procesada)`;
        responseEl.textContent = `JARVIS: ${response.message}`;
        
        if (response.intent === 'search') {
            window.open(`https://www.google.com/search?q=${encodeURIComponent(response.data)}`, '_blank');
        }
        speak(response.message);
    };

    socket.onclose = () => {
        statusEl.textContent = 'Estado: Desconectado';
        if (isListening) stopListening();
    };

    socket.onerror = (error) => {
        console.error('Error de WebSocket:', error);
        statusEl.textContent = 'Error de conexión';
        if (isListening) stopListening();
    };
}

function stopListening() {
    isListening = false;
    startButton.textContent = "Iniciar Reconocimiento";
    jarvisOrb.classList.remove('listening');
    statusEl.textContent = 'Estado: Inactivo';

    if (socket) socket.close();
    if (processor) processor.disconnect();
    if (input) input.disconnect();
    if (audioContext) audioContext.close();
    if (stream) stream.getTracks().forEach(track => track.stop());
    
    processor = input = audioContext = stream = null;
}

function downsampleBuffer(buffer, inputRate, outputRate) {
    if (inputRate === outputRate) { // Si las tasas ya coinciden, solo convierte a Int16
        const result = new Int16Array(buffer.length);
        for (let i = 0; i < buffer.length; i++) {
            result[i] = Math.min(1, buffer[i]) * 0x7FFF;
        }
        return result.buffer;
    }
    const rateRatio = inputRate / outputRate;
    const newLength = Math.round(buffer.length / rateRatio);
    const result = new Int16Array(newLength);
    let offsetResult = 0;
    let offsetBuffer = 0;
    while (offsetResult < result.length) {
        const nextOffsetBuffer = Math.round((offsetResult + 1) * rateRatio);
        let accum = 0, count = 0;
        for (let i = offsetBuffer; i < nextOffsetBuffer && i < buffer.length; i++) {
            accum += buffer[i];
            count++;
        }
        result[offsetResult] = Math.min(1, accum / count) * 0x7FFF;
        offsetResult++;
        offsetBuffer = nextOffsetBuffer;
    }
    return result.buffer;
}

jarvisOrb.addEventListener('click', toggleListening);
startButton.addEventListener('click', toggleListening);

function speak(text) {
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'es-ES';
    utterance.pitch = 0.8;
    utterance.rate = 1.1;
    window.speechSynthesis.speak(utterance);
}
