(() => {
  const tabbar = document.querySelector('.mobile-tabbar');
  if (tabbar && !tabbar.querySelector('[data-view="messages"]')) {
    const button = document.createElement('button');
    button.dataset.view = 'messages';
    button.textContent = 'Messages';
    button.addEventListener('click', () => switchView('messages'));
    tabbar.appendChild(button);
  }

  const messages = document.querySelector('#view-messages .messages');
  const chatHead = document.querySelector('#view-messages .chat-head');
  let back = document.querySelector('#mobileChatBack');
  if (chatHead && !back) {
    back = document.createElement('button');
    back.id = 'mobileChatBack';
    back.className = 'mobile-chat-back';
    back.setAttribute('aria-label', 'Back to conversations');
    back.textContent = '←';
    chatHead.prepend(back);
  }

  document.querySelectorAll('#view-messages .thread').forEach((thread) => {
    thread.addEventListener('click', () => {
      document.querySelectorAll('#view-messages .thread').forEach((t) => t.classList.remove('active'));
      thread.classList.add('active');
      if (window.innerWidth <= 700 && messages) messages.classList.add('mobile-chat-open');
    });
  });

  back?.addEventListener('click', () => messages?.classList.remove('mobile-chat-open'));
})();
