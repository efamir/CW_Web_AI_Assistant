const isAdminPage = document.getElementById('admin-page') !== null;


// call api endpoint to check token validness
async function tokenCheck(token) {
    const backendUrl = '/verify_token';

    try {
        const response = await fetch(backendUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token })
        });

        const data = await response.json();

        if (response.ok && data.exist === true) {
            return { status: "successful", exist: data.exist, isAdmin:data.is_admin};
        }

        return {
            status: "error",
            message: data.message || "Check failed"
        };

    } catch (error) {
        return {
            status: "error",
            message: `Network error: ${error.message || error}`
        };
    }
}

async function checkForLogin() {
	const token = localStorage.getItem('token');
    console.log(token);
	if (!token) {
		window.location.href = '/login-page';
		return;
	}
	try {
		const result = await tokenCheck(token);

		if (!result.exist) {
			window.location.href = '/login-page';
			return;
		}

        if(isAdminPage) {
            if (!result.isAdmin) {
                window.location.href = '/login-page';
                return;
            }
        }

		// токен валідний — користувач лишається на сторінці
	} catch (error) {
		console.error("Token check failed:", error);
		window.location.href = '/login-page';
	}
}
console.log("checking");
checkForLogin();

