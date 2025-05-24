function showMessage(message_text){
    const message = document.getElementById("message");
    message.innerText = message_text;
    message.classList.remove("d-none");

    setTimeout(()=>{
        message.classList.add("d-none");
        message.innerText = '';
    }, 5000);
}

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
        const result = await registerCall(username, password); 
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
        showMessage(error.message ||"Username already taken");
    }
}


async function registerCall(username, password) { 
    const backendUrl = '/register';

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

        return {
            status: "error",
            message: data.message || "Username already taken"
        };

    } catch (error) {
        return {
            status: "error",
            message: `Network error: ${error.message || error}`
        };
    }
}



document.getElementById("loginForm").addEventListener('submit',handleSubmit);
