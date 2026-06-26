const express = require('express');
const session = require('express-session');
const bcrypt = require('bcrypt');
const path = require('path');
const sqlite3 = require('sqlite3').verbose();
const axios = require('axios');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Database setup
const db = new sqlite3.Database(path.join(__dirname, 'ads.db'));

// Database helper functions
function dbGet(sql, params = []) {
  return new Promise((resolve, reject) => {
    db.get(sql, params, (err, row) => {
      if (err) reject(err);
      else resolve(row);
    });
  });
}

function dbRun(sql, params = []) {
  return new Promise((resolve, reject) => {
    db.run(sql, params, function(err) {
      if (err) reject(err);
      else resolve(this);
    });
  });
}

function dbAll(sql, params = []) {
  return new Promise((resolve, reject) => {
    db.all(sql, params, (err, rows) => {
      if (err) reject(err);
      else resolve(rows || []);
    });
  });
}

async function logActivity(userId, action, description = '', adId = null, ipAddress = '') {
  try {
    await dbRun(
      `INSERT INTO activity_logs (user_id, action, description, ad_id, ip_address)
       VALUES (?, ?, ?, ?, ?)`,
      [userId, action, description || null, adId, ipAddress]
    );
  } catch (error) {
    console.warn('Failed to log activity:', error.message);
  }
}

// Create tables
db.serialize(() => {
  db.run(`CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    is_admin INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS sessions (
    sid TEXT PRIMARY KEY,
    sess TEXT NOT NULL,
    expire INTEGER NOT NULL
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS advertisements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    discord_token TEXT NOT NULL,
    channels TEXT NOT NULL,
    delay_between_channels INTEGER DEFAULT 75,
    delay_between_cycles INTEGER DEFAULT 300,
    cycle_status TEXT DEFAULT 'stopped',
    last_posted DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS message_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ad_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    channel_id TEXT NOT NULL,
    message_id TEXT,
    status TEXT,
    response TEXT,
    posted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ad_id) REFERENCES advertisements(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
  )`);
  db.run(`CREATE TABLE IF NOT EXISTS activity_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT NOT NULL,
    description TEXT,
    ad_id INTEGER,
    ip_address TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS ad_edits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ad_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    old_title TEXT,
    new_title TEXT,
    old_description TEXT,
    new_description TEXT,
    old_price REAL,
    new_price REAL,
    edited_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ad_id) REFERENCES advertisements(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
  )`);
});

class SqliteSessionStore extends session.Store {
  get(sid, callback) {
    const done = typeof callback === 'function' ? callback : () => {};

    db.get('SELECT sess, expire FROM sessions WHERE sid = ? AND (expire IS NULL OR expire > ?)', [sid, Date.now()], (err, row) => {
      if (err) return done(err);
      if (!row) return done(null, null);
      if (row.expire && row.expire <= Date.now()) {
        return db.run('DELETE FROM sessions WHERE sid = ?', [sid], () => done(null, null));
      }

      try {
        done(null, JSON.parse(row.sess));
      } catch (parseError) {
        done(parseError);
      }
    });
  }

  set(sid, session, callback) {
    const done = typeof callback === 'function' ? callback : () => {};
    const maxAge = session.cookie && typeof session.cookie.maxAge === 'number' ? session.cookie.maxAge : null;
    const expire = maxAge ? Date.now() + maxAge : null;
    const serializedSession = JSON.stringify(session);

    db.run(
      `INSERT INTO sessions (sid, sess, expire) VALUES (?, ?, ?)
       ON CONFLICT(sid) DO UPDATE SET sess = excluded.sess, expire = excluded.expire`,
      [sid, serializedSession, expire],
      (err) => done(err)
    );
  }

  touch(sid, session, callback) {
    const done = typeof callback === 'function' ? callback : () => {};
    const maxAge = session.cookie && typeof session.cookie.maxAge === 'number' ? session.cookie.maxAge : null;
    const expire = maxAge ? Date.now() + maxAge : null;
    db.run('UPDATE sessions SET expire = ? WHERE sid = ?', [expire, sid], (err) => done(err));
  }

