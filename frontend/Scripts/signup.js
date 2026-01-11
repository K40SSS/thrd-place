(function(){
    const form = document.getElementById('signup-form');
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
        const first_name = document.getElementById('first_name').value.trim();
        const last_name = document.getElementById('last_name').value.trim();
        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value;
        const school = document.getElementById('school').value.trim();

        console.log('[Signup] Form submitted with:', {first_name, last_name, email, school, passwordLength: password.length});

        // Frontend validation
        if (!first_name) {
            showMessage('Please enter your first name.', 'error');
            return;
        }
        if (!last_name) {
            showMessage('Please enter your last name.', 'error');
            return;
        }
        if (!email) {
            showMessage('Please enter your email.', 'error');
            return;
        }
        if (!email.includes('@')) {
            showMessage('Please enter a valid email address.', 'error');
            return;
        }
        if (!password) {
            showMessage('Please enter a password.', 'error');
            return;
        }
        if (password.length < 8) {
            showMessage('Password must be at least 8 characters.', 'error');
            return;
        }
        if (!school) {
            showMessage('Please enter your school.', 'error');
            return;
        }

        console.log('[Signup] All validations passed, sending to backend...');

        try {
            const payload = { first_name, last_name, email, password, school };
            console.log('[Fetch] Sending POST to http://127.0.0.1:8000/auth/register with payload:', payload);
            const res = await fetch('http://127.0.0.1:8000/auth/register', {
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
                    console.log('[Fetch] Could not parse error response:', parseErr);
                }
                showMessage('Sign up failed: ' + (err.detail || err.message || res.statusText), 'error');
                return;
            }

            const data = await res.json();
            if (data && data.access_token) {
                localStorage.setItem('access_token', data.access_token);
                showMessage('✓ Account created successfully! Redirecting...', 'success');
            }
        } catch (err) {
            console.error('[Fetch] Caught exception:', err);
            showMessage('Sign up error: ' + err.message, 'error');
        }
    });
});