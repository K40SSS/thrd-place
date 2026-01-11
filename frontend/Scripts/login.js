(function(){
    const form = document.getElementById('login-form');
    const messageBox = document.getElementById('message');
    
    function showMessage(text, type) {
        console.log('[Message]', type.toUpperCase(), text);
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

        console.log('[Login] Form submitted with:', {email});

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

        console.log('[Login] All validations passed, sending to backend...');

        try {
            const payload = { email, password };
            console.log('[Fetch] Sending POST to http://127.0.0.1:8000/auth/login');
            const res = await fetch('http://127.0.0.1:8000/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            console.log('[Fetch] Response status:', res.status, res.statusText);

            if (!res.ok) {
                let err;
                try {
                    err = await res.json();
                    console.log('[Fetch] Error response body:', err);
                } catch (parseErr) {
                    err = { detail: res.statusText };
                }
                showMessage('Login failed: ' + (err.detail || err.message || res.statusText), 'error');
                return;
            }

            const data = await res.json();
            console.log('[Fetch] Success response:', data);

            if (data && data.access_token) {
                console.log('[Login] Token received, storing in localStorage');
                localStorage.setItem('access_token', data.access_token);
                showMessage('✓ Login successful! Redirecting...', 'success');
            } else {
                console.warn('[Login] Response missing access_token:', data);
                showMessage('Login succeeded but no token received', 'error');
            }
        } catch (err) {
            console.error('[Fetch] Caught exception:', err);
            showMessage('Login error: ' + err.message, 'error');
        }
    });
});