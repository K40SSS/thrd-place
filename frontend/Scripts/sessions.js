// ==================== SESSIONS PAGE HANDLER ====================
(function(){
    const sessionsContainer = document.getElementById('sessions-container');
    const sessionModal = document.getElementById('sessionModal');
    const modalBody = document.getElementById('modalBody');
    const closeBtn = document.querySelector('.close-btn');

    // Check if user is logged in
    const token = localStorage.getItem('access_token') || localStorage.getItem('token');
    if (!token) {
        console.warn('[Sessions] No auth token found, redirecting to login');
        window.location.href = 'login.html';
        return;
    }

    console.log('[Sessions] Script loaded, user is authenticated');

    // Close modal when X is clicked
    closeBtn.addEventListener('click', () => {
        sessionModal.style.display = 'none';
        document.body.classList.remove('modal-open');
    });

    // Close modal when clicking outside of it
    window.addEventListener('click', (e) => {
        if (e.target === sessionModal) {
            sessionModal.style.display = 'none';
            document.body.classList.remove('modal-open');
        }
    });

    // Function to format date and time
    function formatDateTime(date, time) {
        const dateObj = new Date(date);
        const options = { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' };
        const formattedDate = dateObj.toLocaleDateString('en-US', options);
        return `${formattedDate} at ${time}`;
    }

    // Function to create a session card HTML
    function createSessionCard(session) {
        const card = document.createElement('div');
        card.className = 'sessions-card';
        card.innerHTML = `
            <h2>${session.title} - ${session.course_code}</h2>
            <p><strong>Date:</strong> ${session.date}</p>
            <p><strong>Time:</strong> ${session.time}</p>
            <p><strong>Location:</strong> ${session.location}</p>
            <p><strong>Type:</strong> ${session.meeting_type.replace(/_/g, ' ').toUpperCase()}</p>
            <p><strong>Capacity:</strong> ${session.current_capacity}/${session.max_capacity}</p>
            <button class="join-btn">View Details</button>
        `;

        // Add click event to show modal
        card.querySelector('.join-btn').addEventListener('click', () => {
            showSessionModal(session);
        });

        return card;
    }

    // Function to show session details in modal
    function showSessionModal(session) {
        modalBody.innerHTML = `
            <div class="modal-session-details">
                <h2>${session.title}</h2>
                <div class="modal-section">
                    <h3>Course Information</h3>
                    <p><strong>Course Code:</strong> ${session.course_code}</p>
                    <p><strong>Creator:</strong> ${session.creator_name}</p>
                </div>
                <div class="modal-section">
                    <h3>Description</h3>
                    <p>${session.description}</p>
                </div>
                <div class="modal-section">
                    <h3>Session Details</h3>
                    <p><strong>Date:</strong> ${formatDateTime(session.date, session.time)}</p>
                    <p><strong>Location:</strong> ${session.location}</p>
                    <p><strong>Meeting Type:</strong> ${session.meeting_type.replace(/_/g, ' ').toUpperCase()}</p>
                </div>
                <div class="modal-section">
                    <h3>Participation</h3>
                    <p><strong>Participants:</strong> ${session.current_capacity}/${session.max_capacity}</p>
                    <p><strong>Availability:</strong> ${session.is_full ? '❌ Session Full' : '✓ Spots Available'}</p>
                </div>
                <div class="modal-actions">
                    <button class="join-session-btn" data-session-id="${session.id}" 
                            ${session.is_full ? 'disabled' : ''}>
                        ${session.is_full ? 'Session Full' : 'Join Session'}
                    </button>
                    ${localStorage.getItem('user_id') === session.creator_id ? `
                    <button class="delete-session-btn" data-session-id="${session.id}">Delete Session</button>
                    ` : ''}
                </div>
            </div>
        `;

        // Add join session functionality
        const joinBtn = modalBody.querySelector('.join-session-btn');
        if (!session.is_full) {
            joinBtn.addEventListener('click', () => joinSession(session.id));
        }

        // Add delete session functionality if creator
        const deleteBtn = modalBody.querySelector('.delete-session-btn');
        if (deleteBtn) {
            deleteBtn.addEventListener('click', async () => {
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
                    sessionModal.style.display = 'none';
                    loadSessions();
                } catch (e) {
                    console.error('[Sessions] Delete failed', e);
                    alert('Delete error: ' + e.message);
                }
            });
        }

        sessionModal.style.display = 'block';
        document.body.classList.add('modal-open');
    }

    // Function to join a session
    async function joinSession(sessionId) {
        try {
            const res = await fetch(`http://127.0.0.1:8000/sessions/${sessionId}/join`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                alert('Failed to join session: ' + (err.detail || res.statusText));
                return;
            }

            alert('✓ Successfully joined the session!');
            sessionModal.style.display = 'none';
            // Reload sessions to show updated capacity
            loadSessions();
        } catch (err) {
            console.error('[Sessions] Error joining session:', err);
            alert('Error joining session: ' + err.message);
        }
    }

    // Function to load and display all sessions
    async function loadSessions() {
        try {
            console.log('[Sessions] Fetching sessions from backend');
            const res = await fetch('http://127.0.0.1:8000/sessions/', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                console.error('[Sessions] Failed to fetch sessions:', err);
                sessionsContainer.innerHTML = `<p>Error loading sessions: ${err.detail || res.statusText}</p>`;
                return;
            }

            const sessions = await res.json();
            console.log('[Sessions] Received', sessions.length, 'sessions');

            // Clear the container
            sessionsContainer.innerHTML = '';

            if (sessions.length === 0) {
                sessionsContainer.innerHTML = '<p style="grid-column: 1 / -1; text-align: center; color: #999;">No study sessions available yet. <a href="create-session.html">Create one!</a></p>';
                return;
            }

            // Add each session card
            sessions.forEach(session => {
                const card = createSessionCard(session);
                sessionsContainer.appendChild(card);
            });

            console.log('[Sessions] Sessions displayed successfully');
        } catch (err) {
            console.error('[Sessions] Exception:', err);
            sessionsContainer.innerHTML = `<p>Error loading sessions: ${err.message}</p>`;
        }
    }

    // Load sessions when page loads
    loadSessions();
})();
