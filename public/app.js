let currentEditAdId = null;
let activeLogAdId = null;
let logRefreshInterval = null;
let isAdminUser = false;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', async () => {
  // Check if user is admin (Platinum)
  try {
    await checkAdminStatus();
  } catch (error) {
    console.error('Error:', error);
  }

  // Load my ads
  loadMyAds();

  // Live refresh ads every 12 seconds
  setInterval(() => loadMyAds(), 12000);

  // Search filter
  document.getElementById('adSearch')?.addEventListener('input', () => {
    filterAds();
  });

  document.getElementById('statusFilter')?.addEventListener('change', () => {
    filterAds();
  });

  // Add first channel input
  addChannelInput();
  addEditChannelInput();

  // Form handlers
  document.getElementById('createAdForm').addEventListener('submit', createAd);
  document.getElementById('editAdForm').addEventListener('submit', editAd);

  // Theme toggle
  const themeToggle = document.getElementById('themeToggle');
  if (themeToggle) {
    const savedTheme = localStorage.getItem('dashboardTheme') || 'light';
    if (savedTheme === 'dark') document.body.classList.add('dark-mode');
    updateThemeToggle();
  }
});

async function checkAdminStatus() {
  try {
    const response = await fetch('/api/admin/users');
    if (response.ok) {
      isAdminUser = true;
      document.getElementById('adminLink').style.display = 'inline';
      return true;
    }
  } catch (error) {
    isAdminUser = false;
  }
  return false;
}

function switchTab(arg1, arg2) {
  let event = null;
  let tabName = null;

  if (typeof arg1 === 'string') {
    tabName = arg1;
    event = arg2 || null;
  } else {
    event = arg1;
    tabName = arg2;
  }

  // Hide all tabs
  document.querySelectorAll('.tab-content').forEach(tab => {
    tab.classList.remove('active');
  });

  // Remove active from buttons
  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.classList.remove('active');
  });

  // Show selected tab
  if (tabName) {
    document.getElementById(tabName).classList.add('active');
  }

  // Mark button as active
  if (event && event.currentTarget) {
    event.currentTarget.classList.add('active');
  } else if (tabName) {
    const tabButton = document.querySelector(`.nav-btn[data-tab="${tabName}"]`);
    if (tabButton) tabButton.classList.add('active');
  }

  // Load data if needed
  if (tabName === 'my-ads') {
    loadMyAds();
  } else if (tabName === 'manage-ads') {
    loadManageAds();
  } else if (tabName === 'account') {
    loadAccountInfo();
  }
}

async function loadMyAds() {
  try {
    const response = await fetch('/api/my-ads');
    const ads = await response.json();

    renderDashboardStats(ads);

    window.loadedAds = ads;
    filterAds(document.getElementById('adSearch')?.value || '');
  } catch (error) {
    console.error('Error loading ads:', error);
    document.getElementById('myAdsList').innerHTML = '<p class="error">Error loading ads</p>';
  }
}

function renderDashboardStats(ads) {
  const total = ads.length;
  const running = ads.filter(ad => ad.cycle_status === 'running').length;
  const paused = total - running;
  const lastPosted = ads
    .map(ad => ad.last_posted)
    .filter(Boolean)
    .sort((a, b) => new Date(b) - new Date(a))[0] || 'Never';

  document.getElementById('dashboardStats').innerHTML = `
    <div class="stat-card">
      <div class="stat-label">Total Ads</div>
      <div class="stat-value">${total}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Running</div>
      <div class="stat-value">${running}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Paused</div>
      <div class="stat-value">${paused}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Last Post</div>
      <div class="stat-value">${lastPosted}</div>
    </div>
  `;
}

function filterAds() {
  const query = document.getElementById('adSearch')?.value || '';
  const status = document.getElementById('statusFilter')?.value || '';
  const lower = query.trim().toLowerCase();
  const ads = window.loadedAds || [];

  const filtered = ads.filter(ad => {
    const matchesQuery = !lower || [ad.title, ad.description, ad.message, ad.cycle_status]
      .filter(Boolean)
      .some(value => value.toString().toLowerCase().includes(lower));
    const matchesStatus = !status || ad.cycle_status === status;
    return matchesQuery && matchesStatus;
  });

  document.getElementById('myAdsList').innerHTML = buildAdCards(filtered);
}

