// global-timer-checker.js
const isTimersPage = document.getElementById('timers-page') !== null;


function getTimers() {
    return JSON.parse(localStorage.getItem('timers') || '[]');
}

function formatTime(ms) {
    if (ms <= 0) return "00 хв 00 сек";
    const totalSeconds = Math.floor(ms / 1000);
    const minutes = String(Math.floor(totalSeconds / 60)).padStart(2, '0');
    const seconds = String(totalSeconds % 60).padStart(2, '0');
    return `${minutes} хв ${seconds} сек`;
}


function showNotification(timer) {
    const oldPopup = document.getElementById('customCenterPopup');
    if (oldPopup) oldPopup.remove();

    const popup = document.createElement('div');
    popup.id = 'customCenterPopup';
    popup.style.position = 'fixed';
    popup.style.top = '50%';
    popup.style.left = '50%';
    popup.style.transform = 'translate(-50%, -50%)';
    popup.style.background = '#ffffff';
    popup.style.padding = '24px 32px';
    popup.style.borderRadius = '12px';
    popup.style.boxShadow = '0 10px 30px rgba(0,0,0,0.3)';
    popup.style.zIndex = '9999';
    popup.style.maxWidth = '90%';
    popup.style.textAlign = 'center';

    const h2 = document.createElement('h2');
    h2.innerText = "Timer out!";
    h2.style.marginBottom = '12px';
    popup.appendChild(h2);

    const p = document.createElement('p');
    p.innerText = timer.name;
    p.style.marginBottom = '20px';
    p.style.fontSize = '16px';
    popup.appendChild(p);

    const closeBtn = document.createElement('button');
    closeBtn.innerText = 'Закрити';
    closeBtn.style.padding = '8px 16px';
    closeBtn.style.background = '#007bff';
    closeBtn.style.color = '#fff';
    closeBtn.style.border = 'none';
    closeBtn.style.borderRadius = '6px';
    closeBtn.style.cursor = 'pointer';
    closeBtn.onclick = () => popup.remove();
    popup.appendChild(closeBtn);

    document.body.appendChild(popup);

    /* setTimeout(() => {
        popup.remove();
    }, 5000); */
}


   

function playSound() {
    const audio = new Audio('static/sounds/notify.mp3'); 
    audio.play();
}

//  Основна логіка
setInterval(() => {
    const now = Date.now();
    const timers = getTimers();
    let updatedTimers = [];

    for (let timer of timers) {
        const timeLeft = timer.expiresAt - now;
        

        if (timeLeft <= 0 && !timer.notified) {
            showNotification(timer);
            playSound();
            timer.notified = true;
        }

        if (isTimersPage) {
            const el = document.querySelector(`.timer-remaining[data-id="${timer.id}"]`);
            if (el) {
                el.textContent = formatTime(timeLeft);
            }
        }

        updatedTimers.push(timer);
    }

    localStorage.setItem('timers', JSON.stringify(updatedTimers));
}, 1000);


