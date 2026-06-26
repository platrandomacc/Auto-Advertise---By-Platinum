function showPopup({ title = 'Notice', message = '', type = 'info', actions = [{ label: 'OK', value: true }], autoCloseMs } = {}) {
  return new Promise(resolve => {
    const backdrop = document.createElement('div');
    backdrop.className = 'popup-backdrop';

    const card = document.createElement('div');
    card.className = 'popup-card';

    const header = document.createElement('div');
    header.className = 'popup-header';

    const titleRow = document.createElement('div');
    titleRow.style.display = 'flex';
    titleRow.style.alignItems = 'center';

    const icon = document.createElement('span');
    icon.className = `popup-icon ${type}`;
    icon.textContent = type === 'success' ? '✓' : type === 'warning' ? '!' : type === 'danger' ? '✕' : 'ℹ';

    const titleText = document.createElement('h3');
    titleText.className = 'popup-title';
    titleText.textContent = title;

    titleRow.appendChild(icon);
    titleRow.appendChild(titleText);
    header.appendChild(titleRow);

    const body = document.createElement('div');
    body.className = 'popup-body';
    body.innerHTML = message;

    const footer = document.createElement('div');
    footer.className = 'popup-footer';

    actions.forEach(action => {
      const btn = document.createElement('button');
      btn.className = `popup-btn ${action.primary ? 'popup-btn-primary' : 'popup-btn-secondary'}`;
      btn.textContent = action.label;
      btn.onclick = () => {
        if (document.body.contains(backdrop)) {
          document.body.removeChild(backdrop);
        }
        resolve(action.value);
      };
      footer.appendChild(btn);
    });

    card.appendChild(header);
    card.appendChild(body);
    card.appendChild(footer);
    backdrop.appendChild(card);
    document.body.appendChild(backdrop);

    if (autoCloseMs) {
      setTimeout(() => {
        if (document.body.contains(backdrop)) {
          document.body.removeChild(backdrop);
          resolve(actions[0]?.value ?? true);
        }
      }, autoCloseMs);
    }
  });
}

function confirmDialog(message, title = 'Confirm') {
  return showPopup({
    title,
    message,
    type: 'warning',
    actions: [
      { label: 'Cancel', value: false },
      { label: 'Confirm', value: true, primary: true }
    ]
  });
}

function showToast(message, type = 'info') {
  const container = document.getElementById('toastContainer') || document.body.appendChild(Object.assign(document.createElement('div'), { id: 'toastContainer', className: 'toast-container' }));
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  container.appendChild(toast);

  setTimeout(() => {
    toast.classList.add('toast-hide');
    setTimeout(() => toast.remove(), 400);
  }, 3200);
}

function escapeHtml(text) {
  if (text === undefined || text === null) return '';
  return text
    .toString()
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function copyToClipboard(text) {
  if (!navigator.clipboard) {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    textarea.remove();
    return;
  }
  navigator.clipboard.writeText(text);
}
