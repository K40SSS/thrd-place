// Enforce consistent navbar on all pages: About, Sessions, My Sessions, Create Session, then Login/Logout
(function(){
  const right = document.querySelector('header .right-side');
  if (!right) return;

  const token = localStorage.getItem('access_token') || localStorage.getItem('token');
  const inTemplates = window.location.pathname.includes('/templates/');
  const prefix = inTemplates ? '' : 'templates/';
  const homeLink = inTemplates ? '../index.html' : 'index.html';

  // Build consistent navbar
  right.innerHTML = `
    <div class="about"><a href="${prefix}about.html">About</a></div>
    <div class="sessions"><a href="${prefix}sessions.html">Sessions</a></div>
    <div class="my-sessions"><a href="${prefix}my-sessions.html">My Sessions</a></div>
    <div class="group-chats"><a href="${prefix}group-chats.html">Group Chats</a></div>
    <div class="create-session"><a href="${prefix}create-session.html">Create a Session</a></div>
    <button class="login-btn"><a href="${token ? '#' : prefix + 'login.html'}">${token ? 'LOGOUT' : 'LOGIN'}</a></button>
  `;

  // Hook up logout if authenticated
  if (token) {
    const btn = right.querySelector('.login-btn');
    if (btn) {
      btn.addEventListener('click', (e)=>{
        e.preventDefault();
        localStorage.removeItem('access_token');
        localStorage.removeItem('token');
        localStorage.removeItem('user_id');
        localStorage.removeItem('user_email');
        localStorage.removeItem('first_name');
        localStorage.removeItem('last_name');
        localStorage.removeItem('school');
        window.location.href = homeLink;
      });
    }
  }
})();