  destroy(sid, callback) {
    const done = typeof callback === 'function' ? callback : () => {};
    db.run('DELETE FROM sessions WHERE sid = ?', [sid], (err) => done(err));
  }

  clear(callback) {
    const done = typeof callback === 'function' ? callback : () => {};
    db.run('DELETE FROM sessions', (err) => done(err));
  }

  length(callback) {
    const done = typeof callback === 'function' ? callback : () => {};
    db.get('SELECT COUNT(*) as count FROM sessions', (err, row) => done(err, row ? row.count : 0));
  }
}

// Middleware
app.use(express.static(path.join(__dirname, 'public')));
app.use(express.urlencoded({ extended: true }));
app.use(express.json());

app.use(session({
  secret: process.env.SESSION_SECRET || 'discord-ads-secret-key',
  resave: false,
  saveUninitialized: true,
  rolling: true,
  store: new SqliteSessionStore(),
  cookie: {
    maxAge: 30 * 24 * 60 * 60 * 1000,
    httpOnly: true,
    sameSite: 'lax'
  }
}));

// Authentication middleware
const isAuthenticated = (req, res, next) => {
  if (req.session.userId) {
    next();
  } else {
    res.redirect('/login');
  }
};

const isPlatinumAdmin = async (req, res, next) => {
  if (!req.session.userId) {
    return res.redirect('/login');
  }
  
  const user = await dbGet('SELECT username, is_admin FROM users WHERE id = ?', [req.session.userId]);
  if (user && user.username === 'Platinum' && user.is_admin) {
    next();
  } else {
    res.status(403).json({ error: 'Admin access required' });
  }
};

// Job scheduler for posting ads
const postingJobs = {};

async function postAdToDiscord(ad) {
  const channels = JSON.parse(ad.channels);
  const token = ad.discord_token;
  
  for (const channelId of channels) {
    try {
      const response = await axios.post(
        `https://discord.com/api/v10/channels/${channelId}/messages`,
        { content: ad.message },
        { headers: { Authorization: token } }
      );

      // Log successful post
      await dbRun(
        `INSERT INTO message_logs (ad_id, user_id, channel_id, message_id, status, response) 
         VALUES (?, ?, ?, ?, ?, ?)`,
        [ad.id, ad.user_id, channelId, response.data.id, 'success', null]
      );

      console.log(`✓ Posted ad ${ad.id} to channel ${channelId}`);
    } catch (error) {
      // Log failed post
      await dbRun(
        `INSERT INTO message_logs (ad_id, user_id, channel_id, message_id, status, response) 
         VALUES (?, ?, ?, ?, ?, ?)`,
        [ad.id, ad.user_id, channelId, null, 'failed', error.message]
      );

      console.error(`✗ Failed to post ad ${ad.id} to channel ${channelId}:`, error.message);
    }

    // Delay between channels
    await new Promise(resolve => setTimeout(resolve, ad.delay_between_channels * 1000));
  }

  // Update last_posted timestamp
  await dbRun('UPDATE advertisements SET last_posted = CURRENT_TIMESTAMP WHERE id = ?', [ad.id]);
}

function startAdCycle(adId, delayBetweenCycles) {
  if (postingJobs[adId]) {
    clearInterval(postingJobs[adId]);
  }

  // Initial post
  (async () => {
    const ad = await dbGet('SELECT * FROM advertisements WHERE id = ?', [adId]);
    if (ad && ad.cycle_status === 'running') {
      await postAdToDiscord(ad);
    }
  })();

  // Schedule recurring posts
  postingJobs[adId] = setInterval(async () => {
    const ad = await dbGet('SELECT * FROM advertisements WHERE id = ?', [adId]);
    if (ad && ad.cycle_status === 'running') {
      await postAdToDiscord(ad);
    } else {
      clearInterval(postingJobs[adId]);
      delete postingJobs[adId];
    }
  }, delayBetweenCycles * 1000);
}

// ROUTES

// Home
app.get('/', (req, res) => {
  if (req.session.userId) {
    res.redirect('/dashboard');
  } else {
    res.redirect('/login');
  }
});

// Login page
app.get('/login', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'login.html'));
});