function buildAdCards(ads) {
  if (ads.length === 0) {
    return '<p class="no-ads">No ads yet. Create one to get started!</p>';
  }

  return ads.map(ad => {
    const isRunning = ad.cycle_status === 'running';
    const lastPosted = ad.last_posted ? new Date(ad.last_posted).toLocaleString() : 'Never';
    const channelCount = ad.channels ? JSON.parse(ad.channels).length : 0;
    const logPreview = (ad.recent_logs || []).slice(0, 3).map(log => {
      const statusLabel = log.status === 'success' ? 'Delivered' : (log.status === 'failed' ? 'Failed' : log.status);
      return `<span class="log-pill ${log.status}">${escapeHtml(statusLabel)} @ ${escapeHtml(log.channel_id)}</span>`;
    }).join(' ');

    return `
      <div class="ad-card">
        <div class="ad-header">
          <div>
            <h3>${escapeHtml(ad.title)}</h3>
            <p class="ad-tag">${escapeHtml(ad.description || 'No description provided')}</p>
          </div>
          <div class="ad-status ${isRunning ? 'running' : 'stopped'}">
            ${isRunning ? 'LIVE' : 'PAUSED'}
          </div>
        </div>
        <div class="ad-info">
          <div><strong>Channels:</strong> ${channelCount}</div>
          <div><strong>Last Posted:</strong> ${lastPosted}</div>
          <div><strong>Delay/Channel:</strong> ${ad.delay_between_channels}s</div>
          <div><strong>Delay/Cycle:</strong> ${ad.delay_between_cycles}s</div>
        </div>
        <div class="ad-message-preview">
          <strong>Message Preview</strong>
          <pre>${escapeHtml(ad.message.substring(0, 240))}</pre>
        </div>
        <div class="log-preview">
          ${logPreview || '<span class="log-pill muted">No recent activity</span>'}
        </div>
        <div class="ad-actions">
          ${isRunning 
            ? `<button class="btn btn-danger" onclick="stopAd(${ad.id})">⏹️ Stop</button>`
            : `<button class="btn btn-success" onclick="startAd(${ad.id})">▶️ Start</button>`
          }
          <button class="btn btn-secondary" onclick="editAdModal(${ad.id})">✏️ Edit</button>
          <button class="btn btn-info" onclick="viewLogs(${ad.id})">📋 Logs</button>
          <button class="btn btn-primary" onclick="runNow(${ad.id})">⚡ Run Now</button>
          <button class="btn btn-danger" onclick="deleteAd(${ad.id})">🗑️ Delete</button>
        </div>
      </div>
    `;
  }).join('');
}


async function bulkStartAll() {
  const confirmed = await confirmDialog('Start all ads now and resume their cycles?');
  if (!confirmed) return;
  const ads = window.loadedAds || [];
  await Promise.all(ads.map(ad => fetch(`/api/ads/${ad.id}/start`, { method: 'POST' })));
  showToast('All ads are being started.', 'success');
  loadMyAds();
}

async function bulkStopAll() {
  const confirmed = await confirmDialog('Stop all ad cycles now?');
  if (!confirmed) return;
  const ads = window.loadedAds || [];
  await Promise.all(ads.map(ad => fetch(`/api/ads/${ad.id}/stop`, { method: 'POST' })));
  showToast('All ads have been stopped.', 'info');
  loadMyAds();
}

async function loadManageAds() {
  await loadMyAds();
  document.getElementById('manageAdsList').innerHTML = document.getElementById('myAdsList').innerHTML;
}

