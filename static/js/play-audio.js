document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('voiceVisualizer');
    const canvasCtx = canvas.getContext('2d');
    const statusMessageElement = document.getElementById('statusMessage');
    const playButton = document.getElementById('playFetchedAudioButton');

    let audioContext;
    let analyser;
    let bufferSourceNode; // Для відтворення з AudioBuffer
    let dataArray;
    let rafId;

    function initAudioAndVisualizer() {
        if (!audioContext) { 
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
        }
        if (audioContext.state === 'suspended') {
            audioContext.resume().catch(err => console.error("AudioContext resume error:", err));
        }

        analyser = audioContext.createAnalyser();
        analyser.fftSize = 256; 
        const bufferLength = analyser.frequencyBinCount;
        dataArray = new Uint8Array(bufferLength);

        analyser.connect(audioContext.destination);
        console.log("AudioContext and Analyser initialized.");
    }

    function drawAudioVisualization() {
        if (!analyser || !bufferSourceNode || bufferSourceNode.playbackState !== AudioBufferSourceNode.PLAYING_STATE) {
            if (rafId) cancelAnimationFrame(rafId);
            rafId = null;
            if (canvasCtx && canvas) {
                 canvasCtx.fillStyle = '#f8f9fa';
                 canvasCtx.fillRect(0, 0, canvas.width, canvas.height);
            }
            return;
        }


        rafId = requestAnimationFrame(drawAudioVisualization);
        analyser.getByteFrequencyData(dataArray);

        canvasCtx.fillStyle = '#f8f9fa';
        canvasCtx.fillRect(0, 0, canvas.width, canvas.height);

        const barWidth = (canvas.width / dataArray.length) * 1.5;
        let barHeight;
        let x = 0;
        const centerY = canvas.height / 2;

        for (let i = 0; i < dataArray.length; i++) {
            barHeight = dataArray[i] / 1.8;
            if (barHeight > centerY * 0.95) barHeight = centerY * 0.95;

            const r = 50 + barHeight;
            const g = 100 + (dataArray.length - i) * 0.5;
            const b = 150 + i * 0.5;
            canvasCtx.fillStyle = `rgb(${Math.min(255,r)}, ${Math.min(255,g)}, ${Math.min(255,b)})`;
            canvasCtx.fillRect(x, centerY - barHeight / 2, barWidth, barHeight);
            x += barWidth + 1;
        }
    }

    async function playAudioFromBlob(audioBlob) {
        if (!audioBlob || audioBlob.size === 0) {
            statusMessageElement.textContent = "Помилка: отримано порожні аудіо дані.";
            console.error("Порожній Blob отримано.");
            return;
        }

        statusMessageElement.textContent = "Обробка аудіо...";

       
        initAudioAndVisualizer();

        try {
            const arrayBuffer = await audioBlob.arrayBuffer();
            const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);

            statusMessageElement.textContent = "Відтворення...";

            if (bufferSourceNode) {
                try { bufferSourceNode.stop(); } catch (e) {}
                bufferSourceNode.disconnect();
            }

            bufferSourceNode = audioContext.createBufferSource(); 
            bufferSourceNode.buffer = audioBuffer;                 

            bufferSourceNode.connect(analyser);

            bufferSourceNode.start(0); 
            drawAudioVisualization();  

            bufferSourceNode.onended = () => {
                statusMessageElement.textContent = "Відтворення завершено.";
                console.log("AudioBufferSourceNode finished playing.");
                if (rafId) cancelAnimationFrame(rafId);
                rafId = null;
                if (canvasCtx && canvas) {
                    canvasCtx.fillStyle = '#f8f9fa';
                    canvasCtx.fillRect(0, 0, canvas.width, canvas.height);
                }
                bufferSourceNode.disconnect(); 
            };

        } catch (error) {
            statusMessageElement.textContent = `Помилка декодування або відтворення аудіо: ${error.message}`;
            console.error("Помилка обробки аудіо:", error);
        }
    }
});