// Login handler
app.post('/login', async (req, res) => {
  const { username, password } = req.body;

  try {
    const user = await dbGet('SELECT * FROM users WHERE username = ?', [username]);

    if (!user) {
      return res.status(401).json({ error: 'Invalid username or password' });
    }

    const isPasswordValid = await bcrypt.compare(password, user.password);
    if (!isPasswordValid) {
      return res.status(401).json({ error: 'Invalid username or password' });
    }

    req.session.userId = user.id;
    // Make session persistent for 30 days unless user logs out
    req.session.cookie.maxAge = 30 * 24 * 60 * 60 * 1000;
    req.session.save(err => {
      if (err) console.warn('Session save error:', err);
      res.json({ success: true, redirect: '/dashboard' });
    });
  } catch (error) {
    res.status(500).json({ error: 'Server error' });
  }
});

// Signup page
app.get('/signup', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'signup.html'));
});

// Signup handler
app.post('/signup', async (req, res) => {
  const { username, password, confirmPassword } = req.body;

  if (!username || !password || !confirmPassword) {
    return res.status(400).json({ error: 'Missing fields' });
  }

  if (password !== confirmPassword) {
    return res.status(400).json({ error: 'Passwords do not match' });
  }

  try {
    const hashedPassword = await bcrypt.hash(password, 10);
    
    // Set Platinum user as admin
    const isAdmin = username === 'Platinum' ? 1 : 0;
    
    await dbRun(
      'INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)',
      [username, hashedPassword, isAdmin]
    );

    res.json({ success: true, redirect: '/login' });
  } catch (error) {
    if (error.message.includes('UNIQUE constraint failed')) {
      res.status(400).json({ error: 'Username already exists' });
    } else {
      res.status(500).json({ error: 'Server error' });
    }
  }
});

// Logout
app.get('/logout', (req, res) => {
  req.session.destroy();
  res.redirect('/login');
});

// Dashboard
app.get('/dashboard', isAuthenticated, (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'dashboard.html'));
});

// API: Get user profile
app.get('/api/user/profile', isAuthenticated, async (req, res) => {
  try {
    const user = await dbGet(
      'SELECT id, username, is_admin, created_at FROM users WHERE id = ?',
      [req.session.userId]
    );

    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    // Get user stats
    const totalAds = await dbGet(
      'SELECT COUNT(*) as count FROM advertisements WHERE user_id = ?',
      [req.session.userId]
    );

    const runningAds = await dbGet(
      'SELECT COUNT(*) as count FROM advertisements WHERE user_id = ? AND cycle_status = ?',
      [req.session.userId, 'running']
    );

    const totalMessages = await dbGet(
      'SELECT COUNT(*) as count FROM message_logs WHERE user_id = ?',
      [req.session.userId]
    );

    const successMessages = await dbGet(
      'SELECT COUNT(*) as count FROM message_logs WHERE user_id = ? AND status = ?',
      [req.session.userId, 'success']
    );

    const failedMessages = await dbGet(
      'SELECT COUNT(*) as count FROM message_logs WHERE user_id = ? AND status = ?',
      [req.session.userId, 'failed']
    );

    res.json({
      user: user,
      stats: {
        totalAds: totalAds.count || 0,
        runningAds: runningAds.count || 0,
        totalMessages: totalMessages.count || 0,
        successMessages: successMessages.count || 0,
        failedMessages: failedMessages.count || 0
      }
    });
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch profile' });
  }
});

// API: Get user's ads
app.get('/api/my-ads', isAuthenticated, async (req, res) => {
  try {
    const ads = await dbAll(
      'SELECT * FROM advertisements WHERE user_id = ? ORDER BY created_at DESC',
      [req.session.userId]
    );
    // attach recent logs to each ad
    for (const ad of ads) {
      try {
        ad.channels = ad.channels ? JSON.parse(ad.channels) : [];
      } catch (e) {
        ad.channels = [];
      }
      delete ad.discord_token;
      const logs = await dbAll('SELECT * FROM message_logs WHERE ad_id = ? ORDER BY posted_at DESC LIMIT 20', [ad.id]);
      ad.recent_logs = logs || [];
    }
    res.json(ads);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch ads' });
  }
});

