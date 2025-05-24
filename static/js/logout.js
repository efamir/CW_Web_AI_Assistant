document.addEventListener('DOMContentLoaded', (event) => {
    document.getElementById("logout").addEventListener("click",(event) => {
                    localStorage.removeItem("token");
                    localStorage.removeItem("timers");
                    window.location.href = '/login-page';
                });
});