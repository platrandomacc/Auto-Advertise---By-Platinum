let currentAdminEditAdId = null;

document.addEventListener('DOMContentLoaded', () => {
  loadAllAds();
  addAdminEditChannelInput();

  document.getElementById('adminEditForm').addEventListener('submit', adminEditAd);
  document.getElementById('adminSearch').addEventListener('input', filterAdminAds);
  document.getElementById('adminStatusFilter').addEventListener('change', filterAdminAds);
});

function switchAdminTab(event, tabName) {
  document.querySelectorAll('.admin-tab-content').forEach(tab => {
    tab.classList.remove('active');
  });

  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.classList.remove('active');
  });

  document.getElementById(tabName).classList.add('active');
  if (event && event.currentTarget) {
    event.currentTarget.classList.add('active');
  }

  if (tabName === 'all-ads') {
    loadAllAds();
  } else if (tabName === 'all-users') {
    loadAllUsers();
  }
}

async function loadAllAds() {
  try {
    const response = await fetch('/api/admin/all-ads');
    const ads = await response.json();
    window.adminAds = ads || [];
    renderAdminAds();
  } catch (error) {
    console.error('Error loading ads:', error);
    document.getElementById('adminAdsList').innerHTML = '<p class="error">Error loading ads</p>';
  }
}

function filterAdminAds() {
  renderAdminAds();
}

function renderAdminAds() {
  const ads = window.adminAds || [];
  const searchTerm = (document.getElementById('adminSearch')?.value || '').trim().toLowerCase();
  const statusFilter = document.getElementById('adminStatusFilter')?.value || '';

  const filtered = ads.filter(ad => {
    const statusMatch = !statusFilter || ad.cycle_status === statusFilter;
    const searchMatch = !searchTerm || [String(ad.id), ad.username, ad.title, ad.cycle_status, ad.description, ad.message]
      .filter(Boolean)
      .some(value => value.toString().toLowerCase().includes(searchTerm));
    return statusMatch && searchMatch;
  });

  let html = '';
  filtered.forEach(ad => {
    const isRunning = ad.cycle_status === 'running';
    const lastPosted = ad.last_posted ? new Date(ad.last_posted).toLocaleString() : 'Never';

    html += `
      <div class="ad-card">
        <div class="ad-header">
          <h3>${escapeHtml(ad.title)}</h3>
          <div class="ad-meta">
            <span class="badge">ID: ${ad.id}</span>
            <span class="badge">User: ${escapeHtml(ad.username)}</span>
            <div class="ad-status ${isRunning ? 'running' : 'stopped'}">
              ${isRunning ? '🔴 RUNNING' : '⚪ PAUSED'}
            </div>
          </div>
        </div>
        <div class="ad-info">
          <p><strong>Channels:</strong> ${ad.channels.length}</p>
          <p><strong>Last Posted:</strong> ${lastPosted}</p>
          <p><strong>Created:</strong> ${new Date(ad.created_at).toLocaleString()}</p>
        </div>
        <div class="ad-message-preview">
          <strong>Message:</strong><br>
          <pre>${escapeHtml(ad.message.substring(0, 150))}</pre>
        </div>
        <div class="ad-actions">
          ${isRunning ? `<button class="btn btn-danger" onclick="adminStopAd(${ad.id})">⏹️ Stop</button>` : `<button class="btn btn-success" onclick="adminStartAd(${ad.id})">▶️ Start</button>`}
          <button class="btn btn-info" onclick="adminRunAd(${ad.id})">⚡ Run Now</button>
          <button class="btn btn-primary" onclick="adminEditAdModal(${ad.id})">✏️ Edit</button>
          <button class="btn btn-danger" onclick="adminDeleteAd(${ad.id})">🗑️ Delete</button>
        </div>
      </div>
    `;
  });

  document.getElementById('adminAdsList').innerHTML = html || '<p>No advertisements found.</p>';
}

async function loadAllUsers() {
  try {
    const response = await fetch('/api/admin/users');
    const users = await response.json();

    let html = '<table class="users-table"><thead><tr><th>Username</th><th>Admin</th><th>Created</th><th>Action</th></tr></thead><tbody>';

    users.forEach(user => {
      const isAdmin = user.is_admin ? '👑 Yes' : 'No';
      const adminBtn = user.is_admin 
        ? `<button class="btn btn-small btn-warning" onclick="toggleUserAdmin(${user.id}, false)">Remove Admin</button>`
        : `<button class="btn btn-small btn-success" onclick="toggleUserAdmin(${user.id}, true)">Make Admin</button>`;

      html += `<tr>
        <td><strong>${escapeHtml(user.username)}</strong></td>
        <td>${isAdmin}</td>
        <td>${new Date(user.created_at).toLocaleString()}</td>
        <td>${adminBtn}</td>
      </tr>`;
    });

    html += '</tbody></table>';
    document.getElementById('adminUsersList').innerHTML = html;
  } catch (error) {
    console.error('Error loading users:', error);
    document.getElementById('adminUsersList').innerHTML = '<p class="error">Error loading users</p>';
  }
}

async function adminEditAdModal(adId) {
  try {
    const response = await fetch(`/api/admin/ads/${adId}`);
    const ad = await response.json();

    currentAdminEditAdId = ad.id;

    document.getElementById('adminEditTitle').value = ad.title;
    document.getElementById('adminEditMessage').value = ad.message;
    document.getElementById('adminEditToken').value = ad.discord_token || '';
    document.getElementById('adminEditDelayChannels').value = ad.delay_between_channels;
    document.getElementById('adminEditDelayCycles').value = ad.delay_between_cycles;

    // Load channels
    document.getElementById('adminEditChannelsList').innerHTML = '';
    ad.channels.forEach(channel => {
      const input = document.createElement('input');
      input.type = 'text';
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
      document.getElementById('adminEditChannelsList').appendChild(wrapper);
    });

    document.getElementById('adminEditModal').style.display = 'flex';
  } catch (error) {
    console.error('Error loading ad:', error);
    await showPopup({ title: 'Load Error', message: 'Unable to load the advertisement for editing.', type: 'danger' });
  }
}

