function removeTimerById(id) {
    let timers = JSON.parse(localStorage.getItem('timers') || '[]');
    timers = timers.filter(t => t.id !== id);
    localStorage.setItem('timers', JSON.stringify(timers));
    location.reload(); 
}


function addTimer(name, ms) {
    const timers = JSON.parse(localStorage.getItem('timers') || '[]');
    const newTimer = {
        id: crypto.randomUUID(),
        name,
        expiresAt: Date.now() + ms
    };
    timers.push(newTimer);
    localStorage.setItem('timers', JSON.stringify(timers));
    return newTimer;
}

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('addTimerForm');
    const saveBtn = document.getElementById('saveTimerButton');
    const timersContainer = document.getElementById('timersListContainer');
    const noTimersMsg = document.getElementById('noTimersMessage');

    saveBtn.addEventListener('click', () => {
        const name = document.getElementById('timerNameInput').value.trim();
        const hours = parseInt(document.getElementById('timerHoursInput').value) || 0;
        const minutes = parseInt(document.getElementById('timerMinutesInput').value) || 0;
        const seconds = parseInt(document.getElementById('timerSecondsInput').value) || 0;

        const totalMs = (hours * 3600 + minutes * 60 + seconds) * 1000;
        if (totalMs <= 0) {
            alert("Таймер має бути більше 0 секунд.");
            return;
        }

        const timer = addTimer(name,totalMs);
        addTimerToDOM(timer);
        noTimersMsg.style.display = 'none';
        const modal = bootstrap.Modal.getInstance(document.getElementById('addTimerModal'));
        modal.hide();
        form.reset();
    });

    function addTimerToDOM(timer) {
        const timeLeft = Math.max(0, timer.expiresAt - Date.now());
        const minutes = Math.floor(timeLeft / 60000);
        const seconds = Math.floor((timeLeft % 60000) / 1000);

        const col = document.createElement('div');
        col.className = 'col-md-6 col-lg-4';
        col.innerHTML = `
            <div class="card timer-card shadow-sm">
                <div class="card-body">
                    <h5 class="card-title">${timer.name}</h5>
                    <p class="card-text">Залишилось: <span class="timer-remaining" data-id="${timer.id}">${minutes} хв ${seconds} сек</span></p>
                    <button class="btn btn-sm btn-outline-danger" onclick="removeTimer('${timer.id}')"><i class="bi bi-trash"></i> Видалити</button>
                </div>
            </div>`;
        timersContainer.appendChild(col);
    }

    window.removeTimer = removeTimerById;

    const loadTimers = () => {
        const timers = JSON.parse(localStorage.getItem('timers') || '[]');
        if (timers.length === 0) {
            noTimersMsg.style.display = 'block';
        } else {
            timers.forEach(addTimerToDOM);
        }
    };



    loadTimers();
});

