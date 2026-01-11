// ==================== HEADER MANAGEMENT ====================
// This script handles login/logout button visibility across all pages

(function(){
    console.log('[Header] Script loaded');
    
    // Get the login button element
    const loginBtn = document.querySelector('.login-btn');
    if (!loginBtn) {
        console.warn('[Header] Login button not found');
        return;
    }

    // Check if user is logged in
    const token = localStorage.getItem('token');
    console.log('[Header] Token check:', token ? 'Found' : 'Not found');

    if (token) {
        // User is logged in - replace login button with logout button
        loginBtn.innerHTML = '<a href="#">LOGOUT</a>';
        loginBtn.id = 'logout-btn';
        
        loginBtn.addEventListener('click', (e) => {
            e.preventDefault();
            console.log('[Header] Logout clicked');
            
            // Clear token and other user data
            localStorage.removeItem('token');
            localStorage.removeItem('user_email');
            localStorage.removeItem('user_name');
            
            console.log('[Header] User data cleared, redirecting to home');
            window.location.href = window.location.origin;
        });
        
        console.log('[Header] Logout button created for logged-in user');
    } else {
        // User is not logged in - keep login button as is
        console.log('[Header] User not logged in, keeping login button');
    }
})();
