// виводить повідомлення про помилки авторизації
function showMessage(message_text){
    const message = document.getElementById("message");
    message.innerText = message_text;
    message.classList.remove("d-none");

    setTimeout(()=>{
        message.classList.add("d-none");
        message.innerText = '';
    }, 5000);
}

// оброблення логіну, викликає функцію запиту до серверу
async function handleSubmit(event) {
    event.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    if (!username){
        showMessage("Username required");
        return;
    }
    if (!password){
        showMessage("Password required");
        return;
    }

    try {
        const result = await loginCall(username, password); 
        if (result.status === "successful"){
            localStorage.setItem("token", result.token);
            location.href = "/main-page";
        
        } else if (result.status === "error") {
            showMessage(result.message);
        } else {
            showMessage("Something wrong with the response format.");
        }

    } catch (error) {
        console.error("Fail by fetch:", error);
        showMessage(error.message ||"Login failed.");
    }
}

// call api endpoint to login
async function loginCall(username, password) { 
    const backendUrl = '/login';

    try {
        const response = await fetch(backendUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (response.ok && data.token && data.success === true) {
            return { status: "successful", token: data.token };
        }
        else if (data.success === false) {
            if (data.error === "username") {
                return {
                    status: "error",
                    message: "Wrong username"
                };
            }
            else if (data.error === "password") {
                return {
                    status: "error",
                    message: "Wrong password"
                };
            }
        }

        return {
            status: "error",
            message: data.message || "Login failed"
        };

    } catch (error) {
        return {
            status: "error",
            message: `Network error: ${error.message || error}`
        };
    }
}



document.getElementById("loginForm").addEventListener('submit',handleSubmit);