async function adminEditAd(e) {
  e.preventDefault();

  if (!currentAdminEditAdId) return;

  const title = document.getElementById('adminEditTitle').value;
  const message = document.getElementById('adminEditMessage').value;
  const token = document.getElementById('adminEditToken').value;
  const delayChannels = parseInt(document.getElementById('adminEditDelayChannels').value);
  const delayCycles = parseInt(document.getElementById('adminEditDelayCycles').value);

  const channels = [];
  document.querySelectorAll('#adminEditChannelsList .channel-input').forEach(input => {
    if (input.value.trim()) {
      channels.push(input.value.trim());
    }
  });

  if (channels.length === 0) {
    await showPopup({ title: 'Missing Channel', message: 'Please add at least one channel.', type: 'warning' });
    return;
  }

  try {
    const response = await fetch(`/api/admin/ads/${currentAdminEditAdId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title,
        message,
        discord_token: token,
        channels,
        delayChannels,
        delayCycles
      })
    });

    const data = await response.json();

    if (response.ok) {
      await showPopup({ title: 'Advertisement Updated', message: 'The advertisement was updated successfully.', type: 'success' });
      closeAdminEditModal();
      loadAllAds();
    } else {
      await showPopup({ title: 'Update Failed', message: data.error || 'Failed to update advertisement.', type: 'danger' });
    }
  } catch (error) {
    console.error('Error updating ad:', error);
    await showPopup({ title: 'Update Failed', message: 'Error updating advertisement. Please try again.', type: 'danger' });
  }
}

async function adminDeleteAd(adId) {
  const confirmed = await confirmDialog('Are you sure you want to delete this advertisement? This cannot be undone.');
  if (!confirmed) return;

  try {
    const response = await fetch(`/api/admin/ads/${adId}`, { method: 'DELETE' });
    const data = await response.json();

    if (response.ok) {
      await showPopup({ title: 'Advertisement Deleted', message: 'The advertisement was deleted successfully.', type: 'success' });
      loadAllAds();
    } else {
      await showPopup({ title: 'Delete Failed', message: data.error || 'Failed to delete advertisement.', type: 'danger' });
    }
  } catch (error) {
    console.error('Error deleting ad:', error);
    await showPopup({ title: 'Delete Failed', message: 'Error deleting advertisement. Please try again.', type: 'danger' });
  }
}

async function adminStartAd(adId) {
  try {
    const response = await fetch(`/api/admin/ads/${adId}/start`, { method: 'POST' });
    const data = await response.json();
    if (response.ok) {
      showPopup({ title: 'Started', message: 'Advertisement started successfully.', type: 'success' });
      loadAllAds();
    } else {
      showPopup({ title: 'Action Failed', message: data.error || 'Unable to start this advertisement.', type: 'danger' });
    }
  } catch (error) {
    console.error('Error starting ad:', error);
    showPopup({ title: 'Action Failed', message: 'Unable to start this advertisement.', type: 'danger' });
  }
}

async function adminStopAd(adId) {
  try {
    const response = await fetch(`/api/admin/ads/${adId}/stop`, { method: 'POST' });
    const data = await response.json();
    if (response.ok) {
      showPopup({ title: 'Stopped', message: 'Advertisement stopped successfully.', type: 'success' });
      loadAllAds();
    } else {
      showPopup({ title: 'Action Failed', message: data.error || 'Unable to stop this advertisement.', type: 'danger' });
    }
  } catch (error) {
    console.error('Error stopping ad:', error);
    showPopup({ title: 'Action Failed', message: 'Unable to stop this advertisement.', type: 'danger' });
  }
}

async function adminRunAd(adId) {
  try {
    const response = await fetch(`/api/admin/ads/${adId}/run-now`, { method: 'POST' });
    const data = await response.json();
    if (response.ok) {
      showPopup({ title: 'Sent', message: 'Advertisement was posted successfully.', type: 'success' });
      loadAllAds();
    } else {
      showPopup({ title: 'Action Failed', message: data.error || 'Unable to run this advertisement.', type: 'danger' });
    }
  } catch (error) {
    console.error('Error running ad:', error);
    showPopup({ title: 'Action Failed', message: 'Unable to run this advertisement.', type: 'danger' });
  }
}

async function toggleUserAdmin(userId, makeAdmin) {
  try {
    const response = await fetch(`/api/admin/users/${userId}/admin`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ makeAdmin })
    });
    const data = await response.json();

    if (response.ok) {
      await showPopup({ title: 'User Updated', message: 'The user admin status was updated successfully.', type: 'success' });
      loadAllUsers();
    } else {
      await showPopup({ title: 'Update Failed', message: data.error || 'Failed to update user.', type: 'danger' });
    }
  } catch (error) {
    console.error('Error updating user:', error);
    await showPopup({ title: 'Update Failed', message: 'Error updating user. Please try again.', type: 'danger' });
  }
}

function addAdminEditChannelInput() {
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

  document.getElementById('adminEditChannelsList').appendChild(wrapper);
}

function closeAdminEditModal() {
  document.getElementById('adminEditModal').style.display = 'none';
  currentAdminEditAdId = null;
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}
