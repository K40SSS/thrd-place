(function(){
    const form = document.getElementById('login-form');
    const messageBox = document.getElementById('message');

    function showMessage(text, type) {
        messageBox.textContent = text;
        messageBox.className = 'message-box ' + (type === 'error' ? 'error' : 'success');
        messageBox.style.display = 'block';
        if (type === 'success') {
            setTimeout(() => {
                window.location.href = 'sessions.html';
            }, 2000);
        }
    }

    form.addEventListener('submit', async function(e){
        e.preventDefault();
        messageBox.style.display = 'none';

        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value;

        if (!email || !password) {
            showMessage('Please enter both email and password.', 'error');
            return;
        }
        if (!email.includes('@')) {
            showMessage('Please enter a valid email address.', 'error');
            return;
        }

        showMessage('Logging in...', 'success');

        try {
            const payload = { email, password };
            const res = await fetch('http://127.0.0.1:8000/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            let data;
            try {
                data = await res.json();
            } catch {
                data = {};
            }

            if (!res.ok) {
                showMessage('Login failed: ' + (data.detail || res.statusText), 'error');
                return;
            }

            if (data && data.access_token) {
                localStorage.setItem('access_token', data.access_token);
                showMessage('✓ Login successful! Redirecting...', 'success');
            } else {
                showMessage('Login failed: No token received.', 'error');
            }
        } catch (err) {
            showMessage('Login error: ' + err.message, 'error');
        }
    });
});