(function(){
        const form = document.getElementById('signup-form');
        form.addEventListener('submit', async function(e){
            e.preventDefault();
            const first_name = document.getElementById('first_name').value;
            const last_name = document.getElementById('last_name').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const school = document.getElementById('school').value;

            try {
                const res = await fetch('http://127.0.0.1:8000/auth/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ first_name, last_name, email, password, school })
                });

                if (!res.ok) {
                    const err = await res.json().catch(()=>({ detail: res.statusText }));
                    alert('Sign up failed: ' + (err.detail || res.statusText));
                    return;
                }

                const data = await res.json();
                if (data && data.access_token) {
                    localStorage.setItem('access_token', data.access_token);
                }
                // Redirect to root or dashboard
                window.location.href = '/';
            } catch (err) {
                alert('Sign up error: ' + err.message);
            }
        });
    })();