async function createAd(e) {
  e.preventDefault();

  const title = document.getElementById('adTitle').value;
  const message = document.getElementById('adMessage').value;
  const description = document.getElementById('adDescription').value;
  const token = document.getElementById('discordToken').value;
  const delayChannels = parseInt(document.getElementById('delayChannels').value, 10);
  const delayCycles = parseInt(document.getElementById('delayCycles').value, 10);

  // Get channels
  const channels = [];
  document.querySelectorAll('.channel-input').forEach(input => {
    if (input.value.trim()) {
      channels.push(input.value.trim());
    }
  });

  if (channels.length === 0) {
    await showPopup({ title: 'Missing Channel', message: 'Please add at least one channel.', type: 'warning' });
    return;
  }

  try {
    showToast('Creating advertisement...', 'info');
    const response = await fetch('/api/create-ad', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title,
        message,
        description,
        discord_token: token,
        channels,
        delayChannels,
        delayCycles
      })
    });

    const data = await response.json();

    if (response.ok) {
      showToast('Advertisement created successfully!', 'success');
      document.getElementById('createAdForm').reset();
      document.getElementById('channelsList').innerHTML = '';
      addChannelInput();
      switchTab('my-ads');
      loadMyAds();
    } else {
      showToast('Error creating ad: ' + (data.error || 'Failed to create ad'), 'danger');
    }
  } catch (error) {
    console.error('Error creating ad:', error);
    await showPopup({ title: 'Create Failed', message: 'Error creating ad. Please try again.', type: 'danger' });
  }
}

async function editAdModal(adId) {
  try {
    const response = await fetch(`/api/ads/${adId}`);
    const ad = await response.json();

    currentEditAdId = ad.id;

    document.getElementById('editTitle').value = ad.title;
    document.getElementById('editMessage').value = ad.message;
    document.getElementById('editToken').value = ad.discord_token;
    document.getElementById('editDelayChannels').value = ad.delay_between_channels;
    document.getElementById('editDelayCycles').value = ad.delay_between_cycles;

    // Load channels
    document.getElementById('editChannelsList').innerHTML = '';
    ad.channels.forEach(channel => {
      const input = document.createElement('input');
      input.type = 'text';
      input.class = 'channel-input';
      input.className = 'channel-input';
      input.value = channel;
      input.placeholder = 'Channel ID (e.g., 1234567890)';
      const wrapper = document.createElement('div');
      wrapper.className = 'channel-input-wrapper';
      wrapper.appendChild(input);
      const removeBtn = document.createElement('button');
      removeBtn.type = 'button';
      removeBtn.className = 'btn btn-small btn-danger';
      removeBtn.textContent = 'Remove';
      removeBtn.onclick = (e) => { e.preventDefault(); wrapper.remove(); };
      wrapper.appendChild(removeBtn);
      document.getElementById('editChannelsList').appendChild(wrapper);
    });

    document.getElementById('editModal').style.display = 'flex';
  } catch (error) {
    console.error('Error loading ad:', error);
    await showPopup({ title: 'Load Error', message: 'Unable to load the ad for editing.', type: 'danger' });
  }
}

