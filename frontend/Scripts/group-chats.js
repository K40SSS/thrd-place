/**
 * Group Chats Page
 * Instagram-style chat list with side modal for messaging
 */

(async function() {
  'use strict';

  const token = localStorage.getItem('access_token') || localStorage.getItem('token');
  const userId = localStorage.getItem('user_id');

  if (!token || !userId) {
    alert('Please log in to access group chats');
    window.location.href = 'login.html';
    return;
  }

  const chatsGrid = document.getElementById('chats-grid');
  const chatModal = document.getElementById('chatModal');
  const closeChatBtn = document.getElementById('closeChatBtn');
  const chatMessages = document.getElementById('chatMessages');
  const messageInput = document.getElementById('messageInput');
  const sendMessageBtn = document.getElementById('sendMessageBtn');
  const chatTitle = document.getElementById('chatTitle');
  const chatCourseCode = document.getElementById('chatCourseCode');

  let currentSessionId = null;
  let messagePollingInterval = null;

  // Load user's sessions
  async function loadChats() {
    try {
      chatsGrid.innerHTML = '<div class="loading">Loading your group chats...</div>';

      const response = await fetch('http://127.0.0.1:8000/sessions/my/sessions', {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (!response.ok) {
        throw new Error('Failed to load sessions');
      }

      const sessions = await response.json();
      
      if (!sessions || sessions.length === 0) {
        chatsGrid.innerHTML = `
          <div class="empty-state">
            <h3>No Group Chats Yet</h3>
            <p>Join or create a study session to start chatting with your study groups!</p>
            <button class="empty-state-btn" onclick="window.location.href='sessions.html'">
              Browse Sessions
            </button>
          </div>
        `;
        return;
      }

      chatsGrid.innerHTML = '';
      
      for (const session of sessions) {
        const card = createChatCard(session);
        chatsGrid.appendChild(card);
      }
    } catch (error) {
      console.error('[Group Chats] Error loading chats:', error);
      chatsGrid.innerHTML = `
        <div class="empty-state">
          <h3>Error Loading Chats</h3>
          <p>Please try again later.</p>
        </div>
      `;
    }
  }

  // Create a chat card
  function createChatCard(session) {
    const card = document.createElement('div');
    card.className = 'chat-card';
    
    // Get initials for avatar
    const initials = session.course_code ? session.course_code.substring(0, 2).toUpperCase() : 'SS';
    
    card.innerHTML = `
      <div class="chat-card-header">
        <div class="chat-avatar">${initials}</div>
        <div class="chat-card-info">
          <div class="chat-card-title">${session.title}</div>
          <div class="chat-card-course">${session.course_code}</div>
        </div>
      </div>
      <div class="chat-card-preview">
        ${session.description.substring(0, 60)}${session.description.length > 60 ? '...' : ''}
      </div>
      <div class="chat-card-meta">
        <div class="chat-participants">
          👥 ${session.current_capacity}/${session.max_capacity}
        </div>
        <div class="chat-time">${session.date}</div>
      </div>
    `;

    card.addEventListener('click', () => openChat(session));
    
    return card;
  }

  // Open chat modal
  async function openChat(session) {
    currentSessionId = session.id;
    chatTitle.textContent = session.title;
    chatCourseCode.textContent = session.course_code;
    
    chatModal.classList.add('active');
    document.body.classList.add('modal-open');
    
    await loadMessages();
    
    // Start polling for new messages every 3 seconds
    messagePollingInterval = setInterval(loadMessages, 3000);
    
    // Focus input
    messageInput.focus();
  }

  // Close chat modal
  function closeChat() {
    chatModal.classList.remove('active');
    document.body.classList.remove('modal-open');
    currentSessionId = null;
    chatMessages.innerHTML = '';
    messageInput.value = '';
    
    if (messagePollingInterval) {
      clearInterval(messagePollingInterval);
      messagePollingInterval = null;
    }
  }

  // Load messages for current session
  async function loadMessages() {
    if (!currentSessionId) return;

    try {
      const response = await fetch(`http://127.0.0.1:8000/chat/${currentSessionId}/messages`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (!response.ok) {
        console.error('[Group Chats] Failed to load messages');
        return;
      }

      const messages = await response.json();
      
      // Store current scroll position
      const wasAtBottom = chatMessages.scrollHeight - chatMessages.scrollTop === chatMessages.clientHeight;
      
      chatMessages.innerHTML = '';
      
      if (messages.length === 0) {
        chatMessages.innerHTML = `
          <div style="text-align: center; color: #999; padding: 40px 20px;">
            No messages yet. Start the conversation!
          </div>
        `;
        return;
      }

      messages.forEach(msg => {
        const messageEl = createMessageElement(msg);
        chatMessages.appendChild(messageEl);
      });

      // Scroll to bottom if was at bottom or first load
      if (wasAtBottom || messages.length === 1) {
        chatMessages.scrollTop = chatMessages.scrollHeight;
      }
    } catch (error) {
      console.error('[Group Chats] Error loading messages:', error);
    }
  }

  // Create message element
  function createMessageElement(message) {
    const div = document.createElement('div');
    const isOwnMessage = message.user_id === userId;
    div.className = `message ${isOwnMessage ? 'own-message' : ''}`;
    
    // Get initials for avatar
    const nameParts = message.user_name.split(' ');
    const initials = nameParts.map(part => part[0]).join('').substring(0, 2).toUpperCase();
    
    // Format time
    const messageTime = new Date(message.created_at);
    const timeStr = messageTime.toLocaleTimeString('en-US', { 
      hour: 'numeric', 
      minute: '2-digit',
      hour12: true 
    });
    
    div.innerHTML = `
      <div class="message-avatar">${initials}</div>
      <div class="message-content">
        <div class="message-sender">${message.user_name}</div>
        <div class="message-bubble">
          <div class="message-text">${escapeHtml(message.message)}</div>
        </div>
        <div class="message-time">${timeStr}</div>
      </div>
    `;
    
    return div;
  }

  // Send message
  async function sendMessage() {
    if (!currentSessionId || !messageInput.value.trim()) return;

    const messageText = messageInput.value.trim();
    
    try {
      const response = await fetch(`http://127.0.0.1:8000/chat/${currentSessionId}/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          session_id: currentSessionId,
          message: messageText
        })
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        alert('Failed to send message: ' + (error.detail || response.statusText));
        return;
      }

      messageInput.value = '';
      await loadMessages();
    } catch (error) {
      console.error('[Group Chats] Error sending message:', error);
      alert('Error sending message. Please try again.');
    }
  }

  // Escape HTML to prevent XSS
  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // Event listeners
  closeChatBtn.addEventListener('click', closeChat);
  
  chatModal.addEventListener('click', (e) => {
    if (e.target === chatModal) {
      closeChat();
    }
  });

  sendMessageBtn.addEventListener('click', sendMessage);
  
  messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  // Clean up on page unload
  window.addEventListener('beforeunload', () => {
    if (messagePollingInterval) {
      clearInterval(messagePollingInterval);
    }
  });

  // Load chats on page load
  loadChats();
})();
