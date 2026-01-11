(function(){
    const form = document.getElementById('signup-form');
    const messageBox = document.getElementById('message');

    if (!form) {
        console.error('[Signup] ERROR: Form with id "signup-form" not found!');
        alert('ERROR: Signup form not found in HTML');
        return;
    }
    if (!messageBox) {
        console.error('[Signup] ERROR: Message box with id "message" not found!');
        alert('ERROR: Message box not found in HTML');
        return;
    }

    console.log('[Signup] Script loaded successfully');

    function showMessage(text, type) {
        console.log('[Signup] showMessage called with:', text, type);
        messageBox.textContent = text;
        messageBox.className = 'message-box ' + (type === 'error' ? 'error' : 'success');
        messageBox.style.display = 'block';
        console.log('[Signup] Message displayed:', messageBox.className);
        
        if (type === 'success') {
            console.log('[Signup] Success message - will redirect in 2 seconds');
            setTimeout(() => {
                console.log('[Signup] Redirecting to sessions.html');
                window.location.href = 'sessions.html';
            }, 2000);
        }
    }

    form.addEventListener('submit', async function(e){
        e.preventDefault();
        console.log('[Signup] Form submit event fired');
        messageBox.style.display = 'none';

        const first_name = document.getElementById('first_name').value.trim();
        const last_name = document.getElementById('last_name').value.trim();
        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value;
        const school = document.getElementById('school').value.trim();

        console.log('[Signup] Form values:', {first_name, last_name, email, school, passwordLength: password.length});

        // Frontend validation
        if (!first_name || !last_name || !email || !password || !school) {
            console.log('[Signup] Validation failed: missing fields');
            showMessage('All fields are required.', 'error');
            return;
        }
        if (!email.includes('@')) {
            console.log('[Signup] Validation failed: invalid email');
            showMessage('Please enter a valid email address.', 'error');
            return;
        }
        if (password.length < 8) {
            console.log('[Signup] Validation failed: password too short');
            showMessage('Password must be at least 8 characters.', 'error');
            return;
        }

        console.log('[Signup] All validations passed, sending to backend');
        showMessage('Signing up...', 'success');

        try {
            const payload = { first_name, last_name, email, password, school };
            console.log('[Signup] Sending POST to http://127.0.0.1:8000/auth/register');
            const res = await fetch('http://127.0.0.1:8000/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            console.log('[Signup] Response received, status:', res.status);

            let data;
            try {
                data = await res.json();
                console.log('[Signup] Response body:', data);
            } catch (e) {
                console.error('[Signup] Failed to parse response:', e);
                data = {};
            }

            if (!res.ok) {
                console.log('[Signup] Response not OK');
                showMessage('Sign up failed: ' + (data.detail || res.statusText), 'error');
                return;
            }

            if (data && data.access_token) {
                console.log('[Signup] Token received, saving to localStorage');
                localStorage.setItem('access_token', data.access_token);
                showMessage('✓ Account created successfully! Redirecting...', 'success');
            } else {
                console.log('[Signup] No token in response');
                showMessage('Sign up failed: No token received.', 'error');
            }
        } catch (err) {
            console.error('[Signup] Exception caught:', err);
            showMessage('Sign up error: ' + err.message, 'error');
        }
    });
})();