// API: Create ad
app.post('/api/create-ad', isAuthenticated, async (req, res) => {
  const { title, message, discord_token, channels, delayChannels, delayCycles, description } = req.body;

  if (!title || !message || !discord_token || !channels || channels.length === 0) {
    return res.status(400).json({ error: 'Missing required fields' });
  }

  try {
    const result = await dbRun(
      `INSERT INTO advertisements (user_id, title, message, description, discord_token, channels, delay_between_channels, delay_between_cycles, cycle_status)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      [
        req.session.userId,
        title,
        message,
        description || '',
        discord_token,
        JSON.stringify(channels),
        delayChannels || 75,
        delayCycles || 300,
        'stopped'
      ]
    );

    await logActivity(req.session.userId, 'CREATE_AD', `Created ad ${title}`, result.lastID, req.ip);
    res.json({ success: true, adId: result.lastID });
  } catch (error) {
    console.error('Error creating ad:', error);
    res.status(500).json({ error: 'Failed to create ad' });
  }
});

// API: Get single ad
app.get('/api/ads/:id', isAuthenticated, async (req, res) => {
  try {
    const ad = await dbGet('SELECT * FROM advertisements WHERE id = ?', [req.params.id]);
    if (!ad) {
      return res.status(404).json({ error: 'Ad not found' });
    }

    // Check ownership or admin
    const user = await dbGet('SELECT username FROM users WHERE id = ?', [req.session.userId]);
    const isOwner = ad.user_id === req.session.userId;
    if (!isOwner && user.username !== 'Platinum') {
      return res.status(403).json({ error: 'Access denied' });
    }

    ad.channels = JSON.parse(ad.channels);
    if (!isOwner) {
      delete ad.discord_token;
    }
    res.json(ad);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch ad' });
  }
});

// API: Update ad
app.put('/api/ads/:id', isAuthenticated, async (req, res) => {
  const { title, message, discord_token, channels, delayChannels, delayCycles, description } = req.body;

  try {
    const ad = await dbGet('SELECT * FROM advertisements WHERE id = ?', [req.params.id]);
    if (!ad) {
      return res.status(404).json({ error: 'Ad not found' });
    }

    // Check if admin or owner
    const user = await dbGet('SELECT username FROM users WHERE id = ?', [req.session.userId]);
    if (ad.user_id !== req.session.userId && user.username !== 'Platinum') {
      return res.status(403).json({ error: 'Access denied' });
    }

    await dbRun(
      `UPDATE advertisements SET title = ?, message = ?, description = ?, discord_token = ?, channels = ?, delay_between_channels = ?, delay_between_cycles = ?, updated_at = CURRENT_TIMESTAMP
       WHERE id = ?`,
      [
        title || ad.title,
        message || ad.message,
        description || ad.description || '',
        discord_token || ad.discord_token,
        channels ? JSON.stringify(channels) : ad.channels,
        delayChannels || ad.delay_between_channels,
        delayCycles || ad.delay_between_cycles,
        req.params.id
      ]
    );

    await logActivity(req.session.userId, 'EDIT_AD', `Edited ad ${req.params.id}`, req.params.id, req.ip);
    res.json({ success: true });
  } catch (error) {
    console.error('Error updating ad:', error);
    res.status(500).json({ error: 'Failed to update ad' });
  }
});

// API: Delete ad
app.delete('/api/ads/:id', isAuthenticated, async (req, res) => {
  try {
    const ad = await dbGet('SELECT * FROM advertisements WHERE id = ?', [req.params.id]);
    if (!ad) {
      return res.status(404).json({ error: 'Ad not found' });
    }

    // Check if admin or owner
    const user = await dbGet('SELECT username FROM users WHERE id = ?', [req.session.userId]);
    if (ad.user_id !== req.session.userId && user.username !== 'Platinum') {
      return res.status(403).json({ error: 'Access denied' });
    }

    // Stop job if running
    if (postingJobs[ad.id]) {
      clearInterval(postingJobs[ad.id]);
      delete postingJobs[ad.id];
    }

    await dbRun('DELETE FROM advertisements WHERE id = ?', [req.params.id]);
    await dbRun('DELETE FROM message_logs WHERE ad_id = ?', [req.params.id]);

    res.json({ success: true });
  } catch (error) {
    res.status(500).json({ error: 'Failed to delete ad' });
  }
});

// API: Start ad cycle
app.post('/api/ads/:id/start', isAuthenticated, async (req, res) => {
  try {
    const ad = await dbGet('SELECT * FROM advertisements WHERE id = ?', [req.params.id]);
    if (!ad) {
      return res.status(404).json({ error: 'Ad not found' });
    }

    if (ad.user_id !== req.session.userId) {
      return res.status(403).json({ error: 'Access denied' });
    }

    await dbRun('UPDATE advertisements SET cycle_status = ? WHERE id = ?', ['running', req.params.id]);
    startAdCycle(req.params.id, ad.delay_between_cycles);
    await logActivity(req.session.userId, 'START_AD', `Started ad ${req.params.id}`, req.params.id, req.ip);

    res.json({ success: true, status: 'running' });
  } catch (error) {
    res.status(500).json({ error: 'Failed to start ad' });
  }
});

// API: Stop ad cycle
app.post('/api/ads/:id/stop', isAuthenticated, async (req, res) => {
  try {
    const ad = await dbGet('SELECT * FROM advertisements WHERE id = ?', [req.params.id]);
    if (!ad) {
      return res.status(404).json({ error: 'Ad not found' });
    }

    if (ad.user_id !== req.session.userId) {
      return res.status(403).json({ error: 'Access denied' });
    }

    await dbRun('UPDATE advertisements SET cycle_status = ? WHERE id = ?', ['stopped', req.params.id]);
    
    if (postingJobs[req.params.id]) {
      clearInterval(postingJobs[req.params.id]);
      delete postingJobs[req.params.id];
    }

    await logActivity(req.session.userId, 'STOP_AD', `Stopped ad ${req.params.id}`, req.params.id, req.ip);
    res.json({ success: true, status: 'stopped' });
  } catch (error) {
    res.status(500).json({ error: 'Failed to stop ad' });
  }
});

// API: Run an ad immediately once
app.post('/api/ads/:id/run-now', isAuthenticated, async (req, res) => {
  try {
    const ad = await dbGet('SELECT * FROM advertisements WHERE id = ?', [req.params.id]);
    if (!ad) {
      return res.status(404).json({ error: 'Ad not found' });
    }

    if (ad.user_id !== req.session.userId) {
      return res.status(403).json({ error: 'Access denied' });
    }

    await postAdToDiscord(ad);
    await dbRun('UPDATE advertisements SET last_posted = CURRENT_TIMESTAMP WHERE id = ?', [req.params.id]);
    await logActivity(req.session.userId, 'RUN_NOW', `Ran ad ${req.params.id} immediately`, req.params.id, req.ip);

    res.json({ success: true, status: 'posted' });
  } catch (error) {
    console.error('Error running ad now:', error);
    res.status(500).json({ error: 'Failed to run ad now' });
  }
});

// API: Get message logs for ad
app.get('/api/ads/:id/logs', isAuthenticated, async (req, res) => {
  try {
    const ad = await dbGet('SELECT * FROM advertisements WHERE id = ?', [req.params.id]);
    if (!ad) {
      return res.status(404).json({ error: 'Ad not found' });
    }

    if (ad.user_id !== req.session.userId) {
      return res.status(403).json({ error: 'Access denied' });
    }

    const logs = await dbAll(
      'SELECT * FROM message_logs WHERE ad_id = ? ORDER BY posted_at DESC LIMIT 100',
      [req.params.id]
    );

    res.json(logs);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch logs' });
  }
});

// ADMIN ROUTES

// Admin page
app.get('/admin', isPlatinumAdmin, (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'admin.html'));
});

// Management page (admin-only)
app.get('/management', isPlatinumAdmin, (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'management.html'));
});

// Management APIs (admin-only)
app.get('/api/management/activity-logs', isPlatinumAdmin, async (req, res) => {
  try {
    const logs = await dbAll(
      `SELECT al.*, u.username FROM activity_logs al 
       LEFT JOIN users u ON al.user_id = u.id 
       ORDER BY al.created_at DESC LIMIT 200`
    );
    res.json(logs || []);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch logs' });
  }
});

app.get('/api/management/ad-edits', isPlatinumAdmin, async (req, res) => {
  try {
    const edits = await dbAll(
      `SELECT ae.*, u.username, a.title FROM ad_edits ae
       JOIN users u ON ae.user_id = u.id
       JOIN advertisements a ON ae.ad_id = a.id
       ORDER BY ae.edited_at DESC LIMIT 200`
    );
    res.json(edits || []);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch edit history' });
  }
});

app.get('/api/management/user-logs/:userId', isPlatinumAdmin, async (req, res) => {
  try {
    const { userId } = req.params;
    const logs = await dbAll(
      `SELECT * FROM activity_logs WHERE user_id = ? ORDER BY created_at DESC LIMIT 200`,
      [userId]
    );
    res.json(logs || []);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch user logs' });
  }
});

app.get('/api/management/ad-edit-history/:adId', isPlatinumAdmin, async (req, res) => {
  try {
    const { adId } = req.params;
    const edits = await dbAll(
      `SELECT * FROM ad_edits WHERE ad_id = ? ORDER BY edited_at DESC`,
      [adId]
    );
    res.json(edits || []);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch edit history' });
  }
});

app.get('/api/management/stats', isPlatinumAdmin, async (req, res) => {
  try {
    const totalUsers = await dbGet('SELECT COUNT(*) as count FROM users');
    const totalAds = await dbGet('SELECT COUNT(*) as count FROM advertisements');
    const totalEdits = await dbGet('SELECT COUNT(*) as count FROM ad_edits');
    const userAds = await dbGet('SELECT COUNT(*) as count FROM advertisements WHERE user_id = ?', [req.session.userId]);

    res.json({
      totalUsers: totalUsers.count,
      totalAds: totalAds.count,
      totalEdits: totalEdits.count,
      userAds: userAds.count
    });
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch statistics' });
  }
});

// API: Get all ads (admin only)
app.get('/api/admin/all-ads', isPlatinumAdmin, async (req, res) => {
  try {
    const ads = await dbAll(
      `SELECT a.*, u.username FROM advertisements a 
       JOIN users u ON a.user_id = u.id 
       ORDER BY a.created_at DESC`
    );

    ads.forEach(ad => {
      ad.channels = JSON.parse(ad.channels);
      delete ad.discord_token;
    });

    res.json(ads);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch ads' });
  }
});

// API: Get single ad (admin only)
app.get('/api/admin/ads/:id', isPlatinumAdmin, async (req, res) => {
  try {
    const ad = await dbGet(
      `SELECT a.*, u.username FROM advertisements a
       JOIN users u ON a.user_id = u.id
       WHERE a.id = ?`,
      [req.params.id]
    );

    if (!ad) {
      return res.status(404).json({ error: 'Ad not found' });
    }

    ad.channels = JSON.parse(ad.channels);
    res.json(ad);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch advertisement' });
  }
});

// API: Start any ad (admin only)
app.post('/api/admin/ads/:id/start', isPlatinumAdmin, async (req, res) => {
  try {
    const ad = await dbGet('SELECT * FROM advertisements WHERE id = ?', [req.params.id]);
    if (!ad) {
      return res.status(404).json({ error: 'Ad not found' });
    }

    await dbRun('UPDATE advertisements SET cycle_status = ? WHERE id = ?', ['running', req.params.id]);
    startAdCycle(req.params.id, ad.delay_between_cycles);
    res.json({ success: true, status: 'running' });
  } catch (error) {
    res.status(500).json({ error: 'Failed to start ad' });
  }
});

// API: Stop any ad (admin only)
app.post('/api/admin/ads/:id/stop', isPlatinumAdmin, async (req, res) => {
  try {
    const ad = await dbGet('SELECT * FROM advertisements WHERE id = ?', [req.params.id]);
    if (!ad) {
      return res.status(404).json({ error: 'Ad not found' });
    }

    await dbRun('UPDATE advertisements SET cycle_status = ? WHERE id = ?', ['stopped', req.params.id]);
    if (postingJobs[req.params.id]) {
      clearInterval(postingJobs[req.params.id]);
      delete postingJobs[req.params.id];
    }
    res.json({ success: true, status: 'stopped' });
  } catch (error) {
    res.status(500).json({ error: 'Failed to stop ad' });
  }
});

// API: Run any ad once immediately (admin only)
app.post('/api/admin/ads/:id/run-now', isPlatinumAdmin, async (req, res) => {
  try {
    const ad = await dbGet('SELECT * FROM advertisements WHERE id = ?', [req.params.id]);
    if (!ad) {
      return res.status(404).json({ error: 'Ad not found' });
    }

    await postAdToDiscord(ad);
    await dbRun('UPDATE advertisements SET last_posted = CURRENT_TIMESTAMP WHERE id = ?', [req.params.id]);
    res.json({ success: true, status: 'posted' });
  } catch (error) {
    res.status(500).json({ error: 'Failed to run ad now' });
  }
});

// API: Get all users (admin only)
app.get('/api/admin/users', isPlatinumAdmin, async (req, res) => {
  try {
    const users = await dbAll('SELECT id, username, is_admin, created_at FROM users ORDER BY created_at DESC');
    res.json(users);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch users' });
  }
});

// API: Edit any ad (admin only)
app.put('/api/admin/ads/:id', isPlatinumAdmin, async (req, res) => {
  const { title, message, discord_token, channels, delayChannels, delayCycles, description } = req.body;

  try {
    const ad = await dbGet('SELECT * FROM advertisements WHERE id = ?', [req.params.id]);
    if (!ad) {
      return res.status(404).json({ error: 'Ad not found' });
    }

    await dbRun(
      `UPDATE advertisements SET title = ?, message = ?, description = ?, discord_token = ?, channels = ?, delay_between_channels = ?, delay_between_cycles = ?, updated_at = CURRENT_TIMESTAMP
       WHERE id = ?`,
      [
        title || ad.title,
        message || ad.message,
        description || ad.description || '',
        discord_token || ad.discord_token,
        channels ? JSON.stringify(channels) : ad.channels,
        delayChannels || ad.delay_between_channels,
        delayCycles || ad.delay_between_cycles,
        req.params.id
      ]
    );

    res.json({ success: true });
  } catch (error) {
    res.status(500).json({ error: 'Failed to update ad' });
  }
});

// API: Delete any ad (admin only)
app.delete('/api/admin/ads/:id', isPlatinumAdmin, async (req, res) => {
  try {
    const ad = await dbGet('SELECT * FROM advertisements WHERE id = ?', [req.params.id]);
    if (!ad) {
      return res.status(404).json({ error: 'Ad not found' });
    }

    if (postingJobs[ad.id]) {
      clearInterval(postingJobs[ad.id]);
      delete postingJobs[ad.id];
    }

    await dbRun('DELETE FROM advertisements WHERE id = ?', [req.params.id]);
    await dbRun('DELETE FROM message_logs WHERE ad_id = ?', [req.params.id]);

    res.json({ success: true });
  } catch (error) {
    res.status(500).json({ error: 'Failed to delete ad' });
  }
});

// API: Toggle user admin status (admin only)
app.put('/api/admin/users/:userId/admin', isPlatinumAdmin, async (req, res) => {
  try {
    const { makeAdmin } = req.body;
    const user = await dbGet('SELECT username, is_admin FROM users WHERE id = ?', [req.params.userId]);
    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    const newAdminStatus = typeof makeAdmin === 'boolean'
      ? (makeAdmin ? 1 : 0)
      : (user.is_admin ? 0 : 1);

    if (user.username === 'Platinum' && newAdminStatus === 0) {
      return res.status(400).json({ error: 'Cannot remove Platinum admin privileges' });
    }

    await dbRun('UPDATE users SET is_admin = ? WHERE id = ?', [newAdminStatus, req.params.userId]);

    res.json({ success: true, isAdmin: newAdminStatus });
  } catch (error) {
    res.status(500).json({ error: 'Failed to update user' });
  }
});

// Start server
app.listen(PORT, () => {
  console.log(`\n🚀 Discord Ad Server running on http://localhost:${PORT}\n`);
  console.log('📝 Features:');
  console.log('  - User token authentication');
  console.log('  - Discord channel posting');
  console.log('  - Background ad cycles (even with browser closed)');
  console.log('  - Start/Stop buttons per ad');
  console.log('  - Admin panel for Platinum user\n');
});

// On startup, resume any ads that were left running
async function ensureAdColumns() {
  try {
    const adCols = await dbAll(`PRAGMA table_info('advertisements')`);
    const adExisting = adCols.map(c => c.name);

    const toAdd = [];
    if (!adExisting.includes('message')) toAdd.push("ALTER TABLE advertisements ADD COLUMN message TEXT DEFAULT ''");
    if (!adExisting.includes('discord_token')) toAdd.push("ALTER TABLE advertisements ADD COLUMN discord_token TEXT DEFAULT ''");
    if (!adExisting.includes('channels')) toAdd.push("ALTER TABLE advertisements ADD COLUMN channels TEXT DEFAULT '[]'");
    if (!adExisting.includes('delay_between_channels')) toAdd.push("ALTER TABLE advertisements ADD COLUMN delay_between_channels INTEGER DEFAULT 75");
    if (!adExisting.includes('delay_between_cycles')) toAdd.push("ALTER TABLE advertisements ADD COLUMN delay_between_cycles INTEGER DEFAULT 300");
    if (!adExisting.includes('cycle_status')) toAdd.push("ALTER TABLE advertisements ADD COLUMN cycle_status TEXT DEFAULT 'stopped'");
    if (!adExisting.includes('last_posted')) toAdd.push("ALTER TABLE advertisements ADD COLUMN last_posted DATETIME");
    if (!adExisting.includes('description')) toAdd.push("ALTER TABLE advertisements ADD COLUMN description TEXT DEFAULT ''");
    // SQLite doesn't allow adding a column with non-constant default (e.g. CURRENT_TIMESTAMP).
    // Add the column without default, then populate it from created_at.
    if (!adExisting.includes('updated_at')) {
      try {
        await dbRun("ALTER TABLE advertisements ADD COLUMN updated_at DATETIME");
        console.log('Migration: executed -> ALTER TABLE advertisements ADD COLUMN updated_at DATETIME');
        try {
          await dbRun("UPDATE advertisements SET updated_at = created_at WHERE updated_at IS NULL");
          console.log('Migration: populated updated_at from created_at');
        } catch (e) {
          console.warn('Migration: failed populating updated_at:', e.message);
        }
      } catch (e) {
        console.warn('Migration skipped/failure: ALTER TABLE advertisements ADD COLUMN updated_at DATETIME', e.message);
      }
    }

    for (const stmt of toAdd) {
      try {
        await dbRun(stmt);
        console.log('Migration: executed ->', stmt);
      } catch (e) {
        console.warn('Migration skipped/failure:', stmt, e.message);
      }
    }

    // Check users table separately before altering it
    const userCols = await dbAll(`PRAGMA table_info('users')`);
    const userExisting = userCols.map(c => c.name);
    if (!userExisting.includes('is_admin')) {
      try {
        await dbRun("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0");
        console.log('Migration: executed -> ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0');
      } catch (e) {
        console.warn('Migration skipped/failure for users.is_admin:', e.message);
      }
    }
  } catch (err) {
    console.error('Error checking/adding advertisement columns:', err);
  }
}

// Resume ads after ensuring schema
(async () => {
  try {
    await ensureAdColumns();
    const runningAds = await dbAll('SELECT id, delay_between_cycles FROM advertisements WHERE cycle_status = ?', ['running']);
    for (const ad of runningAds) {
      startAdCycle(ad.id, ad.delay_between_cycles || 300);
      console.log(`Resumed ad cycle for ad id=${ad.id}`);
    }
  } catch (err) {
    console.error('Error resuming ad cycles on startup:', err);
  }
})();
