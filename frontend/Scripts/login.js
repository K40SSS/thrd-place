(function(){
    const form = document.getElementById('login-form');
    const messageBox = document.getElementById('message');

    if (!form) {
        console.error('[Login] ERROR: Form with id "login-form" not found!');
        alert('ERROR: Login form not found in HTML');
        return;
    }
    if (!messageBox) {
        console.error('[Login] ERROR: Message box with id "message" not found!');
        alert('ERROR: Message box not found in HTML');
        return;
    }

    console.log('[Login] Script loaded successfully');

    function showMessage(text, type) {
        console.log('[Login] showMessage called with:', text, type);
        messageBox.textContent = text;
        messageBox.className = 'message-box ' + (type === 'error' ? 'error' : 'success');
        messageBox.style.display = 'block';
        console.log('[Login] Message displayed:', messageBox.className);
        
        if (type === 'success') {
            console.log('[Login] Success message - will redirect in 2 seconds');
            setTimeout(() => {
                console.log('[Login] Redirecting to sessions.html');
                window.location.href = 'sessions.html';
            }, 2000);
        }
    }

    form.addEventListener('submit', async function(e){
        e.preventDefault();
        console.log('[Login] Form submit event fired');
        messageBox.style.display = 'none';

        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value;

        console.log('[Login] Form values:', {email, passwordLength: password.length});

        if (!email || !password) {
            console.log('[Login] Validation failed: missing fields');
            showMessage('Please enter both email and password.', 'error');
            return;
        }
        if (!email.includes('@')) {
            console.log('[Login] Validation failed: invalid email');
            showMessage('Please enter a valid email address.', 'error');
            return;
        }

        console.log('[Login] All validations passed, sending to backend');
        showMessage('Logging in...', 'success');

        try {
            const payload = { email, password };
            console.log('[Login] Sending POST to http://127.0.0.1:8000/auth/login');
            const res = await fetch('http://127.0.0.1:8000/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            console.log('[Login] Response received, status:', res.status);

            let data;
            try {
                data = await res.json();
                console.log('[Login] Response body:', data);
            } catch (e) {
                console.error('[Login] Failed to parse response:', e);
                data = {};
            }

            if (!res.ok) {
                console.log('[Login] Response not OK');
                showMessage('Login failed: ' + (data.detail || res.statusText), 'error');
                return;
            }

            if (data && data.access_token) {
                console.log('[Login] Token received, saving to localStorage');
                // Store token under both keys for compatibility
                localStorage.setItem('access_token', data.access_token);
                localStorage.setItem('token', data.access_token);
                // Store basic user info for client-side checks
                if (data.id) localStorage.setItem('user_id', data.id);
                if (data.email) localStorage.setItem('user_email', data.email);
                if (data.first_name) localStorage.setItem('first_name', data.first_name);
                if (data.last_name) localStorage.setItem('last_name', data.last_name);
                if (data.school) localStorage.setItem('school', data.school);
                showMessage('✓ Login successful! Redirecting...', 'success');
            } else {
                console.log('[Login] No token in response');
                showMessage('Login failed: No token received.', 'error');
            }
        } catch (err) {
            console.error('[Login] Exception caught:', err);
            showMessage('Login error: ' + err.message, 'error');
        }
    });
})();