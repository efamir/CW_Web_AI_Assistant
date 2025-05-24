const textStartButton = document.getElementById("textStart");
const textEndButton =  document.getElementById("textEnd");
const textSendButton =  document.getElementById("textSend");
const micStart = document.getElementById("micStart");
const textContainer = document.getElementById("inputDiv");
const inputField = document.getElementById("textInput");
const stopVoice = document.getElementById("stopVoice");
const containerStartMessage = document.getElementById("startMessage");
const dnone = 'd-none'

textStartButton.addEventListener("click", (event) => {
    micStart.classList.add(dnone);
    containerStartMessage.classList.add(dnone);
    textStartButton.classList.add(dnone);
    textEndButton.classList.remove(dnone);
    textSendButton.classList.remove(dnone);
    textContainer.classList.remove(dnone);
})

textEndButton.addEventListener('click', (event) => {
    micStart.classList.remove(dnone);
    containerStartMessage.classList.remove(dnone)
    textStartButton.classList.remove(dnone);
    textEndButton.classList.add(dnone);
    textSendButton.classList.add(dnone);
    textContainer.classList.add(dnone);
})

stopVoice.addEventListener("click", () => {
        stopAudio();
    });

const audioContainer = document.createElement("div");
document.body.appendChild(audioContainer);

let currentAudio = null;

textSendButton.addEventListener('click', async (event) => {
    const textValue = inputField.value.trim();
    if (textValue) {
        document.getElementById("loadingGif").classList.remove("d-none");

        await sendText(textValue);

        document.getElementById("loadingGif").classList.add("d-none");
        inputField.value = "";
    }
});


async function sendText(text) {
    const token = localStorage.getItem("token");


    try {
        const response = await fetch("/process_text", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                token: token,
                prompt: text
            }),
        });

        if (!response.ok) {
            throw new Error(`Помилка сервера: ${response.status}`);
        }
        const data = await response.json();

         if (data.timer_timestamp) {
            addTimer("Timer",data.timer_timestamp);
        }
        console.log("Response text:", data.response_text);
        console.log("Audio file path:", data.audio_file_path);
        console.log("Timer timestamp:", data.timer_timestamp);

        playAudio(data.audio_file_path);

    } catch (error) {
        console.error("Помилка відправлення тексту:", error);
        alert("Не вдалося звернутися до помічника");
    }
}

function playAudio(audioPath) {
    stopAudio();
    stopVoice.classList.remove(dnone);

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
    stopVoice.classList.add(dnone);

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