async function editAd(e) {
  e.preventDefault();

  if (!currentEditAdId) return;

  const title = document.getElementById('editTitle').value;
  const message = document.getElementById('editMessage').value;
  const description = document.getElementById('editDescription').value;
  const token = document.getElementById('editToken').value;
  const delayChannels = parseInt(document.getElementById('editDelayChannels').value);
  const delayCycles = parseInt(document.getElementById('editDelayCycles').value);

  const channels = [];
  document.querySelectorAll('#editChannelsList .channel-input').forEach(input => {
    if (input.value.trim()) {
      channels.push(input.value.trim());
    }
  });

  if (channels.length === 0) {
    await showPopup({ title: 'Missing Channel', message: 'Please add at least one channel before saving.', type: 'warning' });
    return;
  }

  try {
    const response = await fetch(`/api/ads/${currentEditAdId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title,
        message,
        description,
        discord_token: token || undefined,
        channels,
        delayChannels,
        delayCycles
      })
    });

    const data = await response.json();

    if (response.ok) {
      showToast('Advertisement updated successfully.', 'success');
      closeEditModal();
      loadMyAds();
    } else {
      await showPopup({ title: 'Update Failed', message: 'Error updating ad: ' + (data.error || 'Failed to update ad'), type: 'danger' });
    }
  } catch (error) {
    console.error('Error updating ad:', error);
    await showPopup({ title: 'Update Failed', message: 'Error updating ad. Please try again.', type: 'danger' });
  }
}

async function startAd(adId) {
  try {
    const response = await fetch(`/api/ads/${adId}/start`, { method: 'POST' });
    const data = await response.json();

    if (response.ok) {
      showToast('Ad started! Messages will be posted every cycle.', 'success');
      loadMyAds();
    } else {
      await showPopup({ title: 'Start Failed', message: 'Error starting ad: ' + (data.error || 'Failed to start ad'), type: 'danger' });
    }
  } catch (error) {
    console.error('Error starting ad:', error);
    await showPopup({ title: 'Start Failed', message: 'Error starting ad. Please try again.', type: 'danger' });
  }
}

async function stopAd(adId) {
  try {
    const response = await fetch(`/api/ads/${adId}/stop`, { method: 'POST' });
    const data = await response.json();

    if (response.ok) {
      showToast('Ad stopped successfully.', 'success');
      loadMyAds();
    } else {
      await showPopup({ title: 'Stop Failed', message: 'Error stopping ad: ' + (data.error || 'Failed to stop ad'), type: 'danger' });
    }
  } catch (error) {
    console.error('Error stopping ad:', error);
    await showPopup({ title: 'Stop Failed', message: 'Error stopping ad. Please try again.', type: 'danger' });
  }
}

async function deleteAd(adId) {
  const confirmed = await confirmDialog('Are you sure you want to permanently delete this ad?');
  if (!confirmed) return;

  try {
    const response = await fetch(`/api/ads/${adId}`, { method: 'DELETE' });
    const data = await response.json();

    if (response.ok) {
      showToast('Advertisement deleted successfully.', 'success');
      loadMyAds();
    } else {
      showToast('Error deleting ad: ' + (data.error || 'Failed to delete ad'), 'danger');
    }
  } catch (error) {
    console.error('Error deleting ad:', error);
    showToast('Error deleting ad', 'danger');
  }
}

async function runNow(adId) {
  try {
    const response = await fetch(`/api/ads/${adId}/run-now`, { method: 'POST' });
    const data = await response.json();

    if (response.ok) {
      showToast('Ad sent immediately. Check logs for delivery status.', 'success');
      loadMyAds();
    } else {
      showPopup({ title: 'Run Failed', message: 'Could not run the ad now: ' + (data.error || 'Unknown error'), type: 'danger' });
    }
  } catch (error) {
    console.error('Error running ad now:', error);
    showPopup({ title: 'Run Failed', message: 'Failed to run the ad immediately.', type: 'danger' });
  }
}

async function viewLogs(adId) {
  activeLogAdId = adId;
  document.getElementById('logsStatus').textContent = 'Live updates every 5 seconds';
  refreshLogs();
  document.getElementById('logsModal').style.display = 'flex';

  if (logRefreshInterval) {
    clearInterval(logRefreshInterval);
  }
  logRefreshInterval = setInterval(() => refreshLogs(), 5000);
}

async function refreshLogs() {
  if (!activeLogAdId) return;

  try {
    const response = await fetch(`/api/ads/${activeLogAdId}/logs`);
    const logs = await response.json();

    let html = '';
    if (logs.length === 0) {
      html = '<p>No message logs yet.</p>';
    } else {
      html = '<div class="cli-log-lines">';
      logs.forEach(log => {
        const time = new Date(log.posted_at).toLocaleString();
        const statusText = log.status === 'success' ? 'DELIVERED' : (log.status === 'failed' ? 'ERROR' : log.status.toUpperCase());
        const statusClass = log.status === 'success' ? 'success' : 'error';
        const messageId = log.message_id ? `message=${log.message_id}` : 'message=-';
        const responseText = log.response ? ` | ${escapeHtml(log.response)}` : '';
        html += `<pre class="cli-line"><span class="cli-time">${time}</span> | <span class="cli-status ${statusClass}">${statusText}</span> | <span class="cli-channel">#${escapeHtml(log.channel_id)}</span> | <span class="cli-id">${messageId}</span>${responseText}</pre>`;
      });
      html += '</div>';
    }

    document.getElementById('logsList').innerHTML = html;
  } catch (error) {
    console.error('Error loading logs:', error);
    document.getElementById('logsList').innerHTML = '<p class="error">Error loading logs.</p>';
  }
}

function copyLogs() {
  const logsText = document.getElementById('logsList').innerText;
  if (!logsText) return;
  copyToClipboard(logsText);
  showToast('Log text copied to clipboard.', 'success');
}

