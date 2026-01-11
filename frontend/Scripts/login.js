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
        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value;

        // Frontend validation
        if (!email) {
            showMessage('Please enter your email.', 'error');
            return;
        }
        if (!email.includes('@')) {
            showMessage('Please enter a valid email address.', 'error');
            return;
        }
        if (!password) {
            showMessage('Please enter your password.', 'error');
            return;
        }

        try {
            const res = await fetch('http://127.0.0.1:8000/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });

            if (!res.ok) {
                const err = await res.json().catch(()=>({ detail: res.statusText }));
                showMessage('Login failed: ' + (err.detail || res.statusText), 'error');
                return;
            }

            const data = await res.json();
            if (data && data.access_token) {
                localStorage.setItem('access_token', data.access_token);
                showMessage('✓ Login successful! Redirecting...', 'success');
            }
        } catch (err) {
            showMessage('Login error: ' + err.message, 'error');
        }
    });
});