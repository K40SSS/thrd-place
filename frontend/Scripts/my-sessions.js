(function(){
  const createdList = document.getElementById('created-list');
  const joinedList = document.getElementById('joined-list');

  const token = localStorage.getItem('access_token') || localStorage.getItem('token');
  const myId = localStorage.getItem('user_id');
  if (!token) { window.location.href = 'login.html'; return; }

  function card(session, isCreator){
    const el = document.createElement('div');
    el.className = 'sessions-card';
    let html = `
      <h2>${session.title} - ${session.course_code}</h2>
      <p><strong>Date:</strong> ${session.date}</p>
      <p><strong>Time:</strong> ${session.time}</p>
      <p><strong>Location:</strong> ${session.location}</p>
      <p><strong>Type:</strong> ${String(session.meeting_type).replace(/_/g,' ').toUpperCase()}</p>
      <p><strong>Capacity:</strong> ${session.current_capacity}/${session.max_capacity}</p>
    `;
    if (isCreator) {
      html += `<button class=\"delete-session-btn\" data-session-id=\"${session.id}\">Delete Session</button>`;    } else {
      html += `<button class="leave-session-btn" data-session-id="${session.id}">Leave Session</button>`;    }
    el.innerHTML = html;
    
    if (isCreator) {
      const deleteBtn = el.querySelector('.delete-session-btn');
      deleteBtn.addEventListener('click', async (e) => {
        e.stopPropagation();
        if (!confirm('Are you sure you want to delete this session? This cannot be undone.')) return;
        try {
          const res = await fetch(`http://127.0.0.1:8000/sessions/${session.id}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
          });
          if (!res.ok) {
            const err = await res.json().catch(()=>({}));
            alert('Failed to delete: ' + (err.detail || res.statusText));
            return;
          }
          alert('Session deleted.');
          load();
        } catch (e) {
          console.error('[My Sessions] Delete failed', e);
          alert('Delete error: ' + e.message);
        }
      });
    } else {
      const leaveBtn = el.querySelector('.leave-session-btn');
      leaveBtn.addEventListener('click', async (e) => {
        e.stopPropagation();
        if (!confirm('Are you sure you want to leave this session?')) return;
        try {
          const res = await fetch(`http://127.0.0.1:8000/sessions/${session.id}/leave`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` }
          });
          if (!res.ok) {
            const err = await res.json().catch(()=>({}));
            alert('Failed to leave: ' + (err.detail || res.statusText));
            return;
          }
          alert('Left session.');
          load();
        } catch (e) {
          console.error('[My Sessions] Leave failed', e);
          alert('Leave error: ' + e.message);
        }
      });
    }
    return el;
  }

  async function load(){
    try{
      const res = await fetch('http://127.0.0.1:8000/sessions/my/sessions',{
        headers:{ 'Authorization': `Bearer ${token}` }
      });
      if(!res.ok){
        const err = await res.json().catch(()=>({}));
        createdList.innerHTML = `<p>Error: ${err.detail||res.statusText}</p>`;
        joinedList.innerHTML = '';
        return;
      }
      const all = await res.json();
      const created = [];
      const joined = [];
      all.forEach(s=>{
        if (myId && s.creator_id === myId) created.push(s); else joined.push(s);
      });
      createdList.innerHTML = '';
      joinedList.innerHTML = '';
      if (created.length===0) createdList.innerHTML = '<p>No sessions created yet.</p>';
      if (joined.length===0) joinedList.innerHTML = '<p>Not joined any sessions yet.</p>';
      created.forEach(s=> createdList.appendChild(card(s, true)) );
      joined.forEach(s=> joinedList.appendChild(card(s, false)) );
    }catch(e){
      createdList.innerHTML = `<p>Error loading: ${e.message}</p>`;
      joinedList.innerHTML = '';
    }
  }

  load();
})();
