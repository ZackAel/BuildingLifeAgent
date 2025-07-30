if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('service-worker.js');
}

const notifyBtn = document.getElementById('notifyBtn');
notifyBtn.addEventListener('click', async () => {
    if (!('Notification' in window)) return;
    const permission = await Notification.requestPermission();
    if (permission === 'granted') {
        new Notification('Notifications enabled!');
    }
});
