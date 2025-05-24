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

function removeTimerById(id) {
    let timers = JSON.parse(localStorage.getItem('timers') || '[]');
    timers = timers.filter(t => t.id !== id);
    localStorage.setItem('timers', JSON.stringify(timers));
}

function getAllTimers() {
    return JSON.parse(localStorage.getItem('timers') || '[]');
}

function clearAllTimers() {
    localStorage.removeItem('timers');
}
