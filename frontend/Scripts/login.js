(function(){
        const form = document.getElementById('login-form');
        form.addEventListener('submit', async function(e){
            e.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            try {
                const res = await fetch('http://127.0.0.1:8000/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });

                if (!res.ok) {
                    const err = await res.json().catch(()=>({ detail: res.statusText }));
                    alert('Login failed: ' + (err.detail || res.statusText));
                    return;
                }

                const data = await res.json();
                if (data && data.access_token) {
                    localStorage.setItem('access_token', data.access_token);
                }
                // Redirect to root or dashboard
                window.location.href = '/';
            } catch (err) {
                alert('Login error: ' + err.message);
            }
        });
    })();