function addChannelInput() {
  const wrapper = document.createElement('div');
  wrapper.className = 'channel-input-wrapper';

  const input = document.createElement('input');
  input.type = 'text';
  input.className = 'channel-input';
  input.placeholder = 'Channel ID (e.g., 1234567890)';

  const removeBtn = document.createElement('button');
  removeBtn.type = 'button';
  removeBtn.className = 'btn btn-small btn-danger';
  removeBtn.textContent = 'Remove';
  removeBtn.onclick = (e) => { e.preventDefault(); wrapper.remove(); };

  wrapper.appendChild(input);
  wrapper.appendChild(removeBtn);

  document.getElementById('channelsList').appendChild(wrapper);
}

function addEditChannelInput() {
  const wrapper = document.createElement('div');
  wrapper.className = 'channel-input-wrapper';

  const input = document.createElement('input');
  input.type = 'text';
  input.className = 'channel-input';
  input.placeholder = 'Channel ID (e.g., 1234567890)';

  const removeBtn = document.createElement('button');
  removeBtn.type = 'button';
  removeBtn.className = 'btn btn-small btn-danger';
  removeBtn.textContent = 'Remove';
  removeBtn.onclick = (e) => { e.preventDefault(); wrapper.remove(); };

  wrapper.appendChild(input);
  wrapper.appendChild(removeBtn);

  document.getElementById('editChannelsList').appendChild(wrapper);
}

function closeEditModal() {
  document.getElementById('editModal').style.display = 'none';
  currentEditAdId = null;
}

function closeLogsModal() {
  document.getElementById('logsModal').style.display = 'none';
  activeLogAdId = null;
  if (logRefreshInterval) {
    clearInterval(logRefreshInterval);
    logRefreshInterval = null;
  }
}

// Shared UI helpers are loaded from ui.js.

function updateThemeToggle() {
  const themeToggle = document.getElementById('themeToggle');
  if (!themeToggle) return;

  const isDark = document.body.classList.contains('dark-mode');
  themeToggle.innerHTML = isDark
    ? '<span aria-hidden="true">☀️</span><span> Light</span>'
    : '<span aria-hidden="true">🌙</span><span> Dark</span>';
  themeToggle.setAttribute('aria-pressed', String(isDark));
}

function toggleTheme() {
  const isDark = document.body.classList.toggle('dark-mode');
  localStorage.setItem('dashboardTheme', isDark ? 'dark' : 'light');
  updateThemeToggle();
}

function escapeHtml(text) {
  if (!text) return '';
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// Account Tab Functions
async function loadAccountInfo() {
  try {
    const response = await fetch('/api/user/profile');
    if (!response.ok) throw new Error('Failed to load profile');
    
    const data = await response.json();
    const user = data.user;
    const stats = data.stats;

    // Update profile info
    document.getElementById('profileUsername').textContent = user.username;
    document.getElementById('profileType').textContent = user.is_admin ? 'Admin' : 'Regular User';
    document.getElementById('profileCreated').textContent = new Date(user.created_at).toLocaleDateString();

    // Update stats
    document.getElementById('statTotalAds').textContent = stats.totalAds;
    document.getElementById('statRunningAds').textContent = stats.runningAds;
    document.getElementById('statTotalMessages').textContent = stats.totalMessages;
    document.getElementById('statSuccessMessages').textContent = stats.successMessages;
    document.getElementById('statFailedMessages').textContent = stats.failedMessages;

    // Calculate success rate
    const successRate = stats.totalMessages > 0 
      ? Math.round((stats.successMessages / stats.totalMessages) * 100) 
      : 0;
    document.getElementById('statSuccessRate').textContent = successRate + '%';

  } catch (error) {
    console.error('Error loading account info:', error);
    showToast('Error loading account information', 'danger');
  }
}

function changePassword() {
  showPopup({
    title: 'Change Password',
    message: 'Password change feature coming soon! For now, please contact support.',
    type: 'info'
  });
}

function logoutAccount() {
  confirmDialog('Are you sure you want to logout?').then(confirmed => {
    if (confirmed) {
      window.location.href = '/logout';
    }
  });
}
