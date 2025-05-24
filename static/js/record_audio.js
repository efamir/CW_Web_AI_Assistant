let mediaRecorder;
let audioChunks = [];
let stream;
let audioContext;
let analyser;
let source;
let dataArray;
let rafId;

const buttonStart = document.getElementById("micStart");
const buttonStop = document.getElementById("micStop");
const buttonTextStart = document.getElementById("textStart")
const divStartMessage = document.getElementById("startMessage");
const canvas = document.getElementById('voiceVisualizer');
const voiceStop = document.getElementById("stopVoice");
const canvasCtx = canvas.getContext('2d');

function setupVisualizer(audioStream) {
    if (!audioContext) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
    }
    analyser = audioContext.createAnalyser();
   
    analyser.fftSize = 128;

    const bufferLength = analyser.frequencyBinCount; 
    dataArray = new Uint8Array(bufferLength); 

    source = audioContext.createMediaStreamSource(audioStream);
    source.connect(analyser);

    drawBars();
}

function stopVisualizer() {
    if (rafId) {
        cancelAnimationFrame(rafId);
    }
    if (source) source.disconnect();
    if (analyser) analyser.disconnect();
    if (canvasCtx && canvas) {
        canvasCtx.clearRect(0, 0, canvas.width, canvas.height);
    }
}

function drawBars() {
    rafId = requestAnimationFrame(drawBars);

    analyser.getByteFrequencyData(dataArray);

   
    canvasCtx.fillStyle = '#f8f9fa'; 
    canvasCtx.fillRect(0, 0, canvas.width, canvas.height);

    const barWidth = (canvas.width / dataArray.length) * 1.5; 
    let barHeight;
    let x = 0;
    const centerY = canvas.height / 1.5; 

    for (let i = 0; i < dataArray.length; i++) {
        
        barHeight = dataArray[i] / 1.5; 
                                      

        if (barHeight > centerY) {
            barHeight = centerY;
        }

        const r = barHeight + (25 * (i/dataArray.length));
        const g = 50 + 50 * (i/dataArray.length); 
        const b = 150 + barHeight / 2;
        canvasCtx.fillStyle = `rgb(${Math.min(255, r)}, ${Math.min(255, g)}, ${Math.min(255, b)})`;
        


        
        canvasCtx.fillRect(
            x,                      
            centerY - barHeight / 2, 
            barWidth,               
            barHeight               
        );

        x += barWidth + 1;
    }
}

buttonStart.addEventListener("click", async () => {
    try {
        stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        let options = {};
        if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
            options.mimeType = 'audio/webm;codecs=opus';
        } else if (MediaRecorder.isTypeSupported('audio/ogg;codecs=opus')) {
            options.mimeType = 'audio/ogg;codecs=opus';
        } 
        mediaRecorder = new MediaRecorder(stream, options);
        console.log("Using MIME type:", mediaRecorder.mimeType);


        audioChunks = [];

        buttonStart.classList.add("d-none");
        containerStartMessage.classList.add("d-none");
        buttonStop.classList.remove("d-none");
        buttonTextStart.classList.add('d-none');

        setupVisualizer(stream); 

        mediaRecorder.ondataavailable = event => {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
            }
        };

        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: mediaRecorder.mimeType });
            console.log("Розмір аудіо Blob:", audioBlob.size);

            stopVisualizer(); 

            document.getElementById("loadingGif").classList.remove("d-none");
            await sendAudio(audioBlob);
            document.getElementById("loadingGif").classList.add("d-none");
            
            stream.getTracks().forEach(track => track.stop());

            buttonStop.classList.add("d-none");
            containerStartMessage.classList.remove("d-none");
            buttonStart.classList.remove("d-none");
            buttonTextStart.classList.remove('d-none');
        };

        mediaRecorder.start();
        console.log("Запис розпочато");
    } catch (err) {
        console.error("Помилка доступу до мікрофона:", err);
        buttonStop.classList.add("d-none");
        buttonStart.classList.remove("d-none");
    }
});

buttonStop.addEventListener("click", () => {
    if (mediaRecorder && mediaRecorder.state === "recording") {
        mediaRecorder.stop();
    }
});




async function sendAudio(blob) {
    if (!(blob instanceof Blob)) {
        console.error("Некоректний Blob:", blob);
        return;
    }
    const token = localStorage.getItem("token");
    const formData = new FormData();
    formData.append("file", blob, "recorded_audio.webm");
    formData.append("token", token);
    try {
        const response = await fetch("/process_audio", {
            method: "POST",
            body: formData
        });

        if (!response.ok) throw new Error("Помилка при надсиланні");

        const result = await response.json();
        console.log("Отримано відповідь від помічника:", result);

        if (result.audio_file_path) {
            playAudio(result.audio_file_path);
        }

        if (result.timer_timestamp) {
            addTimer("Timer",result.timer_timestamp);
        }

        if (result.response_text) {
            console.log(" Помічник сказав:", result.response_text);
        }

    } catch (err) {
        console.error("Помилка відправлення:", err);
        alert("Не вдалося надіслати аудіо.");
    }
}



function playAudio(audioPath) {
    stopAudio();
    voiceStop.classList.remove("d-none");
    
    currentAudio = new Audio(audioPath);
    currentAudio.addEventListener('ended', () => {
            console.log("ended");
            stopVoice.classList.add(dnone);
        });
    currentAudio.play().catch(e => console.warn("Не вдалося відтворити аудіо:", e));
}

function stopAudio() {
    if (currentAudio) {
        currentAudio.pause();
        currentAudio.currentTime = 0;
    }
    voiceStop.classList.add("d-none");
}

function addTimer(name, ms) {
    const timers = JSON.parse(localStorage.getItem('timers') || '[]');
    const newTimer = {
        id: crypto.randomUUID(),
        name,
        expiresAt: ms
    };
    timers.push(newTimer);
    localStorage.setItem('timers', JSON.stringify(timers));
    return newTimer;
}