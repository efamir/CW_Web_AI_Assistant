
let allUsers = [];  // Зберігає всіх користувачів

document.addEventListener("DOMContentLoaded", async () => {
    const token = localStorage.getItem("token");

    /* if (!token) {
        window.location.href = "/login-page";
        return;
    } */

    try {
        const response = await fetch("/admin/users", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ token })
        });

        const data = await response.json();

        /* if (data.token_dont_exist || data.is_not_admin === true) {
            window.location.href = "/login-page";
            return;
        } */

        if (Array.isArray(data)) {
            allUsers = data;
            populateUserList(allUsers);
        }
    } catch (error) {
        console.error("Помилка при отриманні користувачів:", error);
        window.location.href = "/login-page";
    }

    
    document.getElementById("findUserField").addEventListener("input", () => {
        const query = document.getElementById("findUserField").value.toLowerCase();
        const filteredUsers = allUsers.filter(user =>
            user.username.toLowerCase().includes(query)
        );
        populateUserList(filteredUsers);
    });
});

function populateUserList(users) {
    const userList = document.getElementById("userList");
    userList.innerHTML = ""; 

    users.forEach(user => {
        const li = document.createElement("li");
        li.className = "nav-item";

        const a = document.createElement("a");
        a.className = "nav-link";
        a.href = "#";
        a.textContent = user.username;
        a.dataset.userid = user.token;
        a.addEventListener("click", () => {
            showUserDetails(user.token, user.username, user.role);
        });

        li.appendChild(a);
        userList.appendChild(li);
    });
}

function showUserDetails(userId, username, role) {
    const container = document.getElementById("userDetailsContent");
    const title = document.getElementById("userDetailsTitle");

    title.textContent = `User Details: ${username}`;
    container.innerHTML = `
        <div>
            <h4><span id="detailUsername">${username}</span></h4>
            <p class="mb-1"><small class="text-muted">Token: <span id="detailUserId">${userId}</span></small></p>
            <p>Role: <span id="detailRole">${role}</span></p>
            <button class="btn btn-danger btn-sm mt-3" id="deleteUserButton" onclick="deleteUser('${userId}')">
                <i class="bi bi-trash me-1"></i>Delete User
            </button>
        </div>
    `;
}


async function deleteUser(userToken) {
    const adminToken = localStorage.getItem("token");

    if (!adminToken) {
        alert("Адмін токен не знайдено");
        return;
    }

    try {
        const response = await fetch("/admin/users/delete", {
            method: "DELETE",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                admin_token: adminToken,
                user_token: userToken
            })
        });

        if (!response.ok) {
            throw new Error(`Помилка HTTP: ${response.status}`);
        }

        const result = await response.json();

        if (result.message) {
            window.location.reload();
        } else {
            alert("Не вдалося видалити користувача");
        }
    } catch (error) {
        console.error("Помилка видалення користувача:", error);
        alert("Сталася помилка при спробі видалення");
    }
}



