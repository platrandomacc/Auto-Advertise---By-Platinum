"""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║                 AUTO ADVERTISEMENTS WEBSITE - PROJECT MIGRATED            ║
║                                                                            ║
║  Originally designed with Python/Flask, this project has been migrated   ║
║  to Node.js/Express for better performance and easier deployment.        ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝

🚀 QUICK START:

1. Install dependencies:
   npm install

2. Start the server:
   npm start

3. Open your browser to:
   http://localhost:3000

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 PROJECT STRUCTURE:

✓ server.js              - Main Express server (replaces Flask app)
✓ public/login.html      - User login page
✓ public/signup.html     - User registration page
✓ public/dashboard.html  - Main application interface
✓ public/styles.css      - All CSS styling
✓ public/app.js         - Frontend JavaScript logic
✓ package.json          - Node.js dependencies
✓ ads.db               - SQLite database (auto-created)

📚 DOCUMENTATION:

- README.md             - Full documentation
- QUICKSTART.md         - Quick start guide
- QUICKSTART.md         - Setup and usage

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ FEATURES:

✅ Simple Username/Password Login (No API Keys)
✅ User Registration & Account Management
✅ Post Advertisements with Image Upload
✅ Browse & Search All Advertisements
✅ Manage Your Own Advertisements
✅ Category Filtering
✅ Logout System
✅ Mobile Responsive Design
✅ SQLite Database
✅ Secure Password Hashing

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔧 TECHNOLOGY STACK:

- Backend:   Node.js + Express.js
- Frontend:  HTML5, CSS3, JavaScript
- Database:  SQLite3
- Security:  bcrypt (password hashing)
- Sessions:  Express-session

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 LEARN MORE:

See README.md and QUICKSTART.md for detailed documentation.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
                    color=discord.Color.red(),
                    description="> ❌ An error occurred while opening the modal. Please try again."
                ),
                ephemeral=True
            )
        except:
            pass  # If followup also fails, just ignore

def read_lines(file_path):
    if not file_path.exists():
        return []
    return [l.strip() for l in file_path.read_text("utf-8").split("\n")
            if l.strip() and not l.strip().startswith("#")]


def is_valid_token_string(token):
    token = token.strip()
    if not token:
        return False
    parts = token.split('.')
    return len(parts) == 3 and all(parts)


def parse_email_token_line(line):
    parts = [p.strip() for p in line.strip().split(":") if p.strip()]
    if not parts:
        return None
    if len(parts) == 1:
        return {"email": None, "password": None, "token": parts[0], "valid": is_valid_token_string(parts[0])}
    if len(parts) == 2:
        return {"email": parts[0], "password": None, "token": parts[1], "valid": is_valid_token_string(parts[1])}
    return {
        "email": parts[0],
        "password": ":".join(parts[1:-1]),
        "token": parts[-1],
        "valid": is_valid_token_string(parts[-1])
    }


def extract_email_tokens(amount, include_email_pass=False):
    entries = []
    for line in read_lines(EMAILTOKENS_FILE):
        parsed = parse_email_token_line(line)
        if not parsed or not parsed["valid"]:
            continue
        if include_email_pass and (not parsed["email"] or not parsed["password"]):
            continue
        if include_email_pass:
            entries.append(f"{parsed['email']}:{parsed['password']}:{parsed['token']}")
        else:
            entries.append(parsed["token"])
        if len(entries) >= amount:
            break
    return entries


def get_join_progress_view_url(session_id):
    raw_host = os.environ.get("JOIN_PROGRESS_HOST", "127.0.0.1").strip()
    if raw_host.startswith("http://") or raw_host.startswith("https://"):
        parsed = urlparse(raw_host)
        scheme = parsed.scheme or "http"
        host = parsed.netloc or parsed.path
        return f"{scheme}://{host}:{ACTIVE_WEBHOOK_PORT}/join-progress/{session_id}"
    return f"http://{raw_host}:{ACTIVE_WEBHOOK_PORT}/join-progress/{session_id}"

def get_join_progress_url(session_id):
    raw_host = os.environ.get("JOIN_PROGRESS_HOST", "127.0.0.1").strip()
    if raw_host.startswith("http://") or raw_host.startswith("https://"):
        parsed = urlparse(raw_host)
        scheme = parsed.scheme or "http"
        host = parsed.netloc or parsed.path
        return f"{scheme}://{host}:{ACTIVE_WEBHOOK_PORT}/join-progress/{session_id}/download"
    return f"http://{raw_host}:{ACTIVE_WEBHOOK_PORT}/join-progress/{session_id}/download"

def append_line(file_path, line):
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(line.strip() + "\n")

def remove_line(file_path, value):
    lines = [l for l in read_lines(file_path) if l != value.strip()]
    file_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")

def line_exists(file_path, value):
    return value.strip() in read_lines(file_path)

def is_adv_license_expired(lic):
    """Check if an Auto Adv license has expired."""
    if not lic or not lic.get("expiresAt"): return False
    exp = datetime.fromisoformat(lic["expiresAt"])
    if exp.tzinfo is None: exp = exp.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) > exp

def load_json(file_path):
    if not file_path.exists():
        return {}
    try:
        return json.loads(file_path.read_text("utf-8"))
    except Exception:
        return {}

def save_json(file_path, data):
    file_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

def make_json_safe(value):
    if isinstance(value, dict):
        result = {}
        for k, v in value.items():
            safe_v = make_json_safe(v)
            if safe_v is not None:
                result[k] = safe_v
        return result
    if isinstance(value, list):
        return [make_json_safe(v) for v in value if make_json_safe(v) is not None]
    if isinstance(value, tuple):
        return [make_json_safe(v) for v in value if make_json_safe(v) is not None]
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return None

def load_running_state():
    return load_json(RUNNING_STATE_FILE)

def persist_running_state():
    state = {
        "sessions": {},
        "adv_sessions": {}
    }

    for key, session in sessions.items():
        if not session.get("running"):
            continue
        saved = make_json_safe(session)
        if isinstance(saved, dict):
            saved.pop("tokenStates", None)
        state["sessions"][key] = saved

    for key, adv_state in adv_sessions.items():
        if not adv_state.get("running"):
            continue
        state["adv_sessions"][key] = make_json_safe(adv_state)

    save_json(RUNNING_STATE_FILE, state)

async def restore_running_state():
    data = load_running_state()
    if not data:
        return

    for key, session in data.get("sessions", {}).items():
        if not session.get("running"):
            continue
        if isinstance(session.get("startTime"), str):
            try:
                dt = datetime.fromisoformat(session["startTime"])
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                session["startTime"] = dt
            except Exception:
                session["startTime"] = datetime.now(timezone.utc)
        session.pop("tokenStates", None)
        sessions[key] = session

        uid, stype = key.split(":", 1)
        tokens = session.get("tokens", [])
        if tokens:
            await start_presence_for_tokens(tokens)

        if stype == "vouch":
            asyncio.create_task(vouch_loop(uid))
        elif stype in ("chat", "trade"):
            asyncio.create_task(text_loop(uid, stype))
        elif stype == "vc":
            asyncio.create_task(vc_loop(uid))
        elif stype == "reacts":
            asyncio.create_task(react_loop(uid))

    for key, adv_state in data.get("adv_sessions", {}).items():
        if not adv_state.get("running"):
            continue
        adv_sessions[key] = adv_state
        uid, acc_id = key.split(":", 1)
        token = adv_state.get("token")
        if token:
            await ensure_presence_gateway(token)
        asyncio.create_task(adv_message_loop(uid, acc_id))
        if adv_state.get("dmResponse"):
            asyncio.create_task(adv_dm_loop(uid, acc_id))

async def load_saved_state_and_resume():
    try:
        await restore_running_state()
        print("[Startup] Restored running bot state from disk.")
    except Exception as e:
        print(f"[Startup] Failed to restore running state: {e}")

async def safe_send_modal(interaction, modal):
    try:
        return await interaction.response.send_modal(modal)
    except discord.NotFound:
        try:
            return await interaction.followup.send(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Could not open modal. Please try again."), ephemeral=True)
        except Exception as e:
            print(f"[safe_send_modal] fallback failed: {e}")
    except Exception as e:
        print(f"[safe_send_modal] error: {e}")
    return None

async def safe_send_message(interaction, **kwargs):
    try:
        return await interaction.response.send_message(**kwargs)
    except discord.NotFound:
        try:
            return await interaction.followup.send(**kwargs)
        except Exception as e:
            print(f"[safe_send_message] fallback failed: {e}")
    except Exception as e:
        print(f"[safe_send_message] error: {e}")
    return None

async def safe_edit_message(interaction, **kwargs):
    try:
        if hasattr(interaction, 'edit_original_response'):
            try:
                return await interaction.edit_original_response(**kwargs)
            except Exception as e:
                print(f"[safe_edit_message] edit_original_response failed: {e}")
                return await interaction.followup.send(**kwargs)
        if hasattr(interaction, 'response') and hasattr(interaction.response, 'edit_message'):
            try:
                return await interaction.response.edit_message(**kwargs)
            except Exception as e:
                print(f"[safe_edit_message] response.edit_message failed: {e}")
                return await interaction.followup.send(**kwargs)
        return await interaction.followup.send(**kwargs)
    except discord.NotFound:
        try:
            return await interaction.followup.send(**kwargs)
        except Exception as e:
            print(f"[safe_edit_message] fallback failed: {e}")
    except Exception as e:
        print(f"[safe_edit_message] error: {e}")
    return None

is_owner       = lambda uid: line_exists(OWNER_FILE, uid)
is_admin       = lambda uid: line_exists(ADMINS_FILE, uid)
is_user        = lambda uid: line_exists(USERS_FILE, uid)
is_reseller    = lambda uid: line_exists(RESELLERS_FILE, uid)
is_restricted  = lambda uid: line_exists(RESTRICTED_FILE, uid)
can_manage_bot = lambda uid: is_owner(uid) or is_admin(uid)
can_gen_key    = lambda uid: is_owner(uid) or is_admin(uid) or is_user(uid) or is_reseller(uid)

def get_balance(user_id):
    return load_json(BALANCES_FILE).get(user_id, 0)

def set_balance(user_id, val):
    b = load_json(BALANCES_FILE); b[user_id] = val; save_json(BALANCES_FILE, b)

def deduct_balance(user_id):
    b = load_json(BALANCES_FILE)

    if b.get(user_id) == "infinite":
        return True

    if not b.get(user_id) or float(b[user_id]) < 3:
        return False

    b[user_id] = float(b[user_id]) - 3
    save_json(BALANCES_FILE, b)
    return True

def format_balance(val):
    return "Infinite" if val == "infinite" else f"${val}"

def get_active_redemption(user_id, stype):
    # Returns either None or a dict with redemption metadata, e.g.
    # {"key": "ABCD-1234", "tokenCount": 10, "tokens": [...], "duration_seconds": 3600, "expiresAt": "..."}
    return load_json(REDEMPTIONS_FILE).get(user_id, {}).get(stype)

def set_active_redemption(user_id, stype, data):
    """Store an active redemption for a user and session type.

    `data` may be a string (legacy key code) or a dict with metadata.
    """
    r = load_json(REDEMPTIONS_FILE)
    if user_id not in r: r[user_id] = {}
    if isinstance(data, str):
        # legacy: store as object with key only
        r[user_id][stype] = {"key": data}
    else:
        r[user_id][stype] = data
    save_json(REDEMPTIONS_FILE, r)


def get_meta_value(meta, *keys):
    if not isinstance(meta, dict):
        return None
    for key in keys:
        value = meta.get(key)
        if value is not None:
            return value
    return None


def clear_active_redemption(user_id, stype):
    r = load_json(REDEMPTIONS_FILE)
    if user_id in r:
        r[user_id].pop(stype, None)
        if not r[user_id]: del r[user_id]
    save_json(REDEMPTIONS_FILE, r)

def load_keys(): return load_json(KEYS_FILE)
def save_keys(k): save_json(KEYS_FILE, k)

def normalize_key_code(key):
    if not isinstance(key, str):
        return None
    return re.sub(r"[\s\u200B\u200C\u200D\uFEFF]+", "", key).strip()


def find_key_entry(keys, key):
    normalized = normalize_key_code(key)
    if not normalized:
        return None, None
    if normalized in keys:
        return normalized, keys[normalized]
    for stored_key, stored_value in keys.items():
        if stored_key.upper() == normalized.upper():
            return stored_key, stored_value
    return None, None

def generate_key(): return str(uuid.uuid4()).replace("-", "").upper()[:20]

def persist_generated_key(key, status="active"):
    keys = load_json(KEYS_FILE)
    keys[key] = {
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "status": status,
    }
    save_json(KEYS_FILE, keys)
    return key

def parse_expiry(s):
    if not s or s.lower() == "never": return None
    m = re.match(r'^(\d+)(d|w|m|h)$', s.strip(), re.IGNORECASE)
    if not m: return None
    unit_ms = {"h": 3600000, "d": 86400000, "w": 604800000, "m": 2592000000}
    ms = int(m.group(1)) * unit_ms[m.group(2).lower()]
    return (datetime.now(timezone.utc) + timedelta(milliseconds=ms)).isoformat()

def is_key_expired(k):
    if not k.get("expiresAt"): return False
    exp = datetime.fromisoformat(k["expiresAt"])
    if exp.tzinfo is None: exp = exp.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) > exp

def format_expiry(iso):
    if not iso: return "Never"
    exp = datetime.fromisoformat(iso)
    if exp.tzinfo is None: exp = exp.replace(tzinfo=timezone.utc)
    return f"<t:{int(exp.timestamp())}:R>"

def is_adv_license_expired(lic):
    """Check if an Auto Adv license has expired."""
    if not lic or not lic.get("expiresAt"): return False
    exp = datetime.fromisoformat(lic["expiresAt"])
    if exp.tzinfo is None: exp = exp.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) > exp

def has_claimed_trial(user_id):
    """Check if user has already claimed the free trial"""
    claims = load_json(TRIAL_CLAIMS_FILE)
    return user_id in claims

def record_trial_claim(user_id):
    """Record that a user has claimed the free trial"""
    claims = load_json(TRIAL_CLAIMS_FILE)
    claims[user_id] = datetime.now(timezone.utc).isoformat()
    save_json(TRIAL_CLAIMS_FILE, claims)

# ─── Referral Tier System ─────────────────────────────────────────────────────

REFERRAL_TIERS = {
    0:  {"name": "Rookie",     "refs_required": 0,  "bonus_slots": 0, "perks": []},
    1:  {"name": "Bronze",     "refs_required": 5,  "bonus_slots": 1, "perks": ["+1 Auto Adv slot"]},
    2:  {"name": "Silver",     "refs_required": 10, "bonus_slots": 2, "perks": ["+2 Auto Adv slots (3 total)", "Priority queue access"]},
    3:  {"name": "Gold",       "refs_required": 20, "bonus_slots": 3, "perks": ["+3 Auto Adv slots (5 total)", "Exclusive Discord role", "Early feature access"]},
    4:  {"name": "Platinum",   "refs_required": 50, "bonus_slots": 5, "perks": ["+5 Auto Adv slots (max)", "VIP status", "Custom bot commands", "Direct support"]},
}

REFERRAL_CODE_LENGTH = 8
REFERRAL_LEADERBOARD_MESSAGES = []

def load_referrals():
    """Load referral data"""
    return load_json(REFERRALS_FILE)

def save_referrals(data):
    """Save referral data"""
    save_json(REFERRALS_FILE, data)

def generate_referral_code():
    refs = load_referrals()
    used_codes = {data.get("referralId") for data in refs.values() if data.get("referralId")}
    for _ in range(1000):
        code = "".join(random.choices("0123456789", k=REFERRAL_CODE_LENGTH))
        if code not in used_codes:
            return code
    return str(random.randint(10 ** (REFERRAL_CODE_LENGTH - 1), 10 ** REFERRAL_CODE_LENGTH - 1))

def get_referral_data(user_id):
    """Get or create referral data for user"""
    refs = load_referrals()
    if user_id not in refs:
        refs[user_id] = {
            "referrer": None,
            "referrals": [],
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "referralId": generate_referral_code(),
        }
        save_referrals(refs)
    else:
        if not refs[user_id].get("referralId"):
            refs[user_id]["referralId"] = generate_referral_code()
            save_referrals(refs)
    return refs[user_id]

def find_referrer_by_code(code):
    """Look up the referrer user ID by referral code"""
    refs = load_referrals()
    for user_id, data in refs.items():
        if data.get("referralId") == code:
            return user_id
    return None

def record_referral(referrer_id, new_user_id):
    """Record a new referral"""
    refs = load_referrals()
    referrer_data = refs.get(referrer_id, {
        "referrer": None,
        "referrals": [],
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "referralId": generate_referral_code(),
    })
    if new_user_id not in referrer_data["referrals"]:
        referrer_data["referrals"].append(new_user_id)
    refs[referrer_id] = referrer_data

    new_user_data = refs.get(new_user_id, {
        "referrer": None,
        "referrals": [],
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "referralId": generate_referral_code(),
    })
    if not new_user_data.get("referralId"):
        new_user_data["referralId"] = generate_referral_code()
    new_user_data["referrer"] = referrer_id
    refs[new_user_id] = new_user_data
    save_referrals(refs)

def refresh_referral_leaderboards():
    """Refresh any open referral leaderboard messages."""
    async def _refresh():
        updated_embed = build_referral_leaderboard_embed()
        alive_messages = []
        for entry in list(REFERRAL_LEADERBOARD_MESSAGES):
            try:
                channel = bot.get_channel(entry["channel_id"])
                if not channel:
                    channel = await bot.fetch_channel(entry["channel_id"])
                message = await channel.fetch_message(entry["message_id"])
                await message.edit(embed=updated_embed, view=RefLeaderboardView(entry["admin_uid"]))
                alive_messages.append(entry)
            except Exception:
                continue
        REFERRAL_LEADERBOARD_MESSAGES.clear()
        REFERRAL_LEADERBOARD_MESSAGES.extend(alive_messages)
    asyncio.create_task(_refresh())

def get_referral_tier(user_id):
    """Get user's referral tier (0-4)"""
    refs = load_referrals()
    ref_count = len(refs.get(user_id, {}).get("referrals", []))
    for tier in range(4, -1, -1):
        if ref_count >= REFERRAL_TIERS[tier]["refs_required"]:
            return tier
    return 0

def get_total_adv_slots(user_id):
    """Get total Auto Adv slots (base + referral bonus)"""
    tier = get_referral_tier(user_id)
    base_slots = 1
    bonus_slots = REFERRAL_TIERS[tier]["bonus_slots"]
    return base_slots + bonus_slots

get_tokens   = lambda: [t for t in read_lines(TOKENS_FILE) if is_valid_token_string(t)]
get_reasons  = lambda: read_lines(REASONS_FILE)
get_messages = lambda: read_lines(MESSAGES_FILE)
get_trading  = lambda: read_lines(TRADING_FILE)

CHAT_REPLY_PREFIXES = [
    "Honestly,",
    "For real,",
    "Same here,",
    "Not gonna lie,",
    "That makes sense,",
    "I feel that,",
    "Big facts,",
    "True,",
]

CHAT_QUESTION_REPLIES = [
    "Hmm, not sure, but I'd guess later tonight.",
    "Maybe someone else knows, but that seems likely.",
    "I feel like it depends on the group.",
    "I'm not certain, but that could work.",
    "Probably, if the server stays active.",
]

CHAT_DECORATORS = [
    "No cap,",
    "Real talk,",
    "Lowkey,",
    "Honestly,",
    "Not gonna lie,",
]


def make_chat_message(session, pool):
    if not pool:
        return "hey"

    order = session.get("messageOrder")
    if not order or len(order) != len(pool):
        order = random.sample(range(len(pool)), len(pool))
        session["messageOrder"] = order
        session["messageIndex"] = 0

    index = session.get("messageIndex", 0)
    pool_index = order[index]
    base = pool[pool_index]
    session["messageIndex"] = (index + 1) % len(pool)
    if session["messageIndex"] == 0:
        session["messageOrder"] = random.sample(range(len(pool)), len(pool))

    msg = base
    last_message = session.get("lastMessage", "").strip()
    if last_message and random.random() < 0.35:
        if last_message.endswith("?"):
            msg = random.choice(CHAT_QUESTION_REPLIES)
        else:
            msg = f"{random.choice(CHAT_REPLY_PREFIXES)} {base[0].lower() + base[1:]}" if base else random.choice(CHAT_REPLY_PREFIXES)
    elif random.random() < 0.20:
        msg = f"{random.choice(CHAT_DECORATORS)} {msg[0].lower() + msg[1:]}" if msg else msg

    session["lastMessage"] = msg
    return msg

SESSION_TYPES = ("vouch", "chat", "trade", "vc", "trial", "reacts")
TYPE_ICONS    = {"vouch": "🏆", "chat": "💬", "trade": "🔄", "vc": "🎙️", "trial": "⏰", "reacts": "🎯", "mem-online": "🟢", "mem-offline": "⚫", "boost": "🚀"}
TYPE_LABELS   = {"vouch": "Auto Vouch", "chat": "Auto Chat", "trade": "Auto Trade", "vc": "Auto VC", "trial": "Trial ⏰", "reacts": "Auto Reacts", "mem-online": "Online Members", "mem-offline": "Offline Members", "boost": "Boost"}

def skey(uid, stype): return f"{uid}:{stype}"

def stop_session(uid, stype):
    k = skey(uid, stype)
    s = sessions.get(k)
    if s:
        s["running"] = False
        tokens = s.get("tokens", [])
        if tokens:
            try:
                asyncio.create_task(close_presence_for_tokens(tokens))
            except Exception:
                pass
        sessions.pop(k, None)
        persist_running_state()

def stop_all_sessions(uid):
    for t in SESSION_TYPES: stop_session(uid, t)

def load_adv_licenses(): return load_json(ADV_LICENSES_FILE)
def save_adv_licenses(d): save_json(ADV_LICENSES_FILE, d)

def get_adv_license(uid):
    return load_adv_licenses().get(uid)

def parse_delay_string(s):
    if not s: return 60
    m = re.match(r'^(\d+)([smhd])$', str(s).strip(), re.IGNORECASE)
    if not m: return 60
    v, u = int(m.group(1)), m.group(2).lower()
    return max(5, v * {"s": 1, "m": 60, "h": 3600, "d": 86400}[u])

# ─── Extract invite code from link or bare code ──────────────────────────────

def extract_invite_code(invite_input):
    invite_input = invite_input.strip()
    patterns = [
        r'discord\.gg/([A-Za-z0-9-]+)',
        r'discord\.com/invite/([A-Za-z0-9-]+)',
        r'discordapp\.com/invite/([A-Za-z0-9-]+)',
    ]
    for pat in patterns:
        m = re.search(pat, invite_input, re.IGNORECASE)
        if m:
            return m.group(1)
    if re.match(r'^[A-Za-z0-9-]+$', invite_input):
        return invite_input
    return None

# ─── OAuth2 guild join ────────────────────────────────────────────────────────

# Discord desktop client — matches what reference implementations use
_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) discord/1.0.9011 Chrome/91.0.4472.164 Electron/13.6.6 Safari/537.36"
)

# Discord desktop client super-properties (not Chrome browser)
_X_SUPER_PROPERTIES = (
    "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUi"
    "LCJjbGllbnRfdmVyc2lvbiI6IjEuMC45MDExIiwib3NfdmVyc2lvbiI6IjEwLjAuMTkwNDUiLCJvc19hcmNoIjoieDY0"
    "Iiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiY2xpZW50X2J1aWxkX251bWJlciI6MTc5ODgyLCJuYXRpdmVfYnVpbGRf"
    "bnVtYmVyIjozMDMwNiwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbCwiZGVzaWduX2lkIjowfQ=="
)

def _token_headers(token):
    return {
        "accept":             "*/*",
        "accept-encoding":    "gzip, deflate",
        "accept-language":    "en-US",
        "authorization":      token,
        "content-type":       "application/json",
        "origin":             "https://discord.com",
        "referer":            "https://discord.com/channels/@me",
        "sec-fetch-dest":     "empty",
        "sec-fetch-mode":     "cors",
        "sec-fetch-site":     "same-origin",
        "user-agent":         _USER_AGENT,
        "x-debug-options":    "bugReporterEnabled",
        "x-discord-locale":   "en-US",
        "x-super-properties": _X_SUPER_PROPERTIES,
    }

async def resolve_invite_to_guild(invite_code):
    url = f"https://discord.com/api/v9/invites/{invite_code}?with_counts=true"
    try:
        async with aiohttp.ClientSession() as http:
            async with http.get(url, headers={"User-Agent": _USER_AGENT}) as res:
                if not res.ok:
                    return None
                data = await res.json()
                return data.get("guild", {}).get("id")
    except Exception:
        return None

async def resolve_channel_invite(invite_code):
    """Resolve a channel invite to get guild_id and channel_id."""
    url = f"https://discord.com/api/v9/invites/{invite_code}?with_counts=true"
    try:
        async with aiohttp.ClientSession() as http:
            async with http.get(url, headers={"User-Agent": _USER_AGENT}) as res:
                if not res.ok:
                    return None
                data = await res.json()
                guild_id = data.get("guild", {}).get("id")
                channel_id = data.get("channel", {}).get("id")
                channel_type = data.get("channel", {}).get("type")
                return {"guild_id": guild_id, "channel_id": channel_id, "channel_type": channel_type}
    except Exception:
        return None

def parse_channel_id(channel_input):
    """
    Parse a channel ID from various formats:
    - Direct ID: "123456789"
    - Channel link: "https://discord.com/channels/guild_id/channel_id"
    Returns: channel_id (str) or None if invalid
    """
    channel_input = channel_input.strip()
    
    # Try direct ID first
    if channel_input.isdigit():
        return channel_input
    
    # Try to parse as Discord channel link
    if channel_input.startswith("https://discord.com/channels/"):
        try:
            parts = channel_input.split("/")
            if len(parts) >= 6:
                channel_id = parts[5].split("?")[0]  # Remove query params
                if channel_id.isdigit():
                    return channel_id
        except (IndexError, ValueError):
            pass
    
    return None

async def validate_voice_channel(channel_id, guild_id, user_token=None):
    """
    Validate that a channel exists and is a voice channel.
    Uses user tokens from tokens.txt only.
    """
    tokens_to_try = []

    # Use provided user token first
    if user_token:
        tokens_to_try.append(user_token)

    # Load additional tokens from tokens.txt as backup
    try:
        with open("tokens.txt", "r") as f:
            all_tokens = [line.strip() for line in f if line.strip()]
            # Add tokens that aren't already in the list
            for token in all_tokens:
                if token not in tokens_to_try:
                    tokens_to_try.append(token)
    except FileNotFoundError:
        pass  # tokens.txt doesn't exist

    if not tokens_to_try:
        return {"success": False, "message": "No user tokens available for validation"}

    for token in tokens_to_try:
        try:
            url = f"https://discord.com/api/v10/channels/{channel_id}"
            headers = _token_headers(token).copy()

            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as http:
                async with http.get(url, headers=headers) as res:
                    if res.ok:
                        data = await res.json()
                        channel_guild_id = str(data.get("guild_id"))
                        channel_type = data.get("type")

                        if channel_guild_id != str(guild_id):
                            continue  # Try next token

                        if channel_type != 2:
                            return {"success": False, "message": f"Channel type {channel_type} is not voice (2)"}

                        return {"success": True, "message": "Validation successful"}

                    # If 403 or other auth error, try next token
                    if res.status in (403, 401):
                        continue

                    # Other errors - return immediately
                    body = await res.text()
                    return {"success": False, "message": f"Failed to fetch channel: status {res.status}, body: {body}"}

        except Exception as e:
            continue  # Try next token

    return {"success": False, "message": "All user tokens failed to validate channel - channel may not exist or tokens lack permission"}

async def join_server_with_token(token, guild_id):
    BASE = "https://discord.com/api/v9"
    username = token[:15] + "..."
    try:
        async with aiohttp.ClientSession() as http:

            # Step 1: Fetch user info
            async with http.get(f"{BASE}/users/@me", headers=_token_headers(token)) as res:
                if not res.ok:
                    return {"success": False, "username": username, "reason": f"Invalid token (HTTP {res.status})"}
                me = await res.json()
                username = me.get("username", username)
                user_id  = me["id"]

            # Step 2: Headless OAuth2 authorize
            oauth_headers = _token_headers(token).copy()
            oauth_headers["Content-Type"] = "application/json"
            async with http.post(
                f"{BASE}/oauth2/authorize",
                headers=oauth_headers,
                params={
                    "client_id":     OAUTH_CLIENT_ID,
                    "response_type": "code",
                    "redirect_uri":  OAUTH_REDIRECT_URI,
                    "scope":         "identify guilds.join",
                },
                json={"permissions": 0, "authorize": True},
                allow_redirects=False,
            ) as res:
                raw = await res.text()
                print(f"[OAuth2 authorize] status={res.status} body={raw[:400]}")
                body = {}
                try:
                    import json as _json
                    body = _json.loads(raw)
                except Exception:
                    pass
                location = res.headers.get("location", "") or body.get("location", "")
                if res.status not in (200, 302):
                    reason = body.get("message", f"authorize failed ({res.status}): {raw[:200]}")
                    return {"success": False, "username": username, "reason": str(reason)[:200]}
                if "code=" not in location:
                    return {"success": False, "username": username, "reason": f"No code in location: {location[:200]}"}
                oauth_code = location.split("code=")[1].split("&")[0]

            # Step 3: Exchange code for access_token
            import base64
            basic_auth = base64.b64encode(
                f"{OAUTH_CLIENT_ID}:{OAUTH_CLIENT_SECRET}".encode()
            ).decode()
            async with http.post(
                "https://discord.com/api/v10/oauth2/token",
                headers={
                    "Authorization": f"Basic {basic_auth}",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                data={
                    "grant_type":   "authorization_code",
                    "code":         oauth_code,
                    "redirect_uri": OAUTH_REDIRECT_URI,
                },
            ) as res:
                tok = {}
                try:
                    tok = await res.json()
                except Exception:
                    pass
                access_token = tok.get("access_token")
                if not access_token:
                    return {"success": False, "username": username, "reason": f"Token exchange failed: {tok.get('error_description', str(tok))[:80]}"}

            # Step 4: Add user to guild using bot token + user's access_token
            bot_token = os.environ.get("CLIENT_TOKEN", "")
            async with http.put(
                f"{BASE}/guilds/{guild_id}/members/{user_id}",
                headers={
                    "Authorization": f"Bot {bot_token}",
                    "Content-Type":  "application/json",
                },
                json={"access_token": access_token},
            ) as res:
                if res.status in (200, 201):
                    return {"success": True, "username": username, "alreadyIn": False}
                if res.status == 204:
                    return {"success": True, "username": username, "alreadyIn": True}
                data = {}
                try:
                    data = await res.json()
                except Exception:
                    pass
                if "already" in str(data).lower():
                    return {"success": True, "username": username, "alreadyIn": True}
                if data.get("code") == 40007:
                    return {"success": False, "username": username, "reason": "Token is banned from that server"}
                return {"success": False, "username": username, "reason": f"Guild add failed ({res.status}): {data.get('message', '')[:80]}"}

    except Exception as e:
        return {"success": False, "username": username, "reason": str(e)}

class IncompleteGatewayPayload(Exception):
    pass


def is_websocket_open(ws):
    """Return True if websocket appears open for various websocket client types."""
    if ws is None:
        return False
    try:
        closed = getattr(ws, 'closed', None)
        if isinstance(closed, bool):
            return not closed
        open_attr = getattr(ws, 'open', None)
        if isinstance(open_attr, bool):
            return open_attr
        state = getattr(ws, 'state', None)
        if isinstance(state, str):
            return state.lower() == 'open'
        # If we can't determine, assume it's open
        return True
    except Exception:
        return False


def decode_gateway_payload(raw, decompressor=None):
    """Decode Discord gateway payloads for zlib-stream and text frames."""
    if isinstance(raw, str):
        try:
            json.loads(raw)
            return raw
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid text gateway payload: {e}")

    if not isinstance(raw, (bytes, bytearray)):
        raise Exception("Unexpected gateway payload type")

    # If it starts with { or [, it's likely already JSON (uncompressed)
    if raw.startswith(b"{") or raw.startswith(b"["):
        try:
            text = raw.decode("utf-8")
            json.loads(text)
            return text
        except Exception as e:
            raise Exception(f"Could not parse uncompressed JSON: {e}")

    # Discord zlib-stream payloads are complete when they end with zlib stream suffix
    if not raw.endswith(b"\x00\x00\xff\xff"):
        raise IncompleteGatewayPayload()

    # Use provided decompressor (persistent per-connection) when available
    compressed_data = raw[:-4]
    tried = []

    if decompressor is not None:
        tried.append("persistent_decompressor")
        try:
            text = decompressor.decompress(compressed_data)
            if isinstance(text, bytes):
                text = text.decode("utf-8")
            json.loads(text)
            return text
        except Exception:
            pass

    # Try common zlib variants (raw deflate, zlib header, gzip wrapper)
    zlib_methods = [(-zlib.MAX_WBITS, "zlib_raw"), (zlib.MAX_WBITS, "zlib"), (zlib.MAX_WBITS | 16, "gzip")] 
    for wbits, name in zlib_methods:
        tried.append(name)
        try:
            text = zlib.decompress(compressed_data, wbits).decode("utf-8")
            json.loads(text)
            return text
        except Exception:
            pass

    # Try using decompressobj variants (incremental decompression)
    for wbits, name in zlib_methods:
        tried.append(f"decompressobj_{name}")
        try:
            dobj = zlib.decompressobj(wbits)
            out = dobj.decompress(compressed_data)
            if isinstance(out, bytes):
                out = out.decode("utf-8")
            json.loads(out)
            return out
        except Exception:
            pass

    # Try other compression algorithms if available
    tried.append("bz2")
    try:
        text = bz2.decompress(compressed_data).decode("utf-8")
        json.loads(text)
        return text
    except Exception:
        pass

    tried.append("lzma")
    try:
        text = lzma.decompress(compressed_data).decode("utf-8")
        json.loads(text)
        return text
    except Exception:
        pass

    if brotli is not None:
        tried.append("brotli")
        try:
            text = brotli.decompress(compressed_data).decode("utf-8")
            json.loads(text)
            return text
        except Exception:
            pass

    # Last resort: try interpreting as UTF-8 text
    tried.append("utf8_raw")
    try:
        text = compressed_data.decode("utf-8")
        json.loads(text)
        return text
    except Exception:
        first_bytes = raw[:20].hex() if len(raw) >= 20 else raw.hex()
        raise Exception(f"Could not decode gateway frame. Tried: {tried}. Data starts with: {first_bytes}")


async def recv_gateway_payload(websocket, decompressor):
    buffer = bytearray()
    while True:
        raw = await websocket.recv()
        if isinstance(raw, str):
            return raw
        # raw is bytes
        buffer.extend(raw)

        # Check for zlib-stream sync marker
        if not buffer.endswith(b"\x00\x00\xff\xff"):
            # Need more data
            continue

        try:
            # decode using persistent decompressor
            payload = decode_gateway_payload(bytes(buffer), decompressor=decompressor)
            buffer.clear()
            return payload
        except IncompleteGatewayPayload:
            continue
        except Exception:
            # If decoding failed despite sync marker, raise to caller for fallback
            raise


async def connect_gateway(token, presence=False, intents=0):
    """
    Connect to Discord Gateway WebSocket and handle initial handshake.
    First tries with zlib-stream compression, falls back to plain JSON if compression fails.
    Returns the WebSocket connection and session info.
    """
    # Try with compression first, but have a fallback
    for use_compression in [True, False]:
        try:
            if use_compression:
                gateway_url = "wss://gateway.discord.gg/?v=10&encoding=json&compress=zlib-stream"
                print("[GATEWAY] Attempting connection WITH zlib-stream compression...")
            else:
                gateway_url = "wss://gateway.discord.gg/?v=10&encoding=json"
                print("[GATEWAY] Attempting connection WITHOUT compression (fallback)...")
            
            websocket = await asyncio.wait_for(
                websockets.connect(
                    gateway_url,
                    max_size=64 * 1024 * 1024,  # 64MB limit to handle large payloads
                    compression=None,  # Let Discord handle compression via URL parameter
                    close_timeout=10,
                    ping_interval=None  # Disable automatic ping/pong from websockets lib
                ),
                timeout=10
            )
            print("[GATEWAY] Connected successfully")

            # Create persistent zlib decompressor for this connection
            decompressor = zlib.decompressobj()

            # Receive HELLO (use persistent decompressor)
            hello_text = await asyncio.wait_for(recv_gateway_payload(websocket, decompressor), timeout=10)
            hello_data = json.loads(hello_text)
            
            if hello_data["op"] != 10:
                await websocket.close()
                raise Exception(f"Expected HELLO (op 10), got {hello_data['op']}")

            heartbeat_interval = hello_data["d"]["heartbeat_interval"]
            print(f"[GATEWAY] Received HELLO, heartbeat interval: {heartbeat_interval}ms")

            # Start heartbeat task
            heartbeat_task = asyncio.create_task(send_heartbeats(websocket, heartbeat_interval))

            # Send IDENTIFY
            identify_payload = {
                "op": 2,
                "d": {
                    "token": token,
                    "intents": 0,  # No intents needed for voice or presence-only connections
                    "properties": {
                        "$os": "windows",
                        "$browser": "python",
                        "$device": "python"
                    }
                }
            }
            if presence:
                identify_payload["d"]["presence"] = {
                    "status": "online",
                    "since": 0,
                    "activities": [],
                    "afk": False
                }

            await websocket.send(json.dumps(identify_payload))
            print("[GATEWAY] Sent IDENTIFY")

            # Receive READY
            try:
                ready_text = await asyncio.wait_for(recv_gateway_payload(websocket, decompressor), timeout=10)
                ready_data = json.loads(ready_text)
            except asyncio.TimeoutError:
                await websocket.close()
                raise Exception("READY timeout")
            
            if ready_data["op"] != 0 or ready_data["t"] != "READY":
                await websocket.close()
                raise Exception(f"Expected READY, got op={ready_data.get('op')}, t={ready_data.get('t')}")

            session_id = ready_data["d"].get("session_id")
            user_id = ready_data["d"].get("user", {}).get("id")
            
            if not session_id or not user_id:
                await websocket.close()
                raise Exception("Missing session_id or user_id in READY")
            
            mode_str = "compressed" if use_compression else "uncompressed"
            print(f"[GATEWAY] READY received in {mode_str} mode, session_id: {session_id}, user_id: {user_id}")
            
            del ready_data
            return websocket, session_id, user_id, heartbeat_interval, heartbeat_task, decompressor

        except Exception as e:
            error_str = str(e)
            print(f"[GATEWAY] Connection attempt failed: {error_str[:100]}")
            
            # If compression mode failed, try without compression (unless we already are)
            if use_compression and ("decode" in error_str.lower() or "zlib" in error_str.lower() or "utf" in error_str.lower()):
                print("[GATEWAY] Compression issue detected, will retry without compression...")
                continue
            else:
                # Final attempt failed
                raise Exception(f"[GATEWAY] Gateway connection failed: {e}")


async def send_heartbeats(websocket, interval):
    """
    Send periodic heartbeats to keep the gateway connection alive.
    """
    try:
        while True:
            await asyncio.sleep(interval / 1000)  # Convert ms to seconds
            heartbeat_payload = {
                "op": 1,
                "d": None
            }
            await websocket.send(json.dumps(heartbeat_payload))
            # print("[HEARTBEAT] Sent")  # Uncomment for debug
    except Exception as e:
        print(f"[HEARTBEAT] Error: {e}")
        return


async def drain_gateway_messages(websocket, decompressor):
    """
    Drain incoming gateway events for presence-only connections without buffering.
    """
    try:
        while True:
            try:
                msg = await asyncio.wait_for(recv_gateway_payload(websocket, decompressor), timeout=60)
                # Immediately discard to prevent buffering
                del msg
            except asyncio.TimeoutError:
                # Reconnect if no messages for 60 seconds
                break
    except Exception:
        return


def is_token_voice_connected(token):
    for connections in ACTIVE_VOICE_CONNECTIONS.values():
        if token in connections:
            return True
    return False


async def ensure_presence_gateway(token):
    existing = PRESENCE_GATEWAY_CONNECTIONS.get(token)
    if existing and not existing.get("disconnected"):
        existing["refcount"] += 1
        # Check if connection is too old (>5 minutes) and reconnect if needed
        if time.time() - existing.get("created_at", time.time()) > 300:
            print(f"[PRESENCE] Connection age exceeded for {token[:20]}, scheduling reconnect")
            existing["should_reconnect"] = True
        return existing

    if is_token_voice_connected(token):
        PRESENCE_GATEWAY_CONNECTIONS[token] = {
            "gateway_ws": None,
            "heartbeat_task": None,
            "reader_task": None,
            "refcount": 1,
            "voice_based": True,
            "created_at": time.time(),
            "disconnected": False,
        }
        return PRESENCE_GATEWAY_CONNECTIONS[token]

    try:
        websocket, session_id, user_id, heartbeat_interval, heartbeat_task, decompressor = await connect_gateway(token, presence=True)
        reader_task = asyncio.create_task(drain_gateway_messages(websocket, decompressor))
        PRESENCE_GATEWAY_CONNECTIONS[token] = {
            "gateway_ws": websocket,
            "heartbeat_task": heartbeat_task,
            "reader_task": reader_task,
            "refcount": 1,
            "voice_based": False,
            "created_at": time.time(),
            "disconnected": False,
        }
        return PRESENCE_GATEWAY_CONNECTIONS[token]
    except Exception as e:
        print(f"[PRESENCE] Failed to open presence gateway for token: {e}")
        return None


async def release_presence_gateway(token):
    info = PRESENCE_GATEWAY_CONNECTIONS.get(token)
    if not info:
        return

    info["refcount"] = max(0, info.get("refcount", 1) - 1)
    if info["refcount"] > 0:
        return

    PRESENCE_GATEWAY_CONNECTIONS.pop(token, None)

    if info.get("voice_based"):
        return

    if info.get("heartbeat_task"):
        try:
            info["heartbeat_task"].cancel()
            await info["heartbeat_task"]
        except Exception:
            pass

    if info.get("reader_task"):
        try:
            info["reader_task"].cancel()
            await info["reader_task"]
        except Exception:
            pass

    if info.get("gateway_ws"):
        try:
            await info["gateway_ws"].close()
        except Exception:
            pass


async def start_presence_for_tokens(tokens):
    for token in set(tokens or []):
        await ensure_presence_gateway(token)


async def close_presence_for_tokens(tokens):
    for token in set(tokens or []):
        await release_presence_gateway(token)


async def send_voice_state_update(websocket, guild_id, channel_id):
    """
    Send VOICE_STATE_UPDATE to join voice channel.
    """
    voice_state_payload = {
        "op": 4,
        "d": {
            "guild_id": str(guild_id),
            "channel_id": str(channel_id),
            "self_mute": False,
            "self_deaf": False
        }
    }

    await websocket.send(json.dumps(voice_state_payload))
    print(f"[VOICE] Sent VOICE_STATE_UPDATE for guild {guild_id}, channel {channel_id}")


async def handle_voice_events(websocket, decompressor, timeout=30, guild_id=None, user_id=None):
    """
    Listen for VOICE_STATE_UPDATE and VOICE_SERVER_UPDATE events.
    Both are REQUIRED for a successful voice connection.
    Returns voice server info and state info when both are received.
    """
    voice_state_received = False
    voice_server_received = False
    voice_state_data = None
    voice_server_data = None

    print("[VOICE] Listening for voice events (need both VOICE_STATE_UPDATE and VOICE_SERVER_UPDATE)...")

    start_time = asyncio.get_event_loop().time()

    while not (voice_state_received and voice_server_received):
        elapsed = asyncio.get_event_loop().time() - start_time
        if elapsed > timeout:
            print(f"[VOICE] Timeout after {elapsed:.1f}s - VOICE_STATE={voice_state_received}, VOICE_SERVER={voice_server_received}")
            raise Exception(f"Timeout waiting for voice events (got state={voice_state_received}, server={voice_server_received})")

        try:
            # Set a short timeout for receiving messages and decode payloads consistently
            message = await asyncio.wait_for(recv_gateway_payload(websocket, decompressor), timeout=5.0)
            # Raw event logging for debugging
            try:
                print(f"[RAW EVENT] {message[:200]}")
            except Exception:
                pass
            data = json.loads(message)

            if data["op"] == 0:  # Dispatch event
                event_type = data["t"]

                if event_type == "VOICE_STATE_UPDATE":
                    payload = data["d"]
                    # Filter by guild_id and user_id if provided
                    if guild_id is not None and str(payload.get("guild_id")) != str(guild_id):
                        continue
                    if user_id is not None and str(payload.get("user_id")) != str(user_id):
                        continue
                    voice_state_data = payload
                    voice_state_received = True
                    print(f"[VOICE] ✓ Received VOICE_STATE_UPDATE: session_id={voice_state_data.get('session_id')}")

                elif event_type == "VOICE_SERVER_UPDATE":
                    payload = data["d"]
                    if guild_id is not None and str(payload.get("guild_id")) != str(guild_id):
                        continue
                    voice_server_data = payload
                    voice_server_received = True
                    print(f"[VOICE] ✓ Received VOICE_SERVER_UPDATE: endpoint={voice_server_data.get('endpoint')}")

        except asyncio.TimeoutError:
            continue  # No message received, continue waiting
        except json.JSONDecodeError:
            continue  # Bad JSON, skip

    # Verify we have everything required
    if not voice_state_data or not voice_state_data.get("session_id"):
        raise Exception("Missing session_id in VOICE_STATE_UPDATE")
    
    if not voice_server_data or not voice_server_data.get("endpoint"):
        raise Exception("Missing endpoint in VOICE_SERVER_UPDATE")

    print("[VOICE] Both events received successfully")
    return voice_state_data, voice_server_data


async def connect_to_voice_server(voice_server_data, voice_state_data, guild_id=None, user_id=None, session_id=None):
    """
    Connect to voice WebSocket server and complete handshake.
    """
    endpoint = voice_server_data["endpoint"]
    voice_token = voice_server_data["token"]

    # Get data from voice_state_data if available, otherwise use provided params
    if voice_state_data:
        session_id = voice_state_data["session_id"]
        user_id = voice_state_data["user_id"]
        guild_id = voice_state_data["guild_id"]
    elif not all([guild_id, user_id, session_id]):
        raise Exception("Missing required voice connection data")

    # Remove port if present and add wss://
    if ":" in endpoint:
        endpoint = endpoint.split(":")[0]
    voice_ws_url = f"wss://{endpoint}?v=4"

    print(f"[VOICE] Connecting to voice server: {voice_ws_url}")

    try:
        voice_ws = await websockets.connect(voice_ws_url)

        # Step 1: Receive Hello (op 8)
        hello_data = json.loads(await voice_ws.recv())
        if hello_data["op"] != 8:  # Hello op code
            raise Exception(f"Expected voice Hello (op 8), got {hello_data['op']}")

        voice_heartbeat_interval = hello_data["d"]["heartbeat_interval"]
        print(f"[VOICE] Received Hello, heartbeat interval: {voice_heartbeat_interval}ms")

        # Step 2: Start voice heartbeats
        voice_heartbeat_task = asyncio.create_task(send_voice_heartbeats(voice_ws, voice_heartbeat_interval))

        # Step 3: Send IDENTIFY
        identify_payload = {
            "op": 0,
            "d": {
                "server_id": str(guild_id),
                "user_id": str(user_id),
                "session_id": session_id,
                "token": voice_token
            }
        }

        await voice_ws.send(json.dumps(identify_payload))
        print("[VOICE] Sent voice IDENTIFY")

        # Step 4: Receive READY or E2EE Hello
        response_data = json.loads(await voice_ws.recv())

        if response_data["op"] == 2:  # READY
            print("[VOICE] Voice READY received (no E2EE required)")
        elif response_data["op"] == 8:  # Hello (E2EE required)
            print("[VOICE] Voice Hello received (E2EE required)")

            async def send_dave_select_protocol():
                e2ee_ready_payload = {
                    "op": 1,  # SELECT_PROTOCOL
                    "d": {
                        "protocol": "dave",
                        "data": {
                            "version": 1,
                            "client_id": str(user_id),
                            "mode": "aead_aes256_gcm_rtpsize",
                            "audio_codec": "opus",
                            "video_codec": "H264"
                        }
                    }
                }
                await voice_ws.send(json.dumps(e2ee_ready_payload))
                print("[VOICE] Sent E2EE SELECT_PROTOCOL with DAVE format")

            await send_dave_select_protocol()

            # Receive SESSION_DESCRIPTION or error
            session_data = json.loads(await voice_ws.recv())
            if session_data["op"] == 4:  # SESSION_DESCRIPTION
                print("[VOICE] E2EE SESSION_DESCRIPTION received")
            else:
                print(f"[VOICE] Unexpected op after E2EE: {session_data['op']} - {session_data.get('d')}")
                if session_data.get('op') == 9 or (isinstance(session_data.get('d'), dict) and session_data['d'].get('code') == 4017):
                    raise Exception(f"E2EE/DAVE handshake failed: {session_data['d']}")
                raise Exception(f"Unexpected voice response after E2EE SELECT_PROTOCOL: {session_data}")

        else:
            raise Exception(f"Expected voice READY (op 2) or Hello (op 8), got {response_data['op']}")

        print("[VOICE] Voice connection established successfully")

        # Return both the WebSocket and heartbeat task
        return voice_ws, voice_heartbeat_task

    except Exception as e:
        print(f"[VOICE] Voice server connection failed: {e}")
        raise


async def send_voice_heartbeats(websocket, interval):
    """
    Send periodic heartbeats to keep the voice WebSocket connection alive.
    Catches errors but doesn't die on them - just logs and continues.
    """
    consecutive_errors = 0
    max_consecutive_errors = 5
    
    try:
        while True:
            try:
                await asyncio.sleep(interval / 1000)  # Convert ms to seconds
                heartbeat_payload = {
                    "op": 3,  # Voice heartbeat op code
                    "d": None
                }
                await websocket.send(json.dumps(heartbeat_payload))
                consecutive_errors = 0  # Reset error counter on success
                # print(f"[VOICE HEARTBEAT] Sent ({interval}ms interval)")
            except Exception as hb_error:
                consecutive_errors += 1
                error_str = str(hb_error)
                
                # Only log periodically to avoid spam
                if consecutive_errors % 3 == 1:
                    print(f"[VOICE HEARTBEAT] Error (attempt {consecutive_errors}): {error_str[:60]}")
                
                # If too many consecutive errors, stop and log final error
                if consecutive_errors >= max_consecutive_errors:
                    print(f"[VOICE HEARTBEAT] Stopping after {max_consecutive_errors} consecutive errors")
                    break
                
                await asyncio.sleep(1)  # Wait before retry
                
    except asyncio.CancelledError:
        print("[VOICE HEARTBEAT] Heartbeat task cancelled")
    except Exception as e:
        print(f"[VOICE HEARTBEAT] Fatal error: {e}")


async def disconnect_voice_connections(uid):
    """Disconnect all voice connections for a user."""
    if uid not in ACTIVE_VOICE_CONNECTIONS:
        return 0
    
    disconnected_count = 0
    for token, connection_info in ACTIVE_VOICE_CONNECTIONS[uid].items():
        try:
            # Cancel heartbeat tasks if they exist
            voice_heartbeat = connection_info.get("voice_heartbeat_task")
            if voice_heartbeat:
                voice_heartbeat.cancel()
                try:
                    await voice_heartbeat
                except:
                    pass
            
            gateway_heartbeat = connection_info.get("heartbeat_task")
            if gateway_heartbeat:
                gateway_heartbeat.cancel()
                try:
                    await gateway_heartbeat
                except:
                    pass
            
            # Close voice WebSocket
            voice_ws = connection_info.get("voice_ws")
            if voice_ws:
                try:
                    await voice_ws.close()
                except:
                    pass

            # Close gateway WebSocket if it exists and is open
            gateway_ws = connection_info.get("gateway_ws")
            if gateway_ws:
                try:
                    await gateway_ws.close()
                except:
                    pass
            
            disconnected_count += 1
            print(f"[VC Disconnect:{uid}] Disconnected token from voice")
        except Exception as e:
            print(f"[VC Disconnect:{uid}] Error disconnecting token: {e}")
    
    # Clear the connections
    ACTIVE_VOICE_CONNECTIONS.pop(uid, None)
    return disconnected_count


async def join_voice_channel_with_token(token, guild_id, channel_id, max_attempts=3):
    """
    Join a voice channel using Discord Gateway WebSocket flow with retry logic.
    This is the correct way to join voice channels (not REST API).
    
    Attempts connection with exponential backoff on failure.
    """
    print(f"[VC] Starting voice join: token={token[:20]}... guild={guild_id} channel={channel_id}")
    
    websocket = None
    session_id = None
    gateway_user_id = None
    heartbeat_task = None
    decompressor = None

    for attempt in range(1, max_attempts + 1):
        try:
            # Verify token is in guild
            in_guild, user_id = await verify_token_in_guild(token, guild_id)
            if not in_guild:
                if attempt < max_attempts:
                    wait_time = 2 ** attempt  # Exponential: 4, 8 seconds
                    print(f"[VC] Token not in guild (attempt {attempt}/{max_attempts}). Waiting {wait_time}s before retry...")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    return {"success": False, "status": None, "reason": "Token not in guild after retries"}

            # Ensure we have a gateway connection with persistent decompressor
            if websocket is None or getattr(websocket, 'closed', False):
                try:
                    websocket, session_id, gateway_user_id, heartbeat_interval, heartbeat_task, decompressor = await connect_gateway(token, intents=128)
                    print(f"[VC] [Attempt {attempt}] Gateway connected (session_id={session_id[:16]}...)")
                    # Wait a short moment after READY before sending OP4
                    await asyncio.sleep(2)
                except Exception as e:
                    raise

            # Send voice state update (OP4) using existing gateway
            await send_voice_state_update(websocket, guild_id, channel_id)

            # Listen for voice events with proper timeout, using persistent decompressor
            voice_state_data, voice_server_data = await handle_voice_events(websocket, decompressor, timeout=20, guild_id=guild_id, user_id=gateway_user_id)
            
            if not voice_server_data:
                raise Exception("No VOICE_SERVER_UPDATE received")

            # Connect to voice server
            voice_ws, voice_heartbeat_task = await connect_to_voice_server(
                voice_server_data, voice_state_data, guild_id, gateway_user_id, session_id
            )

            # Voice connection established - we can close the gateway connection now
            # It was only needed for the VOICE_STATE_UPDATE and VOICE_SERVER_UPDATE events
            try:
                heartbeat_task.cancel()
                await asyncio.wait_for(heartbeat_task, timeout=1)
            except:
                pass
            
            try:
                await websocket.close()
            except:
                pass

            print(f"[VC] [SUCCESS on attempt {attempt}] Voice channel joined successfully!")
            return {
                "success": True,
                "status": 200,
                "reason": None,
                "voice_ws": voice_ws,
                "gateway_ws": None,  # Gateway closed - only voice_ws is active
                "heartbeat_task": None,  # Gateway heartbeat stopped
                "voice_heartbeat_task": voice_heartbeat_task  # Only voice heartbeat continues
            }

        except Exception as e:
            error_msg = f"{str(e)}"
            print(f"[VC] [FAIL attempt {attempt}/{max_attempts}] {error_msg}")
            
            # Clean up this attempt's resources
            if 'voice_heartbeat_task' in locals() and voice_heartbeat_task:
                try:
                    voice_heartbeat_task.cancel()
                    await asyncio.wait_for(voice_heartbeat_task, timeout=1)
                except:
                    pass
                voice_heartbeat_task = None
            
            
            if 'voice_ws' in locals() and voice_ws:
                try:
                    await asyncio.wait_for(voice_ws.close(), timeout=2)
                except:
                    pass
                voice_ws = None
            
            # Keep gateway connection alive across retries to preserve session and decompressor.
            # Only clean up gateway on the final attempt.
            if attempt >= max_attempts:
                if 'heartbeat_task' in locals() and heartbeat_task:
                    try:
                        heartbeat_task.cancel()
                        await asyncio.wait_for(heartbeat_task, timeout=1)
                    except:
                        pass
                    heartbeat_task = None
                if attempt >= max_attempts:
                    if 'heartbeat_task' in locals() and heartbeat_task:
                        try:
                            heartbeat_task.cancel()
                            await asyncio.wait_for(heartbeat_task, timeout=1)
                        except:
                            pass
                        heartbeat_task = None
                    if 'websocket' in locals() and websocket:
                        try:
                            close_result = None
                            try:
                                close_result = websocket.close()
                            except TypeError:
                                # Some websocket-like objects may require await websocket.close()
                                try:
                                    await websocket.close()
                                    close_result = None
                                except Exception:
                                    pass
                            if asyncio.iscoroutine(close_result):
                                await asyncio.wait_for(close_result, timeout=2)
                        except Exception:
                            pass
                        websocket = None
            
            # Retry with backoff
            if attempt < max_attempts:
                wait_time = 2 ** attempt  # Exponential: 4, 8 seconds
                print(f"[VC] Waiting {wait_time}s before retry {attempt + 1}/{max_attempts}...")
                await asyncio.sleep(wait_time)
            else:
                return {"success": False, "status": None, "reason": f"Voice join failed after {max_attempts} attempts: {error_msg}"}
    
    return {"success": False, "status": None, "reason": "Unexpected error in voice join retry logic"}

# ─── Send message helpers ─────────────────────────────────────────────────────

_MSG_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) discord/1.0.9015 Chrome/108.0.5359.215 Electron/22.3.2 Safari/537.36"
)

def _msg_headers(token, is_bot=False):
    auth = f"Bot {token}" if is_bot else token
    return {
        "Authorization": auth,
        "Content-Type": "application/json",
        "User-Agent": _MSG_USER_AGENT,
        "X-Debug-Options": "bugReporterEnabled",
        "X-Discord-Locale": "en-US",
        "X-Discord-Timezone": "America/New_York",
        "Origin": "https://discord.com",
        "Referer": "https://discord.com/channels/@me",
    }

def parse_discord_error(status, response_text):
    """Parse Discord API error response and return user-friendly message."""
    error_details = {"status": status, "raw": response_text[:100]}
    
    # Try to parse JSON response
    try:
        data = json.loads(response_text) if response_text else {}
        error_details["parsed"] = data
    except:
        data = {}
    
    # Map HTTP status codes to user-friendly messages
    error_messages = {
        400: {
            "title": "❌ Channel Unknown",
            "reason": "The channel ID is invalid or the channel was deleted",
            "fix": "Check that the channel ID is correct and the channel still exists",
            "discord_code": data.get("code")
        },
        401: {
            "title": "🔐 Token Problem",
            "reason": "Your token is invalid or expired",
            "fix": "Check if token is correct or regenerate it",
            "discord_code": data.get("code")
        },
        403: {
            "title": "🚫 No Permission",
            "reason": "Bot doesn't have permission to send messages in this channel",
            "fix": "Add bot permissions or check channel/server settings",
            "discord_code": data.get("code")
        },
        404: {
            "title": "❓ Channel Not Found",
            "reason": "The channel you're trying to message doesn't exist",
            "fix": "Make sure the channel ID is correct",
            "discord_code": data.get("code")
        },
        429: {
            "title": "⏱️ Rate Limited",
            "reason": "Sending messages too fast - Discord is blocking us temporarily",
            "fix": "Increase the delay between messages",
            "discord_code": data.get("code")
        },
        500: {
            "title": "⚠️ Discord Server Error",
            "reason": "Discord API is having issues",
            "fix": "Wait a few minutes and try again",
            "discord_code": data.get("code")
        }
    }
    
    if status in error_messages:
        return error_messages[status]
    else:
        return {
            "title": f"⚠️ Error {status}",
            "reason": (data.get("message", "Unknown error occurred"))[:200],
            "fix": """Check image url format , it should be url1
            url3 (line separted , no commas) if that doesnt work then make a support ticket""",
            "discord_code": data.get("code")
        }

async def validate_adv_token(token, acc_id=None):
    """
    Validate if a token is valid and return status.
    Returns: (is_valid: bool, message: str, user_info: dict, is_bot: bool)
    """
    async def try_auth(auth):
        try:
            async with aiohttp.ClientSession() as http:
                headers = {
                    "Authorization": auth,
                    "Content-Type": "application/json",
                    "User-Agent": _MSG_USER_AGENT,
                }
                async with http.get("https://discord.com/api/v9/users/@me", headers=headers, timeout=aiohttp.ClientTimeout(total=5)) as res:
                    if res.status == 200:
                        user_data = await res.json()
                        return True, user_data
                    else:
                        return False, {}
        except:
            return False, {}

    # Try as user token first
    valid, user_data = await try_auth(token)
    if valid:
        return True, "Token is valid (user token)", user_data, False
    
    # Try as bot token
    valid, user_data = await try_auth(f"Bot {token}")
    if valid:
        return True, "Token is valid (bot token)", user_data, True
    
    return False, "❌ Token is invalid or expired", {}, False

def format_adv_error_message(status, response_text, channel, channels_list, total_images, acc_id):
    """Format error message in a non-coder-friendly way."""
    error_info = parse_discord_error(status, response_text)
    
    lines = [
        f"❌ **{error_info['title']}** — Channel ID: `{channel}`",
        f"",
        f"📝 What happened:",
        f"  • {error_info['reason']}",
        f"",
        f"🔧 What to try:",
    ]
    
    if status == 401:
        lines.extend([
            f"  • Check your token is correct and not expired",
            f"  • Regenerate bot/user token if old",
            f"  • Use `/testtoken` to validate your token",
        ])
    elif status == 400:
        lines.extend([
            f"  • {error_info['fix']}",
            f"  • Remove this channel from your account setup and add a valid one",
            f"  • Use `/advpanel` → Manage → remove the problematic channel",
        ])
    else:
        lines.extend([
            f"  • {error_info['fix']}",
            f"  • Check bot is in the server/channel",
            f"  • Try a different channel",
        ])
    
    lines.extend([
        f"",
        f"📊 Details:",
        f"  • Account: `{acc_id}`",
        f"  • Channel count: {len(channels_list)}",
        f"  • Problem channel: `{channel}`",
        f"  • Images: {total_images}",
        f"  • Status code: {status}",
    ])
    
    if error_info.get("discord_code"):
        lines.append(f"  • Discord error code: {error_info['discord_code']}")
    
    lines.extend([
        f"",
        f"⏸️ Auto Adv paused for this account until you fix the issue.",
        f"💡 **Run `/testtoken` in your DMs to validate your token, or use `/advpanel` to manage channels.**"
    ])
    
    return "\n".join(lines)

async def _post_message(token, channel_id, content=None, extra=None, is_bot=False):
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
    payload = {"content": content or ""}
    if extra:
        payload.update(extra)
    async with aiohttp.ClientSession() as http:
        res = await http.post(url, headers=_msg_headers(token, is_bot), json=payload)
        if res.status == 429:
            wait = 5
            try:
                b = await res.json()
                wait = (b.get("retry_after") or 5) + 0.5
            except Exception:
                pass
            await asyncio.sleep(wait)
            res = await http.post(url, headers=_msg_headers(token, is_bot), json=payload)
        response_text = ""
        try:
            response_text = await res.text()
        except Exception:
            pass
        return res.status, response_text


async def _react_to_message(token, channel_id, message_id, emoji):
    """React to a message using a token account."""
    # emoji must be URL-encoded; custom emoji should be in name:id format or raw emoji
    try:
        enc = quote(emoji, safe='')
    except Exception:
        enc = quote(str(emoji))
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}/reactions/{enc}/@me"
    async with aiohttp.ClientSession() as http:
        res = await http.put(url, headers=_msg_headers(token))
        if res.status == 429:
            wait = 5
            try:
                b = await res.json()
                wait = (b.get("retry_after") or 5) + 0.5
            except Exception:
                pass
            await asyncio.sleep(wait)
            res = await http.put(url, headers=_msg_headers(token))
        try:
            text = await res.text()
        except Exception:
            text = ""
        return res.status, text

async def fetch_channel_messages(token, channel_id, limit=20):
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages?limit={limit}"
    async with aiohttp.ClientSession() as http:
        async with http.get(url, headers=_msg_headers(token)) as res:
            if res.status != 200:
                return []
            try:
                return await res.json()
            except Exception:
                return []

async def get_token_user_id(token):
    url = "https://discord.com/api/v9/users/@me"
    async with aiohttp.ClientSession() as http:
        async with http.get(url, headers=_msg_headers(token)) as res:
            if res.status != 200:
                return None
            try:
                data = await res.json()
                return str(data.get("id")) if data else None
            except Exception:
                return None

async def choose_reply_target(session, token, messages):
    token_user_id = session.get("tokenUserIds", {}).get(token)
    if token_user_id is None:
        token_user_id = await get_token_user_id(token)
        if token_user_id:
            session.setdefault("tokenUserIds", {})[token] = token_user_id

    candidates = []
    for msg in messages:
        author = msg.get("author", {})
        if not author:
            continue
        if author.get("bot"):
            continue
        if token_user_id and str(author.get("id")) == token_user_id:
            continue
        content = msg.get("content", "").strip()
        if not content:
            continue
        candidates.append(msg)

    if not candidates:
        return None

    recent = candidates[:8]
    weights = [8 - i for i in range(len(recent))]
    try:
        return random.choices(recent, weights=weights, k=1)[0]
    except Exception:
        return random.choice(recent)


def build_reply_message(pool, target_message):
    if not pool:
        return "yeah"

    target_text = target_message.get("content", "").strip()
    target_lower = target_text.lower()

    if "?" in target_text:
        return random.choice([
            "I was wondering the same thing.",
            "That’s a good question, I’m curious too.",
            "Not sure, but I feel like it depends.",
            "What do you think about that?",
            "Probably later, but who knows.",
            "I want to hear what others think.",
        ])

    if any(word in target_lower for word in ("music", "song", "listen", "beat", "playlist")):
        return random.choice([
            "That sounds fire, what song are you on?",
            "I’ve been in the mood for chill tracks too.",
            "Nice, any recommendation for a good playlist?",
            "I could use something new to listen to.",
            "Same, the right music really changes the vibe.",
        ])

    if any(word in target_lower for word in ("game", "playing", "played", "gamer", "stream", "play")):
        return random.choice([
            "What game is everyone talking about?",
            "I’m down for a good match if someone wants to team up.",
            "That sounds fun, what are you playing?",
            "I’ve been looking for a new game to try.",
            "Nice, I’d join if I had time.",
        ])

    if any(word in target_lower for word in ("server", "vibe", "chat", "quiet", "active", "people", "community")):
        return random.choice([
            "Yeah, this server has a really solid vibe.",
            "I agree, the chat is chill and easy to follow.",
            "It feels like people actually hang out here.",
            "Honestly, this place is one of the better servers.",
            "Feels way more active than most of the stuff I’m in.",
        ])

    if any(word in target_lower for word in ("bored", "nothing", "meh", "tired", "slow", "quiet")):
        return random.choice([
            "Same, I’m just trying to keep the convo moving.",
            "Maybe we should start a random topic?",
            "I feel that, let’s make the chat more interesting.",
            "Quiet servers can turn into good convo spots.",
            "Anyone got something fun to share?",
        ])

    if any(word in target_lower for word in ("buy", "sell", "trade", "selling", "buying", "trade")):
        return random.choice([
            "That sounds like a solid deal, who’s interested?",
            "I’ve been looking for something like that too.",
            "Nice, any trusted sellers here?",
            "Seems like there’s a market for that right now.",
            "If anyone’s selling, I might be interested.",
        ])

    if any(word in target_lower for word in ("hello", "hi", "hey", "sup", "yo", "what's up", "wanna")):
        return random.choice([
            "Hey, good to see you here.",
            "Yo, what’s up?",
            "Hi, how’s it going?",
            "Sup, wanna chat?",
        ])

    content = random.choice(pool)
    if random.random() < 0.60:
        content = f"{random.choice(CHAT_REPLY_PREFIXES)} {content[0].lower() + content[1:]}" if content else content
    return content

async def _download_image(session, url):
    try:
        async with session.get( url,headers={"User-Agent": _MSG_USER_AGENT},timeout=15) as res:
            if res.status != 200:
                return None
            data = await res.read()
            if not data:
                return None
            content_type = res.headers.get("Content-Type", "application/octet-stream").split(";")[0].strip()
            if "image" not in content_type.lower():
                return None
            parsed = urlparse(url)
            filename = Path(parsed.path).name or f"image_{uuid.uuid4().hex}"
            if not Path(filename).suffix:
                ext = mimetypes.guess_extension(content_type) or ".png"
                filename = f"{filename}{ext}"
            return filename, data, content_type
    except Exception:
        return None

async def _post_message_with_files(token, channel_id, content=None, file_urls=None, is_bot=False):
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
    payload = {"content": content or ""}
    headers = _msg_headers(token, is_bot).copy()
    headers.pop("Content-Type", None)

    async with aiohttp.ClientSession() as http:
        form = aiohttp.FormData()
        attachments = []

        if file_urls:
            file_index = 0
            for file_url in file_urls[:5]:
                downloaded = await _download_image(http, file_url)
                if not downloaded:
                    continue
                filename, data, content_type = downloaded     
                attachments.append({
                    "id": str(file_index),
                    "filename": filename,
                    "description": "image"
                })

                form.add_field(
                    name=f"files[{file_index}]",
                    value=data,
                    filename=filename,
                    content_type=content_type
                  )
                file_index += 1
                if file_index >= 5:
                    break

            if not attachments:
                return 400, "Image URL invalid / blocked / unsupported format."


        form.add_field("payload_json", json.dumps(payload), content_type="application/json")
        res = await http.post(url, headers=headers, data=form)
        if res.status == 429:
            wait = 5
            try:
                b = await res.json()
                wait = (b.get("retry_after") or 5) + 0.5
            except Exception:
                pass
            await asyncio.sleep(wait)
            res = await http.post(url, headers=headers, data=form)
        response_text = ""
        try:
            response_text = await res.text()
        except Exception:
            pass
        return res.status, response_text


def normalize_image_urls(value):
    if not value:
        return []
    raw_urls = re.findall(r"(https?://[^\s\"'<>]+|www\.[^\s\"'<>]+)", value.strip(), flags=re.IGNORECASE)
    normalized = []
    seen = set()
    for raw in raw_urls:
        url = raw.strip().strip('<>()[]"\'')
        if url.lower().startswith("www."):
            url = "https://" + url
        url = url.rstrip(".,;:!?)")
        if not re.match(r"^https?://", url, re.IGNORECASE):
            continue
        if url not in seen:
            seen.add(url)
            normalized.append(url)
    return normalized


async def _post_message_with_attachments_or_links(token, channel_id, content=None, file_urls=None, is_bot=False):
    if not file_urls:
        return await _post_message(token, channel_id, content, is_bot=is_bot)

    status, reason = await _post_message_with_files(token, channel_id, content, file_urls=file_urls, is_bot=is_bot)
    if status in (400, 403):
        fallback_content = (content or "").strip()
        if file_urls:
            url_lines = []
            for url in file_urls:
                if len(url_lines) >= 5:
                    break
                url_lines.append(url)
            url_text = "\n".join(url_lines)
            if fallback_content:
                fallback_content = f"{fallback_content}\n\n{url_text}"
            else:
                fallback_content = url_text
            if len(fallback_content) > 2000:
                fallback_content = fallback_content[:1990].rstrip() + "\n...[image URLs trimmed]"
        return await _post_message(token, channel_id, fallback_content, is_bot=is_bot)
    return status, reason

def build_message_embeds(image_urls):
    embeds = []
    for url in image_urls[:10]:
        embeds.append({
            "image": {"url": url}
        })
    return embeds

async def send_adv_log_dm(uid, message, image_urls=None):
    try:
        user = bot.get_user(int(uid))
        if user is None:
            user = await bot.fetch_user(int(uid))
        if user:
            message = message[:4096]
            embed = discord.Embed(color=discord.Color.blue(), description=message)
            await user.send(embed=embed)
            
            # Send image URLs as separate messages
            if image_urls:
                for url in image_urls:
                    try:
                        await user.send(url)
                    except Exception as e:
                        print(f"[AdvLog:{uid}] Failed to send image URL: {e}")
    except Exception as e:
        print(f"[AdvLog:{uid}] Failed to send DM: {e}")

async def stop_adv_after_duration(uid, acc_id, duration_secs):
    await asyncio.sleep(duration_secs)
    key = skey(uid, acc_id)
    state = adv_sessions.get(key)
    if state and state["running"]:
        state["running"] = False
        adv_sessions[key] = state
        await send_adv_log_dm(uid, f"⏰ **Scheduled Auto Adv Stopped**\n\nAccount: {acc_id}\nDuration: {duration_secs}s elapsed")

async def notify_adv_license_expired(uid, lic):
    """Send DM to user when their Auto Adv license expires."""
    try:
        user = bot.get_user(int(uid))
        if user is None:
            user = await bot.fetch_user(int(uid))
        if user:
            embed = discord.Embed(
                color=discord.Color.red(),
                title="⏰ Auto Adv License Expired",
                description=f"> Your Auto Adv license has expired and all accounts have been stopped.\n\n> **Expired:** {format_expiry(lic.get('expiresAt'))}\n\n> To continue using Auto Adv, redeem a new key with `/autoadv`."
            )
            embed.add_field(name="📊 Your License Info", value=f"> • Key: `{lic.get('keyCode', '?')}`\n> • Slots: **{lic.get('slots', '?')}**", inline=False)
            await user.send(embed=embed)
    except Exception as e:
        print(f"[NotifyExpiry:{uid}] Error sending expiry DM: {e}")

# ─── Webhook and member join functions ────────────────────────────────────────

def get_mem_tokens(mode):
    """Get tokens for member join based on mode (online/offline)."""
    if mode == "online":
        return [t for t in read_lines(ONTOKENS_FILE) if is_valid_token_string(t)]
    elif mode == "offline":
        return [t for t in read_lines(OFFTOKENS_FILE) if is_valid_token_string(t)]
    return []

def get_booster_tokens():
    """Get tokens for boost sessions from boosters.txt."""
    return [t for t in read_lines(BOOSTERS_FILE) if is_valid_token_string(t)]

async def get_available_boosts(token):
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as http:
            async with http.get("https://discord.com/api/v9/users/@me/guilds/premium/subscription-slots", headers=_token_headers(token)) as res:
                if res.status != 200:
                    return 0
                data = await res.json()
                available = sum(1 for slot in data if not slot.get("premium_guild_subscription"))
                return available
    except Exception:
        return 0

async def get_subscription_slots(token):
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as http:
            async with http.get("https://discord.com/api/v9/users/@me/guilds/premium/subscription-slots", headers=_token_headers(token)) as res:
                if res.status == 200:
                    return await res.json()
                return []
    except Exception:
        return []

async def boost_server(token, guild_id, slot_id):
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as http:
            async with http.put(
                f"https://discord.com/api/v9/guilds/{guild_id}/premium/subscriptions",
                headers=_token_headers(token),
                json={"user_premium_guild_subscription_slot_ids": [slot_id]}
            ) as res:
                body = await res.text()
                success = res.status in (200, 201)
                return {"success": success, "status": res.status, "body": body}
    except Exception as e:
        return {"success": False, "status": None, "error": str(e)}

async def get_booster_token_status(token):
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as http:
            async with http.get("https://discord.com/api/v9/users/@me", headers=_token_headers(token)) as res:
                if res.status != 200:
                    return {"token": token, "valid": False, "error": f"HTTP {res.status}"}
                data = await res.json()
                premium_type = data.get("premium_type", 0)
                username = data.get("username", "Unknown")
                discriminator = data.get("discriminator")
                if discriminator:
                    username = f"{username}#{discriminator}"
                available_boosts = await get_available_boosts(token) if premium_type > 0 else 0
                if premium_type == 2:
                    nitro_label = "Nitro"
                elif premium_type == 1:
                    nitro_label = "Nitro Classic"
                else:
                    nitro_label = "No Nitro"
                return {"token": token, "valid": True, "username": username, "premium_type": premium_type, "available_boosts": available_boosts, "nitro_label": nitro_label}
    except Exception as e:
        return {"token": token, "valid": False, "error": str(e)}

async def run_boost(interaction, uid, key, invite_input):
    invite_code = extract_invite_code(invite_input)
    if not invite_code:
        return await safe_send_message(
            interaction,
            embed=discord.Embed(color=discord.Color.red(), description="> ❌ Invalid invite link or code."), ephemeral=True)

    keys = load_keys()
    lookup_key, _ = find_key_entry(keys, key)
    if not lookup_key:
        return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> ❌ Invalid key."), ephemeral=True)
    key = lookup_key
    if keys[key]["used"]:
        return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> ❌ This key has already been redeemed."), ephemeral=True)
    if is_key_expired(keys[key]):
        return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description=f"> ❌ This key expired {format_expiry(keys[key].get('expiresAt'))}."), ephemeral=True)
    if keys[key].get("keyType") != "boost":
        kt = keys[key].get("keyType", "unknown")
        return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description=f"> ❌ This is a **{kt}** key. Use `/{kt}` to redeem it."), ephemeral=True)

    boost_count = int(keys[key].get("boostCount", 0) or 0)
    if boost_count < 1:
        return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> ❌ Invalid boost key configuration."), ephemeral=True)

    invite_guild_id = await resolve_invite_to_guild(invite_code)
    if not invite_guild_id:
        return await safe_send_message(
            interaction,
            embed=discord.Embed(color=discord.Color.red(), description="> ❌ Could not resolve the invite. Make sure it's valid and not expired."), ephemeral=True)

    booster_tokens = get_booster_tokens()
    if len(booster_tokens) < boost_count:
        return await safe_send_message(
            interaction,
            embed=discord.Embed(color=discord.Color.red(), description=f"> ❌ Not enough booster tokens in boosters.txt. Need **{boost_count}**, found **{len(booster_tokens)}**."), ephemeral=True)

    # Get tokens with available boosts
    available_tokens = []
    for token in booster_tokens:
        info = await get_booster_token_status(token)
        if info["valid"] and info["available_boosts"] > 0:
            available_tokens.append((token, info["available_boosts"], info["username"]))

    if len(available_tokens) < boost_count:
        # Reset key
        keys[key]["used"] = False
        keys[key].pop("redeemedBy", None)
        keys[key].pop("redeemedAt", None)
        save_keys(keys)
        return await safe_send_message(
            interaction,
            embed=discord.Embed(color=discord.Color.red(), description=f"> ❌ Not enough tokens with available boosts. Need **{boost_count}**, found **{len(available_tokens)}**. Key reset."), ephemeral=True)

    selected_tokens = available_tokens[:boost_count]

    keys[key]["used"] = True
    keys[key]["redeemedBy"] = uid
    keys[key]["redeemedAt"] = datetime.now(timezone.utc).isoformat()
    save_keys(keys)

    await safe_send_message(
        interaction,
        embed=discord.Embed(color=discord.Color.yellow(), title="🔑 Boost Key Redeemed!",
                            description=(f"> **Phase 1/2:** Joining **{boost_count}** booster tokens to the server...\n> Invite: `discord.gg/{invite_code}`")),
        ephemeral=True)

    joined_tokens = []
    for i, (token, boosts, username) in enumerate(selected_tokens):
        r = await join_server_with_token(token, invite_guild_id)
        if r["success"]:
            joined_tokens.append((token, username))

        status_str = (
            "✅ joined" if r["success"] and not r.get("alreadyIn") else
            "↩️ already in server" if r.get("alreadyIn") else
            f"❌ {r.get('reason', 'failed')}"
        )

        await safe_edit_message(
            interaction,
            embed=discord.Embed(
                color=discord.Color.yellow(),
                description=(
                    f"> **Phase 1/2:** Joining booster tokens...\n> **{len(joined_tokens)}/{boost_count}** joined\n> Last: **{username}** — {status_str}"
                )
            )
        )

        if i < boost_count - 1:
            await asyncio.sleep(1.5)

    # Wait for joins to propagate
    await asyncio.sleep(5)

    await safe_edit_message(
        interaction,
        embed=discord.Embed(
            color=discord.Color.yellow(),
            description=(
                f"> **Phase 2/2:** Boosting the server with **{len(joined_tokens)}** tokens...\n> Invite: `discord.gg/{invite_code}`"
            )
        )
    )

    boosted_count = 0
    for token, username in joined_tokens:
        slots = await get_subscription_slots(token)
        available_slots = [slot for slot in slots if not slot.get("premium_guild_subscription")]
        success = False
        result = {"status": None, "body": None, "error": None}
        if available_slots:
            slot_id = available_slots[0]["id"]
            result = await boost_server(token, invite_guild_id, slot_id)
            success = result["success"]
            if success:
                boosted_count += 1

        if not available_slots:
            status_str = "❌ no available slots"
        elif success:
            status_str = "🚀 boosted"
        else:
            details = result.get("body") or result.get("error") or "unknown error"
            status_str = f"❌ failed ({result.get('status', 'error')}) {details[:120]}"

        await safe_edit_message(
            interaction,
            embed=discord.Embed(
                color=discord.Color.green() if boosted_count == len(joined_tokens) else discord.Color.yellow(),
                description=(
                    f"> **Phase 2/2:** Boosting server...\n> **{boosted_count}/{len(joined_tokens)}** boosted\n> Last: **{username}** — {status_str}"
                )
            )
        )

        await asyncio.sleep(1.5)

    final_embed = discord.Embed(color=discord.Color.green(), title="✅ Boost Complete!",
                                description=(f"> **{len(joined_tokens)}** tokens joined, **{boosted_count}** boosts applied to the server.\n> Invite: `discord.gg/{invite_code}`"))

    await safe_edit_message(interaction, embed=final_embed)

async def find_boost_key_for_user(uid):
    keys = load_keys()
    available = [code for code, data in keys.items()
                 if data.get("keyType") == "boost" and not data.get("used") and not is_key_expired(data) and data.get("createdBy") == uid]
    if len(available) == 1:
        return available[0]
    return None

async def find_or_require_boost_key(interaction, uid, key):
    if key:
        return key.strip().upper()
    available = await find_boost_key_for_user(uid)
    if available:
        return available
    await safe_send_message(
        interaction,
        embed=discord.Embed(color=discord.Color.red(), description="> ❌ You must provide a valid boost key"),
        ephemeral=True)
    return None

async def handle_boost_check(interaction):
    tokens = get_booster_tokens()
    total_tokens = len(tokens)
    if total_tokens == 0:
        return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> ❌ No tokens found in boosters.txt."), ephemeral=True)

    status_results = []
    total_potential = 0
    for token in tokens:
        info = await get_booster_token_status(token)
        if info["valid"]:
            total_potential += info["available_boosts"]
        status_results.append(info)

    valid_tokens = [item for item in status_results if item["valid"]]
    invalid_tokens = [item for item in status_results if not item["valid"]]

    description = (f"> **Total booster tokens:** {total_tokens}\n"
                   f"> **Valid boosters:** {len(valid_tokens)}\n"
                   f"> **Invalid boosters:** {len(invalid_tokens)}\n"
                   f"> **Total available boosts:** **{total_potential}**\n\n"
                   "> Each valid Nitro token shows actual available boosts.")

    # Remove invalid tokens from boosters.txt
    if invalid_tokens:
        invalid_token_strings = [info['token'] for info in invalid_tokens]
        all_booster_tokens = get_booster_tokens()
        valid_booster_tokens = [t for t in all_booster_tokens if t not in invalid_token_strings]
        BOOSTERS_FILE.write_text("\n".join(valid_booster_tokens) + ("\n" if valid_booster_tokens else ""), encoding="utf-8")
        description += f"\n\n> **Cleaned boosters.txt**: Removed **{len(invalid_tokens)}** invalid tokens."

    embed = discord.Embed(color=discord.Color.blue(), title="📊 Booster Token Check", description=description)
    lines = []
    for info in valid_tokens[:15]:
        lines.append(f"• **{info['username']}** — {info['available_boosts']} boost(s) available ({info['nitro_label']})")
    for info in invalid_tokens[:5]:
        lines.append(f"• Invalid token — {info.get('error','unknown error')}")

    if lines:
        embed.add_field(name="Sample token status", value="\n".join(lines), inline=False)
    if len(valid_tokens) > 15 or len(invalid_tokens) > 5:
        embed.set_footer(text="Showing first 15 valid and first 5 invalid entries.")

    await safe_send_message(interaction, embed=embed, ephemeral=True)

async def handle_sell_auth_webhook(data):
    """Handle payment webhook from sell.auth"""
    try:
        buyer_id = data.get("buyer_id")
        if not buyer_id:
            print("[Webhook] Missing buyer_id")
            return {"status": "error", "message": "Missing buyer_id"}

        amount = data.get("amount", 0)
        if amount <= 0:
            print(f"[Webhook] Invalid amount: {amount}")
            return {"status": "error", "message": "Invalid amount"}

        # Update balance
        current_balance = get_balance(buyer_id) or 0
        if current_balance == "infinite":
            new_balance = "infinite"
        else:
            new_balance = current_balance + amount

        set_balance(buyer_id, new_balance)

        # Log the transaction
        print(f"[Webhook] Added ${amount} to {buyer_id}. New balance: {format_balance(new_balance)}")

        return {"status": "success", "new_balance": new_balance}
    except Exception as e:
        print(f"[Webhook] Error processing payment: {e}")
        return {"status": "error", "message": str(e)}

async def send_webhook_notification(event_type, data):
    """Send notification to configured webhook URL"""
    if not WEBHOOK_URL:
        return

    try:
        payload = {
            "event": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(WEBHOOK_URL, json=payload) as response:
                if response.status not in (200, 201, 202):
                    print(f"[Webhook] Notification failed: {response.status}")
                else:
                    print(f"[Webhook] Notification sent for {event_type}")
    except Exception as e:
        print(f"[Webhook] Error sending notification: {e}")

def generate_order_content(key_type, order_data):
    """Generate order content for buyers"""
    buyer_id = order_data.get("buyer_id", "Unknown")
    key_id = order_data.get("key_id", "Unknown")

    if key_type == "mem-online" or key_type == "mem-offline":
        token_count = order_data.get("token_count", 0)
        mode = order_data.get("mode", "online")
        return f"""🎯 **Member Join Order - {mode.title()} Tokens**

**Order Details:**
• Buyer ID: {buyer_id}
• Key ID: {key_id}
• Token Count: {token_count}
• Mode: {mode.title()}

**Instructions:**
1. Use `/redeem {key_id}` command
2. Provide a valid Discord server invite link/code
3. {token_count} {mode} tokens will join your server
4. Process completes automatically

**Note:** Make sure the invite link is valid and not expired."""

    elif key_type in ["vouch", "chat", "trade", "vc"]:
        return f"""🎯 **{key_type.title()} Session Order**

**Order Details:**
• Buyer ID: {buyer_id}
• Key ID: {key_id}
• Session Type: {key_type.title()}

**Instructions:**
1. Use `/{key_type}` command
2. Fill in the required information (server invite, channel ID, etc.)
3. Tokens will join your server and begin the {key_type} session
4. Use `/manage` to control the session

**Note:** Sessions run indefinitely until stopped."""

    elif key_type == "autoadv":
        slots = order_data.get("slots", 1)
        return f"""🚀 **Auto Advertising Order**

**Order Details:**
• Buyer ID: {buyer_id}
• Key ID: {key_id}
• Account Slots: {slots}

**Instructions:**
1. Use `/autoadv` command
2. Redeem the key: {key_id}
3. Add up to {slots} Discord accounts
4. Configure advertising channels and messages
5. Start advertising automatically

**Note:** Use `/advpanel` to manage your accounts."""

    return f"""🎯 **Bot Service Order**

**Order Details:**
• Buyer ID: {buyer_id}
• Key ID: {key_id}
• Service Type: {key_type}

Please contact support for redemption instructions."""

# The webhook server implementation is defined later in this file.

def generate_join_progress_html(session_id):
    if not session_id or session_id not in join_sessions:
        return None

    session_data = join_sessions[session_id]

    # Generate HTML page
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Join Progress - Session {session_id[:8]}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #121212;
            margin: 0;
            padding: 20px;
            color: #ffffff;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: #1e1e1e;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .progress-bar {{
            width: 100%;
            height: 30px;
            background: #333333;
            border-radius: 15px;
            overflow: hidden;
            margin: 20px 0;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #4CAF50, #45a049);
            transition: width 0.3s ease;
        }}
        .stats {{
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
            text-align: center;
        }}
        .stat {{
            background: #2a2a2a;
            padding: 15px;
            border-radius: 8px;
            flex: 1;
            margin: 0 5px;
        }}
        .logs {{
            background: #0d0d0d;
            border-radius: 8px;
            padding: 15px;
            max-height: 400px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 14px;
        }}
        .log-entry {{
            margin: 5px 0;
            padding: 5px;
            border-radius: 4px;
        }}
        .success {{ background: rgba(76, 175, 80, 0.2); color: #81c784; }}
        .error {{ background: rgba(244, 67, 54, 0.2); color: #ef5350; }}
        .warning {{ background: rgba(255, 193, 7, 0.2); color: #ffb74d; }}
        .refresh {{
            display: block;
            margin: 20px auto;
            padding: 10px 20px;
            background: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
            text-align: center;
        }}
        .refresh:hover {{
            background: #45a049;
        }}
        .footer {{
            text-align: center;
            margin-top: 20px;
            color: #888;
            font-size: 14px;
        }}
        @media (max-width: 600px) {{
            .container {{
                padding: 15px;
            }}
            .stats {{
                flex-direction: column;
            }}
            .stat {{
                margin: 5px 0;
            }}
            .logs {{
                font-size: 12px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔑 Member Join Progress</h1>
            <p>Session: {session_id[:8]} | Mode: {session_data['mode'].title()} | Tokens: {session_data['token_count']}</p>
            <p>Started: {session_data['start_time'][:19].replace('T', ' ')} UTC</p>
        </div>

        <div class="stats">
            <div class="stat">
                <h3>{session_data['joined_count']}</h3>
                <p>Joined</p>
            </div>
            <div class="stat">
                <h3>{session_data['token_count']}</h3>
                <p>Total</p>
            </div>
            <div class="stat">
                <h3>{session_data['token_count'] - session_data['joined_count']}</h3>
                <p>Remaining</p>
            </div>
            <div class="stat">
                <h3>{'✅ Complete' if session_data['status'] == 'completed' else '🔄 In Progress'}</h3>
                <p>Status</p>
            </div>
        </div>

        <div class="progress-bar">
            <div class="progress-fill" style="width: {min(100, (session_data['joined_count'] / max(1, session_data['token_count'])) * 100)}%"></div>
        </div>

        <h2>Final Join Logs</h2>
        <div class="logs">
"""

    # Add log entries
    for log in session_data.get('logs', []):
        css_class = "success" if "✅" in log else "error" if "❌" in log else "warning"
        html_content += f'            <div class="log-entry {css_class}">{log}</div>\n'

    html_content += """
        </div>

        <div class="footer">
            <p>📊 Final Report - Session Complete</p>
        </div>
    </div>
</body>
</html>
"""

    return html_content

async def start_webhook_server():
    """Start the aiohttp webhook server"""
    from aiohttp import web

    async def webhook_handler(request):
        try:
            data = await request.json()
            print(f"[Webhook] Received: {data}")

            # Handle different webhook types
            if request.match_info.get('type') == 'sell_auth':
                result = await handle_sell_auth_webhook(data)
                return web.json_response(result)

            return web.json_response({"status": "unknown_webhook_type"})

        except Exception as e:
            print(f"[Webhook] Error: {e}")
            return web.json_response({"status": "error", "message": str(e)}, status=500)

    async def join_progress_handler(request):
        session_id = request.match_info.get('session_id')
        html_content = generate_join_progress_html(session_id)
        if html_content is None:
            return web.Response(text="<h1>Session Not Found</h1><p>The join session could not be found or has expired.</p>", content_type='text/html')

        return web.Response(text=html_content, content_type='text/html')

    async def join_progress_download_handler(request):
        session_id = request.match_info.get('session_id')
        html_content = generate_join_progress_html(session_id)
        if html_content is None:
            return web.Response(text="<h1>Session Not Found</h1><p>The join session could not be found or has expired.</p>", content_type='text/html')

        response = web.Response(text=html_content, content_type='text/html')
        response.headers['Content-Disposition'] = f'attachment; filename="join_progress_{session_id[:8]}.html"'
        return response

    app = web.Application()
    app.router.add_post('/webhook/{type}', webhook_handler)
    app.router.add_get('/join-progress/{session_id}', join_progress_handler)
    app.router.add_get('/join-progress/{session_id}/download', join_progress_download_handler)

    runner = web.AppRunner(app)
    await runner.setup()

    global ACTIVE_WEBHOOK_PORT
    bind_port = WEBHOOK_PORT
    site = None
    last_error = None
    for port in range(WEBHOOK_PORT, WEBHOOK_PORT + 10):
        try:
            site = web.TCPSite(runner, '0.0.0.0', port, reuse_address=True, reuse_port=False)
            await site.start()
            ACTIVE_WEBHOOK_PORT = port
            print(f"[Webhook] Server started on port {port}")
            break
        except OSError as e:
            last_error = e
            print(f"[Webhook] Port {port} unavailable: {e}")
            continue

    if site is None:
        print(f"[Webhook] Failed to bind server on ports {WEBHOOK_PORT}-{WEBHOOK_PORT + 9}")
        raise last_error

    # Start session cleanup task
    async def cleanup_old_sessions():
        while True:
            try:
                current_time = datetime.now(timezone.utc)
                to_remove = []
                for session_id, session_data in join_sessions.items():
                    start_time = datetime.fromisoformat(session_data["start_time"])
                    # Remove sessions older than 24 hours
                    if (current_time - start_time).total_seconds() > 86400:
                        to_remove.append(session_id)

                for session_id in to_remove:
                    del join_sessions[session_id]
                    print(f"[Session Cleanup] Removed old session {session_id[:8]}")

            except Exception as e:
                print(f"[Session Cleanup] Error: {e}")

            await asyncio.sleep(3600)  # Clean up every hour

    asyncio.create_task(cleanup_old_sessions())

    # Keep the server running
    try:
        while True:
            await asyncio.sleep(3600)  # Sleep for an hour
    except asyncio.CancelledError:
        await runner.cleanup()

# ─── Vouch loop ───────────────────────────────────────────────────────────────

async def vouch_loop(uid):
    session = sessions.get(skey(uid, "vouch"))
    if not session or not session["running"]: return
    reasons = session.get("messagePool") or get_reasons()
    token   = session["tokens"][session["tokenIndex"] % len(session["tokens"])]
    session["tokenIndex"] += 1
    reason  = random.choice(reasons) if reasons else "great seller, very trustworthy"
    content = f"{random.choice(['vouch','rep','+rep'])} <@{session['targetUserId']}> {reason}"
    try:
        status, _ = await _post_message(token, session["channelId"], content)
        if status == 200: session["totalSent"] += 1
    except Exception as e:
        print(f"[Vouch:{uid}] {e}")
    if not session["running"]: return
    await asyncio.sleep(session["delayMs"] / 1000)
    asyncio.create_task(vouch_loop(uid))

# ─── Chat / Trade loop ────────────────────────────────────────────────────────

async def text_loop(uid, stype):
    session = sessions.get(skey(uid, stype))
    if not session or not session["running"]: return
    pool  = session.get("messagePool") or (get_trading() if stype == "trade" else get_messages())
    strict_pool = True if session.get("messagePool") else False
    token = session["tokens"][session["tokenIndex"] % len(session["tokens"])]
    session["tokenIndex"] += 1

    reply_target = None
    extra = None
    if stype == "chat" and random.random() < 0.60:
        recent_messages = await fetch_channel_messages(token, session["channelId"], limit=25)
        reply_target = await choose_reply_target(session, token, recent_messages)

    if stype == "chat":
        if reply_target:
            # If a custom message file was provided, always use it for replies too
            if strict_pool and pool:
                msg = random.choice(pool)
            else:
                msg = build_reply_message(pool, reply_target)
            extra = {"message_reference": {"message_id": reply_target["id"], "channel_id": session["channelId"], "fail_if_not_exists": False}}
        else:
            if strict_pool and pool:
                msg = random.choice(pool)
            else:
                msg = make_chat_message(session, pool)
        session["lastMessage"] = msg
    else:
        msg = random.choice(pool) if pool else "hey"

    try:
        status, _ = await _post_message(token, session["channelId"], msg, extra=extra)
        if status == 200:
            session["totalSent"] += 1
    except Exception as e:
        print(f"[{stype.title()}:{uid}] {e}")
    if not session["running"]: return
    await asyncio.sleep(session["delayMs"] / 1000)
    asyncio.create_task(text_loop(uid, stype))

# ─── Voice / VC loop ─────────────────────────────────────────────────────────

# ─── NEW VC System ───────────────────────────────────────────────────────────
# Better architected: per-token state, intelligent reconnection, duration support

async def verify_token_in_guild(token, guild_id):
    """
    Verify that a token is a member of the guild.
    Returns: (is_member: bool, user_id: str or None)
    """
    try:
        url = f"https://discord.com/api/v10/users/@me/guilds/{guild_id}/member"
        headers = _token_headers(token).copy()
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as http:
            async with http.get(url, headers=headers) as res:
                if res.status == 200:
                    data = await res.json()
                    return True, str(data.get("user", {}).get("id"))
                return False, None
    except:
        return False, None


class VcTokenState:
    """Track state of a single token in a VC session."""
    def __init__(self, token):
        self.token = token
        self.connected = False
        self.failed_attempts = 0
        self.last_attempt = None
        self.connected_at = None
        self.error_message = None
        self.in_guild = None  # Track if we've verified guild membership
    
    def mark_success(self):
        self.connected = True
        self.failed_attempts = 0
        self.connected_at = datetime.now(timezone.utc)
        self.error_message = None
    
    def mark_failure(self, error):
        self.connected = False
        self.failed_attempts += 1
        self.last_attempt = datetime.now(timezone.utc)
        self.error_message = str(error)[:100]
    
    def should_retry(self, max_retries=5):
        """Check if token should retry (exponential backoff)."""
        if self.failed_attempts >= max_retries:
            return False
        if not self.last_attempt:
            return True
        # Exponential backoff: 5s, 10s, 20s, 40s, 80s
        backoff = 5 * (2 ** (self.failed_attempts - 1))
        elapsed = (datetime.now(timezone.utc) - self.last_attempt).total_seconds()
        return elapsed >= backoff

async def vc_session_handler(uid, session_key):
    """
    Intelligent VC session handler with per-token tracking,
    reconnection logic, and duration support.
    """
    session = sessions.get(session_key)
    if not session or not session.get("running"):
        return
    
    guild_id = session.get("guildId")
    channel_id = session.get("channelId")
    tokens = session.get("tokens", [])
    delay_seconds = session.get("delayMs", 30000) / 1000
    start_time = session.get("startTime")
    duration_seconds = session.get("durationSeconds", 3600)  # Default 1 hour
    max_retries = session.get("maxRetries", 5)
    
    if not guild_id or not channel_id or not tokens:
        session["running"] = False
        return
    
    # Initialize token states if not present
    if "tokenStates" not in session:
        session["tokenStates"] = {t: VcTokenState(t) for t in tokens}
        session["iterationCount"] = 0
    
    session["iterationCount"] = session.get("iterationCount", 0) + 1
    iteration = session["iterationCount"]
    
    # Check if duration exceeded
    if start_time:
        elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
        if elapsed > duration_seconds and duration_seconds > 0:  # 0 = infinite
            session["running"] = False
            session["status"] = "completed"
            persist_running_state()
            print(f"[VC:{uid}] Session ended - duration limit reached ({elapsed:.0f}s)")
            # Disconnect all voice connections
            await disconnect_voice_connections(uid)
            return
    
    token_states = session["tokenStates"]
    successful_joins = 0
    
    print(f"[VC:{uid}] Iteration #{iteration} starting - checking {len(tokens)} tokens")
    
    # Check existing connections
    existing_connections = ACTIVE_VOICE_CONNECTIONS.get(uid, {})
    connected_tokens = set(existing_connections.keys())
    
    # Process each token
    for i, token in enumerate(tokens):
        state = token_states[token]
        
        # Skip if already connected
        if token in connected_tokens:
            print(f"[VC:{uid}] Token {i+1}/{len(tokens)} already connected - skipping")
            continue
        
        # Skip if max retries exceeded
        if state.failed_attempts >= max_retries and not state.connected:
            if iteration == 1:  # Only log once
                print(f"[VC:{uid}] Token {i+1}/{len(tokens)} already maxed retries")
            continue
        
        # Check if should retry
        if not state.should_retry(max_retries):
            continue
        
        # First iteration: verify token is in guild
        if state.in_guild is None and iteration == 1:
            in_guild, user_id = await verify_token_in_guild(token, guild_id)
            state.in_guild = in_guild
            if not in_guild:
                print(f"[VC:{uid}] Token {i+1}/{len(tokens)} is NOT in guild - waiting for OAuth2...")
                state.mark_failure("Token not yet in guild (OAuth2 pending)")
                continue
            else:
                print(f"[VC:{uid}] Token {i+1}/{len(tokens)} verified in guild as {user_id}")
        
        if state.in_guild == False:
            # Token was never added to guild, skip
            continue
        
        # Attempt connection
        try:
            result = await join_voice_channel_with_token(token, guild_id, channel_id)
            if result["success"]:
                state.mark_success()
                successful_joins += 1
                
                # Store connection in global dict
                connection_info = {
                    "voice_ws": result.get("voice_ws"),
                    "gateway_ws": result.get("gateway_ws"),
                    "heartbeat_task": result.get("heartbeat_task"),
                    "voice_heartbeat_task": result.get("voice_heartbeat_task"),
                    "guild_id": guild_id,
                    "channel_id": channel_id,
                    "joined_at": datetime.now(timezone.utc).isoformat()
                }
                
                if uid not in ACTIVE_VOICE_CONNECTIONS:
                    ACTIVE_VOICE_CONNECTIONS[uid] = {}
                ACTIVE_VOICE_CONNECTIONS[uid][token] = connection_info
                
                print(f"[VC:{uid}] [OK] Token {i+1}/{len(tokens)} joined voice")
            else:
                reason = result.get("reason", "Unknown error")
                state.mark_failure(reason)
                print(f"[VC:{uid}] [FAIL] Token {i+1}/{len(tokens)} failed: {reason}")
        except Exception as e:
            state.mark_failure(str(e))
            print(f"[VC:{uid}] [FAIL] Token {i+1}/{len(tokens)} exception: {str(e)[:80]}")
        
        # Small delay between token attempts to avoid rate limiting
        await asyncio.sleep(0.3)
    
    # Update session stats
    session["totalConnected"] = len(ACTIVE_VOICE_CONNECTIONS.get(uid, {}))
    session["totalAttempts"] = sum(s.failed_attempts for s in token_states.values()) + session["totalConnected"]
    
    print(f"[VC:{uid}] Iteration #{iteration} complete: {session['totalConnected']} connected, {successful_joins} new joins")
    
    # Stop if no tokens can connect
    if session["totalConnected"] == 0 and all(s.failed_attempts >= max_retries for s in token_states.values() if not s.connected):
        session["running"] = False
        session["status"] = "failed_all_tokens"
        persist_running_state()
        print(f"[VC:{uid}] Session ended - all tokens exhausted retries")
        return
    
    # Schedule next iteration
    if session["running"]:
        await asyncio.sleep(delay_seconds)
        asyncio.create_task(vc_session_handler(uid, session_key))

async def vc_loop(uid):
    """Maintained for backward compatibility - routes to new handler."""
    session_key = skey(uid, "vc")
    await vc_session_handler(uid, session_key)


async def react_loop(uid):
    session = sessions.get(skey(uid, "reacts"))
    if not session or not session["running"]:
        return
    tokens = session.get("tokens", [])
    channel_id = session.get("channelId")
    message_id = session.get("messageId")  # message_id stored in messageId for reacts
    emoji = session.get("emoji")
    total = len(tokens)
    reacted = 0
    for token in tokens:
        try:
            status, _ = await _react_to_message(token, channel_id, message_id, emoji)
            if status in (204, 200):
                session["totalSent"] = session.get("totalSent", 0) + 1
                reacted += 1
        except Exception as e:
            print(f"[React:{uid}] {e}")
        await asyncio.sleep(0.5)
    # After reacting, stop session
    stop_session(uid, "reacts")

# ─── Auto-Adv loops ───────────────────────────────────────────────────────────

async def adv_message_loop(uid, acc_id):
    key   = skey(uid, acc_id)
    state = adv_sessions.get(key)
    if not state or not state["running"]: return
    is_bot = state.get("is_bot", False)

    # Check if license has expired
    lic = get_adv_license(uid)
    if not lic or is_adv_license_expired(lic):
        state["running"] = False
        adv_sessions[key] = state
        persist_running_state()
        if lic:
            await notify_adv_license_expired(uid, lic)
            # Stop all accounts for this user
            stop_all_adv(uid)
            # Remove expired license
            licenses = load_adv_licenses()
            licenses.pop(uid, None)
            save_adv_licenses(licenses)
        return

    token         = state["token"]
    channels      = state["channels"]
    auto_msg      = state["autoMessage"]
    cycle_delay   = state["cycleDelaySecs"]
    image_urls    = state.get("imageUrls", []) or []

    if auto_msg or image_urls:
        # Cycle through all channels with 5s between each
        for channel in channels:
            if not state["running"]: return  # Check if still running
            content_to_send = (auto_msg or "")[:2000]
            try:
                if image_urls:
                    status, reason = await _post_message_with_attachments_or_links(token, channel, content_to_send, file_urls=image_urls, is_bot=is_bot)
                else:
                    status, reason = await _post_message(token, channel, content_to_send, is_bot=is_bot)
                if status == 200:
                    state["totalSent"] = state.get("totalSent", 0) + 1
                    # Clear pause reason on success
                    state.pop("paused_reason", None)
                    debug_lines = [
                        f"✅ **Message Sent Successfully!**",
                        f"",
                        f"📤 Sent to: <#{channel}>",
                        f"📊 Progress: {state['totalSent']} messages sent",
                        f"🔄 Cycling through {len(channels)} channels",
                        f"🖼️  {len(image_urls)} image(s)",
                    ]
                    msg_preview = (auto_msg[:50] + "...") if len(auto_msg) > 50 else auto_msg
                    if msg_preview:
                        debug_lines.insert(2, f"💬 Message: *{msg_preview}*")
                    await send_adv_log_dm(uid, "\n".join(debug_lines), image_urls=image_urls if image_urls else None)
                else:
                    # Critical error - pause account
                    if status in [401, 403]:
                        state["running"] = False
                        adv_sessions[key] = state
                        persist_running_state()
                        if status == 401:
                            state["paused_reason"] = "❌ Token Invalid — Use `/testtoken` to fix"
                        elif status == 403:
                            state["paused_reason"] = "❌ No Channel Permission — Check settings"
                    
                    error_msg = format_adv_error_message(status, reason, channel, channels, len(image_urls), acc_id)
                    await send_adv_log_dm(uid, error_msg)
            except Exception as e:
                await send_adv_log_dm(
                    uid,
                    f"❌ **Unexpected Error** — Channel <#{channel}>\n"
                    f"\n"
                    f"Something unexpected happened:\n"
                    f"  • {str(e)[:100]}\n"
                    f"\n"
                    f"Try restarting the Auto Adv for this account."
                )
            # Wait 5 seconds between channels
            await asyncio.sleep(5)

        # After full cycle, send completion log
        await send_adv_log_dm(
            uid,
            f"🔄 **Channel Rotation Complete**\n"
            f"\n"
            f"Account: {acc_id}\n"
            f"Messages sent this round: {len(channels)}\n"
            f"Channels: {', '.join(f'<#{ch}>' for ch in channels)}"
        )

    if not state["running"]: return
    # Wait cycle delay before next full cycle
    await asyncio.sleep(cycle_delay)
    asyncio.create_task(adv_message_loop(uid, acc_id))


async def adv_dm_loop(uid, acc_id):
    key   = skey(uid, acc_id)
    state = adv_sessions.get(key)
    if not state or not state["running"] or not state.get("dmResponse"): return

    # Check if license has expired
    lic = get_adv_license(uid)
    if not lic or is_adv_license_expired(lic):
        state["running"] = False
        adv_sessions[key] = state
        persist_running_state()
        if lic:
            await notify_adv_license_expired(uid, lic)
            # Stop all accounts for this user
            stop_all_adv(uid)
            # Remove expired license
            licenses = load_adv_licenses()
            licenses.pop(uid, None)
            save_adv_licenses(licenses)
        return

    token      = state["token"]
    dm_resp    = state["dmResponse"]
    is_bot     = state.get("is_bot", False)
    replied    = adv_dm_replied.setdefault(key, set())
    BASE       = "https://discord.com/api/v9"

    async with aiohttp.ClientSession() as http:
        res = await http.get(f"{BASE}/users/@me/channels", headers=_msg_headers(token, is_bot))
        try:
            if not res.ok:
                if res.status == 401:
                    await send_adv_log_dm(uid, 
                        f"⚠️ **DM Auto-Reply Paused**\n\n"
                        f"Your token appears invalid. The message Auto Adv is also affected.\n"
                        f"Please check your account and token."
                    )
                    state["running"] = False
                    adv_sessions[key] = state
                    persist_running_state()
                await asyncio.sleep(30)
                if adv_sessions.get(key, {}).get("running"):
                    asyncio.create_task(adv_dm_loop(uid, acc_id))
                return
            dm_channels = await res.json()
        finally:
            res.close()

        dm_count = 0
        for ch in dm_channels:
            if ch.get("type") != 1: continue
            ch_id = ch["id"]
            res = await http.get(f"{BASE}/channels/{ch_id}/messages?limit=10",
                                headers=_msg_headers(token, is_bot))
            try:
                if not res.ok: continue
                msgs = await res.json()
            finally:
                res.close()
        for msg in msgs:
            author_id = msg.get("author", {}).get("id")
            if author_id == state.get("selfUserId"): continue
            if not msg.get("content", "").strip(): continue
            # Only reply once per user per session
            if author_id in replied: continue
            replied.add(author_id)
            dm_count += 1
            dm_resp = state["dmResponse"].strip()
            if not dm_resp: continue
            try:
                await asyncio.sleep(random.uniform(1, 3))
                _, _ = await _post_message(token, ch_id, dm_resp, is_bot=is_bot)
                state["dmReplied"] = state.get("dmReplied", 0) + 1
            except Exception as e:
                print(f"[Adv DM:{uid}:{acc_id}] reply error: {e}")
            
            if dm_count > 0:
                total_replied = state.get("dmReplied", 0)
                await send_adv_log_dm(uid,
                    f"💬 **DM Auto-Reply Stats**\n\n"
                    f"Replied to: {dm_count} new message(s)\n"
                    f"Total replied overall: {total_replied}"
                )

    await asyncio.sleep(5)
    if adv_sessions.get(key, {}).get("running"):
        asyncio.create_task(adv_dm_loop(uid, acc_id))


async def start_adv_account(uid, acc):
    acc_id = acc["id"]
    key    = skey(uid, acc_id)
    if adv_sessions.get(key, {}).get("running"): return

    # Validate token
    is_valid, msg, user_info, is_bot = await validate_adv_token(acc["token"])
    if not is_valid:
        await send_adv_log_dm(uid, f"❌ **Auto Adv Start Failed**\n\nAccount: {acc_id}\nReason: {msg}")
        return

    self_user_id = user_info.get("id")
    adv_sessions[key] = {
        "running":    True,
        "token":      acc["token"],
        "channels":   acc["channels"],
        "autoMessage": acc.get("autoMessage", ""),
        "imageUrls":  acc.get("imageUrls", []),
        "dmResponse": acc.get("dmResponse", ""),
        "cycleDelaySecs":  acc.get("delaySecs", 60),
        "selfUserId": self_user_id,
        "is_bot":     is_bot,
        "totalSent":  0,
        "dmReplied":  0,
    }
    persist_running_state()
    await ensure_presence_gateway(acc["token"])
    asyncio.create_task(adv_message_loop(uid, acc_id))
    if acc.get("dmResponse"):
        asyncio.create_task(adv_dm_loop(uid, acc_id))


def stop_adv_account(uid, acc_id):
    key = skey(uid, acc_id)
    s   = adv_sessions.get(key)
    if s:
        token = s.get("token")
        task = s.get("schedule_task")
        if task and not task.done():
            task.cancel()
        s["running"] = False
        adv_sessions.pop(key, None)
        persist_running_state()
        if token:
            try:
                asyncio.create_task(release_presence_gateway(token))
            except Exception:
                pass


def stop_all_adv(uid):
    lic = get_adv_license(uid)
    if not lic: return
    for acc in lic.get("accounts", []):
        stop_adv_account(uid, acc["id"])

# ─── Adv panel builder ────────────────────────────────────────────────────────

def build_adv_panel(uid):
    lic = get_adv_license(uid)
    if not lic:
        embed = discord.Embed(color=discord.Color.red(),
                              description="> ❌ You have no active Auto Adv license. Redeem one with `/autoadv`.")
        return embed, None

    accounts     = lic.get("accounts", [])
    slots        = lic.get("slots", 1)
    allow_dm     = lic.get("allowDmReply", False)
    running_accs = [a for a in accounts if adv_sessions.get(skey(uid, a["id"]), {}).get("running")]

    embed = discord.Embed(color=discord.Color.blurple(), title="📢 Auto Adv Panel")
    embed.add_field(name="Accounts",    value=f"{len(accounts)}/{slots}",           inline=True)
    embed.add_field(name="Running",     value=str(len(running_accs)),               inline=True)
    embed.add_field(name="DM Reply",    value="✅ Enabled" if allow_dm else "❌ Off", inline=True)
    embed.add_field(name="Key Expires", value=format_expiry(lic.get("expiresAt")),  inline=True)

    if accounts:
        lines = []
        for acc in accounts:
            state   = adv_sessions.get(skey(uid, acc["id"]), {})
            running = state.get("running", False)
            sent    = state.get("totalSent", 0)
            dms     = state.get("dmReplied", 0)
            icon    = "🟢" if running else "🔴"
            ch_cnt  = len(acc.get("channels", []))
            
            # Show pause status if there was a token error
            paused_reason = state.get("paused_reason", "")
            schedule_end = state.get("schedule_end_time")
            schedule_note = ""
            if schedule_end:
                try:
                    end_dt = datetime.fromisoformat(schedule_end)
                    if end_dt.tzinfo is None:
                        end_dt = end_dt.replace(tzinfo=timezone.utc)
                    schedule_note = f" | scheduled until <t:{int(end_dt.timestamp())}:R>"
                except Exception:
                    pass

            if paused_reason:
                lines.append(f"{icon} **{acc.get('name','Account')}** ⚠️\n   └─ {paused_reason}")
            else:
                lines.append(f"{icon} **{acc.get('name','Account')}** — {ch_cnt} ch | {sent} sent | {dms} DMs{schedule_note}")
        
        embed.add_field(name="Account Status", value="\n".join(lines), inline=False)
    
    embed.add_field(
        name="💡 Token Problem?",
        value="If an account shows ❌ or ⚠️, test your token with:\n`/testtoken <your_token>`",
        inline=False
    )

    view = AdvPanelView(uid, lic)
    return embed, view

# ─── Manage panel (Vouch/Chat/Trade) ─────────────────────────────────────────

def build_manage_embed_and_view(uid, stype):
    session = sessions.get(skey(uid, stype))
    icon    = TYPE_ICONS[stype]; label = TYPE_LABELS[stype]
    
    # If no session in memory, check if there's an active redemption in JSON
    if not session:
        active_redemption = get_active_redemption(uid, stype)
        if active_redemption:
            key = active_redemption if isinstance(active_redemption, str) else active_redemption.get("key")
            token_count = get_meta_value(active_redemption, "tokenCount", "token_count")
            channel_id = get_meta_value(active_redemption, "channelId", "channel_id", "channel")
            delay_ms = get_meta_value(active_redemption, "delayMs")
            if delay_ms is None:
                delay_seconds = get_meta_value(active_redemption, "delaySeconds", "delay_seconds", "delay")
                if delay_seconds is not None:
                    try:
                        delay_ms = int(float(delay_seconds) * 1000)
                    except Exception:
                        delay_ms = None
            else:
                try:
                    delay_ms = int(delay_ms)
                except Exception:
                    delay_ms = None
            target_user = get_meta_value(active_redemption, "targetUserId", "target_user_id")
            expires_at = get_meta_value(active_redemption, "expiresAt", "expires_at")

            description = (
                f"> You have an active **{label}** redemption, but the session isn't loaded in memory.\n> This can happen after bot restarts."
            )
            embed = discord.Embed(color=discord.Color.yellow(), title=f"⚠️ {icon} {label} - Inactive Session", description=description)
            embed.add_field(name="Active Key", value=f"`{key}`", inline=False)
            if token_count is not None:
                embed.add_field(name="Token Count", value=str(token_count), inline=True)
            if channel_id:
                embed.add_field(name="Channel", value=f"<#{channel_id}>", inline=True)
            if delay_ms is not None:
                embed.add_field(name="Delay", value=f"{delay_ms/1000}s", inline=True)
            if target_user:
                embed.add_field(name="Target User", value=f"<@{target_user}>", inline=True)
            if isinstance(active_redemption, dict) and isinstance(active_redemption.get("messages"),                    list) and active_redemption.get("messages"):
                embed.add_field(
                    name="Message Pool",
                    value=f"Uploaded file ({len(active_redemption['messages'])} messages)",
                    inline=False
                )
                embed.add_field(name="Message Pool", value=f"Uploaded file ({len(active_redemption['messages'])} messages)", inline=False)
            embed.add_field(name="Expires", value=format_expiry(expires_at), inline=True)
            embed.add_field(name="Next Steps", value="Press **Start** to restore the session from the saved active redemption.", inline=False)
            return embed, ManageView(uid, stype, None)
        
        embed = discord.Embed(color=discord.Color.red(),
                              description=f"> ❌ You have no active **{icon} {label}** session.")
        return embed, ManageView(uid, stype, None)
    
    color = discord.Color.green() if session["running"] else discord.Color.red()
    embed = discord.Embed(color=color, title=f"🎛️ {icon} {label} Panel")
    embed.add_field(name="Status",     value="🟢 Running" if session["running"] else "🔴 Stopped", inline=True)
    channel_label = "Voice Channel" if stype == "vc" else "Channel"
    embed.add_field(name=channel_label, value=f"<#{session['channelId']}>",                          inline=True)
    if stype == "vouch":
        embed.add_field(name="Vouching For", value=f"<@{session['targetUserId']}>", inline=True)
    embed.add_field(name="Delay",      value=f"{session['delayMs']/1000}s",         inline=True)
    embed.add_field(name="Expires",    value=format_expiry(session.get("expiresAt")), inline=True)
    embed.add_field(name="Tokens",     value=str(len(session["tokens"])),            inline=True)
    if session.get("messagePool"):
        embed.add_field(name="Message Pool", value=f"Uploaded file ({len(session['messagePool'])} messages)", inline=True)
    
    # Enhanced stats for VC
    if stype == "vc":
        connected = session.get("totalConnected", 0)
        total = len(session["tokens"])
        embed.add_field(name="Connected", value=f"{connected}/{total}", inline=True)
        
        duration = session.get("durationSeconds", 3600)
        duration_display = "Infinite" if duration == 0 else f"{int(duration)}s"
        embed.add_field(name="Duration", value=duration_display, inline=True)
        
        if session.get("startTime"):
            elapsed = (datetime.now(timezone.utc) - session["startTime"]).total_seconds()
            elapsed_display = f"{int(elapsed)}s"
            embed.add_field(name="Elapsed", value=elapsed_display, inline=True)
        
        embed.add_field(name="Retries/Token", value=str(session.get("maxRetries", 5)), inline=True)
    else:
        embed.add_field(name="Total Sent", value=str(session["totalSent"]),              inline=True)
    
    return embed, ManageView(uid, stype, session)

def build_admin_embed_and_view():
    embed = discord.Embed(color=discord.Color.blurple(), title="Control Panel",
                          description="Admin commands provided by the owner.")
    return embed, AdminView()

# ─── Bot ──────────────────────────────────────────────────────────────────────

try:
    intents = discord.Intents.all()
except AttributeError:
    print("ERROR: The imported discord package does not provide Intents.")
    print("discord module:", discord)
    print("discord file:", getattr(discord, '__file__', None))
    print("discord version:", getattr(discord, '__version__', None))
    print("Please ensure py-cord is installed and any conflicting discord.py package is removed.")
    sys.exit(1)

try:
    BotClass = discord.Bot
except AttributeError:
    try:
        from discord.ext import commands
        BotClass = commands.Bot
        print("WARNING: Falling back to commands.Bot because discord.Bot is unavailable.")
    except Exception:
        print("ERROR: No compatible Bot class found in discord package.")
        sys.exit(1)

if BotClass == discord.Bot:
    bot = BotClass(intents=intents, activity=discord.CustomActivity(name="MISHRA JI AUTO"))
else:
    # commands.Bot requires command_prefix
    bot = BotClass(command_prefix="!", intents=intents, activity=discord.CustomActivity(name="MISHRA JI AUTO"))

_original_slash_command = bot.slash_command

def slash_command(*args, **kwargs):
    def decorator(func):
        name = kwargs.get("name", func.__name__)
        description = kwargs.get("description", (func.__doc__ or "").strip() or "No description.")
        if not any(cmd["name"] == name for cmd in COMMANDS):
            COMMANDS.append({"name": name, "description": description})
        return _original_slash_command(*args, **kwargs)(func)
    return decorator

bot.slash_command = slash_command

# Flask Web Admin Panel Routes
@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        # Simple password check - in production, use proper auth
        admin_pass = os.environ.get('ADMIN_PASSWORD', 'admin123')  # Change this!
        if password == admin_pass:
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        flash('Invalid password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    # Gather stats
    balances = load_json(BALANCES_FILE)
    total_balance = sum(float(bal) for bal in balances.values() if isinstance(bal, (int, float, str)) and str(bal).replace('.', '').isdigit())
    
    active_redemptions = load_json(REDEMPTIONS_FILE)
    total_active_redemptions = sum(len(user_redemptions) for user_redemptions in active_redemptions.values())
    
    stats = {
        'total_users': len(read_lines(USERS_FILE)),
        'total_admins': len(read_lines(ADMINS_FILE)),
        'total_resellers': len(read_lines(RESELLERS_FILE)),
        'total_restricted': len(read_lines(RESTRICTED_FILE)),
        'total_tokens': len(get_tokens()),
        'total_keys': len(load_keys()),
        'active_sessions': len(sessions),
        'adv_licenses': len(load_adv_licenses()),
        'total_balance': round(total_balance, 2),
        'active_redemptions': total_active_redemptions
    }
    return render_template('dashboard.html', stats=stats)

@app.route('/users')
def users():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    users_list = read_lines(USERS_FILE)
    admins_list = read_lines(ADMINS_FILE)
    resellers_list = read_lines(RESELLERS_FILE)
    restricted_list = read_lines(RESTRICTED_FILE)
    balances = load_json(BALANCES_FILE)
    
    return render_template('users.html', users=users_list, admins=admins_list, 
                          resellers=resellers_list, restricted=restricted_list, balances=balances)

@app.route('/tokens')
def tokens():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    tokens_list = get_tokens()
    ontokens_list = read_lines(ONTOKENS_FILE)
    offtokens_list = read_lines(OFFTOKENS_FILE)
    
    return render_template('tokens.html', tokens=tokens_list, ontokens=ontokens_list, offtokens=offtokens_list)

@app.route('/keys')
def keys():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    keys_data = load_keys()
    return render_template('keys.html', keys=keys_data)

@app.route('/adv')
def adv():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    licenses = load_adv_licenses()
    adv_users = load_adv_users()
    return render_template('adv.html', licenses=licenses, adv_users=adv_users)

@app.route('/referrals')
def referrals():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    referrals_data = load_json(REFERRALS_FILE)
    return render_template('referrals.html', referrals=referrals_data)

@app.route('/redemptions')
def redemptions():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    redemptions_data = load_json(REDEMPTIONS_FILE)
    return render_template('redemptions.html', redemptions=redemptions_data)

@app.route('/messages')
def messages():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    messages_list = read_lines(MESSAGES_FILE)
    return render_template('messages.html', messages=messages_list)

@app.route('/reasons')
def reasons():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    reasons_list = read_lines(REASONS_FILE)
    return render_template('reasons.html', reasons=reasons_list)

@app.route('/trading')
def trading():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    trading_list = read_lines(TRADING_FILE)
    return render_template('trading.html', trading=trading_list)

@app.route('/trials')
def trials():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    trials_data = load_json(TRIAL_CLAIMS_FILE)
    return render_template('trials.html', trials=trials_data)

@app.route('/logs')
def logs():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    # For now, just show recent messages or something
    return render_template('logs.html')

# API endpoints for actions
@app.route('/api/clean_tokens', methods=['POST'])
def api_clean_tokens():
    if not session.get('logged_in'):
        return {'error': 'Not logged in'}, 401
    
    # Run clean in a new event loop
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(clean_tokens())
        return {'success': True}
    finally:
        loop.close()

@app.route('/api/revoke_key', methods=['POST'])
def api_revoke_key():
    if not session.get('logged_in'):
        return {'error': 'Not logged in'}, 401
    
    data = request.json
    key = data.get('key')
    
    if not key:
        return {'error': 'Key required'}, 400
    
    keys = load_keys()
    if key not in keys:
        return {'error': 'Key not found'}, 404
    
    # Mark as revoked
    keys[key]['status'] = 'revoked'
    save_keys(keys)
    
    return {'success': True}

@app.route('/api/delete_key', methods=['POST'])
def api_delete_key():
    if not session.get('logged_in'):
        return {'error': 'Not logged in'}, 401
    
    data = request.json
    key = data.get('key')
    
    if not key:
        return {'error': 'Key required'}, 400
    
    keys = load_keys()
    if key not in keys:
        return {'error': 'Key not found'}, 404
    
    del keys[key]
    save_keys(keys)
    
    return {'success': True}

@app.route('/api/clear_redemptions', methods=['POST'])
def api_clear_redemptions():
    if not session.get('logged_in'):
        return {'error': 'Not logged in'}, 401
    
    data = request.json
    user_id = data.get('user_id')
    service_type = data.get('service_type')
    
    redemptions = load_json(REDEMPTIONS_FILE)
    
    if user_id and service_type:
        if user_id in redemptions and service_type in redemptions[user_id]:
            del redemptions[user_id][service_type]
            if not redemptions[user_id]:
                del redemptions[user_id]
    elif user_id:
        redemptions.pop(user_id, None)
    else:
        redemptions = {}
    
    save_json(REDEMPTIONS_FILE, redemptions)
    
    return {'success': True}

@app.route('/api/update_trading_messages', methods=['POST'])
def api_update_trading_messages():
    if not session.get('logged_in'):
        return {'error': 'Not logged in'}, 401
    
    try:
        import json as json_lib
        types_str = request.form.get('types', '[]')
        types = json_lib.loads(types_str)
        
        if not types:
            return {'success': False, 'error': 'No message types selected'}, 400
        
        messages_list = []
        src_map = {
            "bf": "bloxfruits.txt",
            "sab": "sab.txt",
            "mm2": "mm2.txt",
        }
        
        # Handle mix type - load all sources
        if "mix" in types:
            for ch in ["bf", "sab", "mm2"]:
                fname = src_map.get(ch)
                if fname and Path(fname).exists():
                    try:
                        messages_list.extend(read_lines(Path(fname)))
                    except Exception as e:
                        print(f"Error reading {fname}: {e}")
            types = [t for t in types if t != "mix"]
        
        # Load other selected types
        for ch in types:
            if ch == "custom":
                continue
            fname = src_map.get(ch)
            if fname and Path(fname).exists():
                try:
                    messages_list.extend(read_lines(Path(fname)))
                except Exception as e:
                    print(f"Error reading {fname}: {e}")
        
        # Handle custom file upload
        if "custom" in types:
            if 'customFile' not in request.files:
                return {'success': False, 'error': 'Custom file required but not provided'}, 400
            
            file = request.files['customFile']
            if file.filename == '':
                return {'success': False, 'error': 'No file selected'}, 400
            
            try:
                content = file.read().decode('utf-8', errors='replace')
                custom_messages = [line.strip() for line in content.splitlines() if line.strip()]
                messages_list.extend(custom_messages)
            except Exception as e:
                return {'success': False, 'error': f'Failed to read custom file: {e}'}, 400
        
        if not messages_list:
            return {'success': False, 'error': 'No messages loaded from selected sources'}, 400
        
        # Save to trading.txt
        with open(BASE_DIR / "trading.txt", 'w', encoding='utf-8') as f:
            for msg in messages_list:
                f.write(msg + '\n')
        
        return {'success': True, 'message': f'Updated trading messages with {len(messages_list)} messages'}
    except Exception as e:
        return {'success': False, 'error': str(e)}, 500

async def clean_tokens():
    """Clean invalid tokens from all token files."""
    files = [
        (TOKENS_FILE, "tokens.txt"),
        (ONTOKENS_FILE, "ontokens.txt"),
        (OFFTOKENS_FILE, "offtokens.txt"),
    ]

    async with aiohttp.ClientSession() as http:
        for path, display in files:
            lines = [l for l in read_lines(path) if l.strip()]
            if not lines:
                continue

            valid_tokens = []
            invalid_tokens = []

            for token in lines:
                # quick format check
                if not is_valid_token_string(token):
                    invalid_tokens.append(token)
                    continue

                try:
                    async with http.get("https://discord.com/api/v9/users/@me", headers=_token_headers(token), timeout=aiohttp.ClientTimeout(total=5)) as res:
                        if res.status == 200:
                            valid_tokens.append(token)
                        else:
                            invalid_tokens.append(token)
                except Exception:
                    invalid_tokens.append(token)

            # overwrite file with valid tokens only
            if valid_tokens:
                path.write_text("\n".join(valid_tokens) + "\n", encoding="utf-8")
            else:
                # clear file
                path.write_text("", encoding="utf-8")

            print(f"[Clean] {display}: Kept {len(valid_tokens)}, Removed {len(invalid_tokens)}")

# Function to run Flask in thread
def run_flask():
    app.run(host='0.0.0.0', port=5000, debug=False)

# ─── Copy Details View (Individual Copy Buttons) ──────────────────────────────

class CopyDetailsView(discord.ui.View):
    """View with individual copy buttons for each account detail."""
    def __init__(self, token, channels, auto_msg, dm_resp, image_urls):
        super().__init__(timeout=300)
        self.token = token
        self.channels = channels
        self.auto_msg = auto_msg
        self.dm_resp = dm_resp
        self.image_urls = image_urls

        # Format image URLs for copying
        if image_urls:
            self.img_formatted = "\n".join(f"{i+1}. {url}" for i, url in enumerate(image_urls))
        else:
            self.img_formatted = "(no images configured)"

        # Create buttons manually and bind to methods that expect (self, interaction)
        btn_all = discord.ui.Button(label="📋 Copy All", style=discord.ButtonStyle.primary, custom_id="copy_all")
        btn_all.callback = self._copy_all
        self.add_item(btn_all)

        btn_token = discord.ui.Button(label="🔐 Copy Token", style=discord.ButtonStyle.blurple, custom_id="copy_token")
        btn_token.callback = self._copy_token
        self.add_item(btn_token)

        btn_channels = discord.ui.Button(label="📢 Copy Channels", style=discord.ButtonStyle.blurple, custom_id="copy_channels")
        btn_channels.callback = self._copy_channels
        self.add_item(btn_channels)

        btn_auto = discord.ui.Button(label="💬 Copy Auto Msg", style=discord.ButtonStyle.blurple, custom_id="copy_auto_msg")
        btn_auto.callback = self._copy_auto_msg
        self.add_item(btn_auto)

        btn_dm = discord.ui.Button(label="💌 Copy Auto Reply", style=discord.ButtonStyle.blurple, custom_id="copy_dm_resp")
        btn_dm.callback = self._copy_dm_resp
        self.add_item(btn_dm)

        btn_images = discord.ui.Button(label="🖼️ Copy Images", style=discord.ButtonStyle.blurple, custom_id="copy_images")
        btn_images.callback = self._copy_images
        self.add_item(btn_images)

    async def _copy_all(self, interaction: discord.Interaction):
        parts = []
        parts.append(f"🔐 TOKEN:\n```\n{self.token}\n```")
        parts.append(f"📢 CHANNELS:\n```\n{self.channels}\n```")
        parts.append(f"💬 AUTO MESSAGE:\n```\n{self.auto_msg}\n```")
        parts.append(f"💌 AUTO REPLY MESSAGE:\n```\n{self.dm_resp}\n```")
        parts.append(f"🖼️ IMAGE URLS ({len(self.image_urls)}):\n```\n{self.img_formatted}\n```")
        await interaction.response.send_message("\n\n".join(parts), ephemeral=True)

    async def _copy_token(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"```\n{self.token}\n```", ephemeral=True)

    async def _copy_channels(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"```\n{self.channels}\n```", ephemeral=True)

    async def _copy_auto_msg(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"```\n{self.auto_msg}\n```", ephemeral=True)

    async def _copy_dm_resp(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"```\n{self.dm_resp}\n```", ephemeral=True)

    async def _copy_images(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"```\n{self.img_formatted}\n```", ephemeral=True)

# ─── Adv Panel View ──────────────────────────────────────────────────────────

class AdvPanelView(discord.ui.View):
    def __init__(self, uid, lic_or_acc_id):
        super().__init__(timeout=None)
        self.uid = uid
        if isinstance(lic_or_acc_id, str):
            # acc_id for single account panel
            self.is_single = True
            lic = get_adv_license(uid)
            if lic:
                acc = next((a for a in lic.get("accounts", []) if a["id"] == lic_or_acc_id), None)
                if acc:
                    accounts = [acc]
                    slots = 1
                else:
                    accounts = []
                    slots = 1
            else:
                accounts = []
                slots = 1
            self.lic = lic
        else:
            # lic for main panel
            self.is_single = False
            self.lic = lic_or_acc_id
            accounts = self.lic.get("accounts", []) if self.lic else []
            slots = self.lic.get("slots", 1) if self.lic else 1
        at_max = len(accounts) >= slots

        add_btn   = discord.ui.Button(label="➕ Add Account",  style=discord.ButtonStyle.success,   custom_id="adv_add",       disabled=at_max,       row=0)
        mgr_btn   = discord.ui.Button(label="⚙️ Manage",       style=discord.ButtonStyle.secondary,  custom_id="adv_manage",    disabled=not accounts, row=0)
        start_btn = discord.ui.Button(label="▶ Start All",     style=discord.ButtonStyle.primary,    custom_id="adv_start_all",                        row=1)
        stop_btn  = discord.ui.Button(label="⏹ Stop All",      style=discord.ButtonStyle.danger,     custom_id="adv_stop_all",                         row=1)
        sched_btn = discord.ui.Button(label="⏱ Schedule",      style=discord.ButtonStyle.secondary,  custom_id="adv_schedule",                          row=1)
        img_btn   = discord.ui.Button(label="🖼 Edit Images",    style=discord.ButtonStyle.secondary,  custom_id="adv_add_images", disabled=not accounts, row=1)
        copy_btn  = discord.ui.Button(label="📋 Copy Details",  style=discord.ButtonStyle.secondary,  custom_id="adv_copy_details", disabled=not accounts, row=2)
        ref_btn   = discord.ui.Button(label="🔄 Refresh",      style=discord.ButtonStyle.secondary,  custom_id="adv_refresh",                          row=2)

        add_btn.callback   = self.add_callback
        mgr_btn.callback   = self.manage_callback
        start_btn.callback = self.start_all_callback
        stop_btn.callback  = self.stop_all_callback
        sched_btn.callback = self.schedule_callback
        img_btn.callback   = self.add_images_callback
        copy_btn.callback  = self.copy_details_callback
        ref_btn.callback   = self.refresh_callback

        self.add_item(add_btn)
        self.add_item(mgr_btn)
        self.add_item(start_btn)
        self.add_item(stop_btn)
        self.add_item(sched_btn)
        self.add_item(img_btn)
        self.add_item(copy_btn)
        self.add_item(ref_btn)

    async def add_callback(self, interaction: discord.Interaction):
        if not (str(interaction.user.id) == self.uid or can_manage_bot(str(interaction.user.id))):
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Not your panel."), ephemeral=True)
        lic      = get_adv_license(self.uid)
        accounts = lic.get("accounts", []) if lic else []
        slots    = lic.get("slots", 1) if lic else 1
        if len(accounts) >= slots:
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description=f"> ❌ You have used all **{slots}** account slots."), ephemeral=True)
        allow_dm = lic.get("allowDmReply", False) if lic else False
        await interaction.response.send_modal(AddAdvAccountModal(self.uid, allow_dm))

    async def add_images_callback(self, interaction: discord.Interaction):
        if not (str(interaction.user.id) == self.uid or can_manage_bot(str(interaction.user.id))):
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Not your panel."), ephemeral=True)
        lic      = get_adv_license(self.uid)
        accounts = lic.get("accounts", []) if lic else []
        if not accounts:
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ No accounts configured yet."), ephemeral=True)
        options = [discord.SelectOption(label=acc.get("name", f"Account {i+1}")[:100],
                                        description=f"{len(acc.get('channels', []))} channels | cycle delay {acc.get('rawDelay','?')}",
                                        value=acc["id"]) for i, acc in enumerate(accounts)]
        select = discord.ui.Select(placeholder="Select an account to edit images in",
                                   custom_id="adv_add_images_select", options=options[:25])
        async def select_callback(sel_interaction: discord.Interaction):
            acc_id = select.values[0]
            lic2   = get_adv_license(self.uid)
            acc    = next((a for a in lic2.get("accounts", []) if a["id"] == acc_id), None)
            if not acc:
                return await sel_interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Account not found."), ephemeral=True)
            await sel_interaction.response.send_modal(AddAdvImagesModal(self.uid, acc))
        select.callback = select_callback
        view = discord.ui.View(timeout=60)
        view.add_item(select)
        await interaction.response.send_message(content="Select an account to add images to:", view=view, ephemeral=True)

    async def copy_details_callback(self, interaction: discord.Interaction):
        if not (str(interaction.user.id) == self.uid or can_manage_bot(str(interaction.user.id))):
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Not your panel."), ephemeral=True)
        lic      = get_adv_license(self.uid)
        accounts = lic.get("accounts", []) if lic else []
        if not accounts:
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ No accounts configured yet."), ephemeral=True)
        options = [discord.SelectOption(label=acc.get("name", f"Account {i+1}")[:100],
                                        description=f"{len(acc.get('channels', []))} channels | {len(acc.get('imageUrls', []))} images",
                                        value=acc["id"]) for i, acc in enumerate(accounts)]
        select = discord.ui.Select(placeholder="Select an account to copy details from",
                                   custom_id="adv_copy_details_select", options=options[:25])
        async def select_callback(sel_interaction: discord.Interaction):
            acc_id = select.values[0]
            lic2   = get_adv_license(self.uid)
            acc    = next((a for a in lic2.get("accounts", []) if a["id"] == acc_id), None)
            if not acc:
                return await sel_interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Account not found."), ephemeral=True)
            
            # Format account details
            token = acc.get("token", "N/A")
            channels = ", ".join(acc.get("channels", []))
            auto_msg = acc.get("autoMessage", "") or "(empty)"
            dm_resp = acc.get("dmResponse", "") or "(empty)"
            image_urls = acc.get("imageUrls", [])
            
            # Build embed with field descriptions
            embed = discord.Embed(
                title=f"📋 Account Details — {acc.get('name', 'Account')}",
                description="**📋 Click \"Copy All\" to copy everything at once, or select individual details below**",
                color=discord.Color.blue()
            )
            embed.add_field(name="🔐 Token", value=f"`{len(token)} chars`", inline=False)
            embed.add_field(name="📢 Channels", value=f"`{len(channels)} chars | {len(acc.get('channels', []))} channels`", inline=False)
            embed.add_field(name="💬 Auto Message", value=f"`{len(auto_msg)} chars`", inline=False)
            embed.add_field(name="💌 Auto Reply Message", value=f"`{len(dm_resp)} chars`", inline=False)
            embed.add_field(name="🖼️ Image URLs", value=f"`{len(image_urls)} images`", inline=False)
            embed.set_footer(text="Each button copies that detail individually")
            
            # Create view with copy buttons
            view = CopyDetailsView(token, channels, auto_msg, dm_resp, image_urls)
            await sel_interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        
        select.callback = select_callback
        view = discord.ui.View(timeout=60)
        view.add_item(select)
        await interaction.response.send_message(content="Select an account to copy details from:", view=view, ephemeral=True)

    async def manage_callback(self, interaction: discord.Interaction):
        if not (str(interaction.user.id) == self.uid or can_manage_bot(str(interaction.user.id))):
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Not your panel."), ephemeral=True)
        lic      = get_adv_license(self.uid)
        accounts = lic.get("accounts", []) if lic else []
        if not accounts:
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ No accounts configured yet."), ephemeral=True)
        options = [discord.SelectOption(label=acc.get("name", f"Account {i+1}")[:100],
                                        description=f"{len(acc.get('channels', []))} channels | cycle delay {acc.get('rawDelay','?')}",
                                        value=acc["id"]) for i, acc in enumerate(accounts)]
        select = discord.ui.Select(placeholder="Select an account to manage",
                                   custom_id="adv_manage_select", options=options[:25])
        async def select_callback(sel_interaction: discord.Interaction):
            acc_id = select.values[0]
            lic2   = get_adv_license(self.uid)
            acc    = next((a for a in lic2.get("accounts", []) if a["id"] == acc_id), None)
            if not acc:
                return await sel_interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Account not found."), ephemeral=True)
            await sel_interaction.response.send_modal(EditAdvAccountModal(self.uid, acc))
        select.callback = select_callback
        view = discord.ui.View(timeout=60)
        view.add_item(select)
        await interaction.response.send_message(content="Select the account to manage:", view=view, ephemeral=True)

    async def schedule_callback(self, interaction: discord.Interaction):
        if not (str(interaction.user.id) == self.uid or can_manage_bot(str(interaction.user.id))):
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Not your panel."), ephemeral=True)
        lic      = get_adv_license(self.uid)
        accounts = lic.get("accounts", []) if lic else []
        if not accounts:
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ No accounts configured yet."), ephemeral=True)
        options = [discord.SelectOption(label=acc.get("name", f"Account {i+1}")[:100],
                                        description=f"{len(acc.get('channels', []))} channels | cycle delay {acc.get('rawDelay','?')}",
                                        value=acc["id"]) for i, acc in enumerate(accounts)]
        select = discord.ui.Select(placeholder="Select an account to schedule",
                                   custom_id="adv_schedule_select", options=options[:25])
        async def select_callback(sel_interaction: discord.Interaction):
            acc_id = select.values[0]
            lic2   = get_adv_license(self.uid)
            acc    = next((a for a in lic2.get("accounts", []) if a["id"] == acc_id), None)
            if not acc:
                return await sel_interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Account not found."), ephemeral=True)
            await sel_interaction.response.send_modal(ScheduleAdvModal(self.uid, acc))
        select.callback = select_callback
        view = discord.ui.View(timeout=60)
        view.add_item(select)
        await interaction.response.send_message(content="Select an account to schedule:", view=view, ephemeral=True)

    async def start_all_callback(self, interaction: discord.Interaction):
        if not (str(interaction.user.id) == self.uid or can_manage_bot(str(interaction.user.id))):
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Not your panel."), ephemeral=True)
        lic      = get_adv_license(self.uid)
        accounts = lic.get("accounts", []) if lic else []
        if not accounts:
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ No accounts to start."), ephemeral=True)
        for acc in accounts:
            await start_adv_account(self.uid, acc)
        embed, view = build_adv_panel(self.uid)
        await interaction.response.edit_message(embed=embed, view=view)

    async def stop_all_callback(self, interaction: discord.Interaction):
        if not (str(interaction.user.id) == self.uid or can_manage_bot(str(interaction.user.id))):
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Not your panel."), ephemeral=True)
        stop_all_adv(self.uid)
        embed, view = build_adv_panel(self.uid)
        await interaction.response.edit_message(embed=embed, view=view)

    async def refresh_callback(self, interaction: discord.Interaction):
        if not (str(interaction.user.id) == self.uid or can_manage_bot(str(interaction.user.id))):
            return await interaction.response.send_message(
                embed=discord.Embed(
                    color=discord.Color.red(),
                    description="> ❌ Not your panel."
                ),
                ephemeral=True
            )

        embed, view = build_adv_panel(self.uid)

        await interaction.response.edit_message(
            embed=embed,
            view=view
        )

class AddAdvAccountModal(discord.ui.Modal):
    def __init__(self, uid, allow_dm):
        super().__init__(title="Add Account")
        self.uid      = uid
        self.allow_dm = allow_dm
        self.add_item(discord.ui.InputText(custom_id="token",       label="User Token",                          style=discord.InputTextStyle.short,     placeholder="Paste user token here",                      required=True))
        self.add_item(discord.ui.InputText(custom_id="channels",    label="Channel IDs (comma separated)",    style=discord.InputTextStyle.short,     placeholder="channel_id1, channel_id2",                          required=True))
        self.add_item(discord.ui.InputText(custom_id="delay",       label="Cycle delay (e.g. 30s 5m)",style=discord.InputTextStyle.short,     placeholder="30s | 1m | 5m | 1h",                         required=True))
        self.add_item(discord.ui.InputText(custom_id="auto_msg", label="Auto Message (sent in channels)", style=discord.InputTextStyle.paragraph,
            placeholder="Message to auto-send in the channels", required=False))
        self.add_item(discord.ui.InputText(custom_id="dm_response", label="DM Auto Response (leave blank = off)",style=discord.InputTextStyle.paragraph, placeholder="Reply sent to anyone who DMs this account",   required=False))

    async def callback(self, interaction: discord.Interaction):
        uid        = self.uid
        token_val  = self.children[0].value.strip()
        channels   = [c.strip() for c in self.children[1].value.split(",") if c.strip()]
        delay_raw  = self.children[2].value.strip()
        auto_msg   = self.children[3].value.strip()
        dm_resp    = self.children[4].value.strip()
        delay_secs = parse_delay_string(delay_raw)

        image_urls = []

        if not channels:
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ At least one channel ID required."), ephemeral=True)

        # Validate channel IDs format
        invalid_channels = [ch for ch in channels if not ch.isdigit() or len(ch) < 17]
        if invalid_channels:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    color=discord.Color.red(),
                    description=f"> ❌ Invalid channel IDs: {', '.join(invalid_channels[:5])}\n> Channel IDs should be 17-20 digit numbers."
                ),
                ephemeral=True
            )

        dm_resp = dm_resp if self.allow_dm and dm_resp else ""
        await interaction.response.defer(ephemeral=True)

        self_user_id = None
        try:
            async with aiohttp.ClientSession() as http:
                async with http.get("https://discord.com/api/v9/users/@me", headers=_msg_headers(token_val)) as res:
                    if not res.ok:
                        return await interaction.followup.send(embed=discord.Embed(color=discord.Color.red(), description=f"> ❌ Invalid token (HTTP {res.status})."), ephemeral=True)
                    me           = await res.json()
                    self_user_id = me.get("id")
                    acc_name     = me.get("username", "Account")
        except Exception as e:
            return await interaction.followup.send(embed=discord.Embed(color=discord.Color.red(), description=f"> ❌ Could not verify token: {e}"), ephemeral=True)

        licenses = load_adv_licenses()
        lic      = licenses.get(uid, {})
        if "accounts" not in lic: lic["accounts"] = []

        acc_id = str(uuid.uuid4())[:8]
        acc    = {"id": acc_id, "name": acc_name, "token": token_val, "channels": channels,
                  "rawDelay": delay_raw, "delaySecs": delay_secs,
                  "autoMessage": auto_msg, "imageUrls": image_urls,
                  "dmResponse": dm_resp, "selfUserId": self_user_id}
        lic["accounts"].append(acc)
        licenses[uid] = lic
        save_adv_licenses(licenses)

        await start_adv_account(uid, acc)

        embed, view = build_adv_panel(uid)
        await interaction.followup.send(embed=discord.Embed(color=discord.Color.green(),
                                                            description=f"> ✅ **{acc_name}** added and started!"), ephemeral=True)
        try:
            await interaction.message.edit(embed=embed, view=view)
        except Exception:
            pass


class AddAdvImagesModal(discord.ui.Modal):
    def __init__(self, uid, acc):
        super().__init__(title=f"Edit Images — {acc.get('name', 'Account')}")
        self.uid = uid
        self.acc_id = acc["id"]
        current_urls = acc.get("imageUrls", [])
        
        self.add_item(discord.ui.TextInput(
            custom_id="image_links", 
            label="Image URLs (one per line, optional)",
            style=discord.InputTextStyle.paragraph,
            value="\n".join(current_urls) if current_urls else "",
            placeholder="https://example.com/image1.png\nhttps://example.com/image2.jpg",
            required=False,
            max_length=4000
        ))

    async def callback(self, interaction: discord.Interaction):
        image_input = self.children[0].value.strip()
        image_urls = normalize_image_urls(image_input)
        if image_input and not image_urls:
            return await interaction.response.send_message(
                embed=discord.Embed(color=discord.Color.red(),
                                    description="> ❌ No valid image URLs detected. Please enter valid URLs starting with http:// or https://, one per line."),
                ephemeral=True
            )
        
        licenses = load_adv_licenses()
        lic      = licenses.get(self.uid, {})
        accounts = lic.get("accounts", [])
        idx = next((i for i, a in enumerate(accounts) if a["id"] == self.acc_id), None)
        if idx is None:
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Account not found."), ephemeral=True)
        
        accounts[idx]["imageUrls"] = image_urls
        lic["accounts"] = accounts
        licenses[self.uid] = lic
        save_adv_licenses(licenses)
        key = skey(self.uid, self.acc_id)
        state = adv_sessions.get(key)
        if state:
            state["imageUrls"] = image_urls
        
        # Show confirmation with image count
        count_text = f"{len(image_urls)} image(s)" if image_urls else "No images"
        await interaction.response.send_message(
            embed=discord.Embed(color=discord.Color.green(), description=f"> ✅ Saved — {count_text}"),
            ephemeral=True
        )


class ScheduleAdvModal(discord.ui.Modal):
    def __init__(self, uid, acc):
        super().__init__(title=f"Schedule Auto Adv — {acc.get('name', 'Account')}")
        self.uid = uid
        self.acc_id = acc["id"]
        self.acc_name = acc.get("name", "Account")
        self.add_item(discord.ui.TextInput(custom_id="duration", label="Run duration", style=discord.InputTextStyle.short, placeholder="30s | 5m | 2h | 1d", required=True))

    async def callback(self, interaction: discord.Interaction):
        duration_raw = self.children[0].value.strip()
        m = re.match(r'^(\d+)([smhd])$', duration_raw, re.IGNORECASE)
        if not m:
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Invalid duration. Use 30s, 5m, 2h, or 1d."), ephemeral=True)
        duration_secs = int(m.group(1)) * {"s": 1, "m": 60, "h": 3600, "d": 86400}[m.group(2).lower()]

        licenses = load_adv_licenses()
        lic      = licenses.get(self.uid, {})
        accounts = lic.get("accounts", [])
        acc      = next((a for a in accounts if a["id"] == self.acc_id), None)
        if not acc:
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Account not found."), ephemeral=True)

        key = skey(self.uid, self.acc_id)
        state = adv_sessions.get(key)
        started_now = False
        if not state or not state.get("running"):
            await start_adv_account(self.uid, acc)
            state = adv_sessions.get(key)
            started_now = True

        if state:
            existing_task = state.get("schedule_task")
            if existing_task and not existing_task.done():
                existing_task.cancel()

            schedule_end = datetime.now(timezone.utc) + timedelta(seconds=duration_secs)
            state["schedule_task"] = asyncio.create_task(self._scheduled_stop(duration_secs))
            state["schedule_end_time"] = schedule_end.isoformat()

        if started_now:
            await send_adv_log_dm(self.uid,
                f"⏱ **Auto Adv Scheduled**\n\n> {self.acc_name} started and will stop after {duration_raw}."
            )
        else:
            await send_adv_log_dm(self.uid,
                f"⏱ **Auto Adv Schedule Set**\n\n> {self.acc_name} is already running and will stop after {duration_raw}."
            )

        await interaction.response.send_message(embed=discord.Embed(color=discord.Color.green(), description=f"> ✅ Scheduled **{self.acc_name}** for {duration_raw}."), ephemeral=True)

    async def _scheduled_stop(self, duration_secs):
        key = skey(self.uid, self.acc_id)
        try:
            await asyncio.sleep(duration_secs)
            state = adv_sessions.get(key)
            if not state or not state.get("running"):
                return
            stop_adv_account(self.uid, self.acc_id)
            
            # Format duration
            mins, secs = divmod(int(duration_secs), 60)
            hours, mins = divmod(mins, 60)
            duration_str = f"{hours}h {mins}m {secs}s" if hours else f"{mins}m {secs}s" if mins else f"{secs}s"
            
            await send_adv_log_dm(self.uid,
                f"⏹️ **Auto Adv Schedule Ended**\n\n"
                f"Account: {self.acc_name}\n"
                f"Duration: {duration_str}\n"
                f"Total messages: {state.get('totalSent', 0)}\n"
                f"DM replies: {state.get('dmReplied', 0)}"
            )
        except asyncio.CancelledError:
            return
        finally:
            state = adv_sessions.get(key)
            if state:
                state.pop("schedule_task", None)
                state.pop("schedule_end_time", None)


class EditAdvAccountModal(discord.ui.Modal):
    def __init__(self, uid, acc):
        super().__init__(title=f"Edit {acc.get('name', 'Account')}")

        self.uid = uid
        self.acc_id = acc["id"]
        lic = acc.get("license", {}) or {}
        self.allow_dm = lic.get("allowDmReply", False)

        self.add_item(discord.ui.TextInput(custom_id="token", label="User Token",
            style=discord.InputTextStyle.short, value=acc.get("token", ""), required=True))

        self.add_item(discord.ui.TextInput(custom_id="channels", label="Channel IDs (comma separated)",
            style=discord.InputTextStyle.short, value=", ".join(acc.get("channels", [])), required=True))

        self.add_item(discord.ui.TextInput(custom_id="delay", label="Cycle delay (e.g. 30s 5m 1h)",
            style=discord.InputTextStyle.short, value=acc.get("rawDelay", "1m"), required=True))

        self.add_item(discord.ui.TextInput(custom_id="auto_msg", label="Auto Message",
            style=discord.InputTextStyle.paragraph, value=acc.get("autoMessage", ""), required=False))

        if self.allow_dm:
            self.add_item(discord.ui.TextInput(custom_id="action_dm_response", label="Action + DM Response",
                style=discord.InputTextStyle.paragraph,
                value=f"save\n{acc.get('dmResponse', '')}",
                placeholder="First line: action (save | delete | stop | start)\nRemaining lines: DM response",
                required=True))
        else:
            self.add_item(discord.ui.TextInput(custom_id="action", label="Action: save | delete | stop | start",
                style=discord.InputTextStyle.short, placeholder="save | delete | stop | start", required=True))

    async def callback(self, interaction: discord.Interaction):
        uid    = self.uid
        acc_id = self.acc_id
        
        # 🔹 PARSE INPUTS (ORDERED)
        i = 0
        token     = self.children[i].value.strip()
        i += 1
        channels  = [
            c.strip()
            for c in self.children[i].value.split(",")
            if c.strip()
        ]
        i += 1
        delay_raw = self.children[i].value.strip()
        i += 1
        auto_msg  = self.children[i].value.strip()
        i += 1
        
        # Validate channel IDs format
        invalid_channels = [ch for ch in channels if not ch.isdigit() or len(ch) < 17]
        if invalid_channels:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    color=discord.Color.red(),
                    description=f"> ❌ Invalid channel IDs: {', '.join(invalid_channels[:5])}\n> Channel IDs should be 17-20 digit numbers."
                ),
                ephemeral=True
            )
        
        image_urls = []
        
        if self.allow_dm:
            action_and_dm = self.children[i].value.strip()
            lines = action_and_dm.splitlines()
            action = lines[0].strip().lower() if lines else "save"
            dm_resp = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""
        else:
            action = self.children[i].value.strip().lower()
            dm_resp = ""
        delay_secs = parse_delay_string(delay_raw)
        # 🔹 LOAD DATA
        licenses = load_adv_licenses()
        lic      = licenses.get(uid, {})
        accounts = lic.get("accounts", [])
        idx = next((i for i, a in enumerate(accounts) if a["id"] == acc_id),
            None)
        # ❌ ACCOUNT NOT FOUND
        if idx is None:
            await interaction.response.send_message(
                embed=discord.Embed(
                    color=discord.Color.red(),
                    description="❌ Account not found."
                ),
                ephemeral=True
            )
            return
        
        image_urls = accounts[idx].get("imageUrls", [])
        
        old_token = accounts[idx].get("token", "")

        if action in ("save", "start"):
            if token != old_token:
                is_valid, msg, user_info, _ = await validate_adv_token(token)

                if not is_valid:
                    return await interaction.response.send_message(
                        embed=discord.Embed(
                                 color=discord.Color.red(),
                            description=f"❌ Invalid token: {msg}"
                        ),
                        ephemeral=True
                    )

                self_user_id = user_info.get("id")
                accounts[idx]["selfUserId"] = self_user_id

        accounts[idx]["token"] = token

        # 🔥 ACTION HANDLER
        if action == "delete":
            stop_adv_account(uid, acc_id)
            accounts.pop(idx)
        elif action == "stop":
            stop_adv_account(uid, acc_id)
        elif action == "start":
            await start_adv_account(uid, accounts[idx])
        elif action == "save":
            accounts[idx].update({
                "token":       token,
                "channels":    channels,
                "rawDelay":    delay_raw,
                "delaySecs":   delay_secs,
                "autoMessage": auto_msg,
                "imageUrls":   image_urls,
                "dmResponse":  dm_resp,
                "selfUserId":  accounts[idx].get("selfUserId")
            })
            stop_adv_account(uid, acc_id)
            await start_adv_account(uid, accounts[idx])
        # 💾 SAVE BACK
        lic["accounts"] = accounts
        licenses[uid]   = lic
        save_adv_licenses(licenses)
        # ✅ RESPONSE
        await interaction.response.send_message(
            "✅ Updated successfully",
            ephemeral=True
        )
# ─── Manage View (Vouch/Chat/Trade) ──────────────────────────────────────────

class ManageView(discord.ui.View):
    def __init__(self, uid, stype, session):
        super().__init__(timeout=None)
        self.uid = uid; self.stype = stype
        running  = session["running"] if session else False
        start_btn = discord.ui.Button(label="▶ Start",           style=discord.ButtonStyle.success,  custom_id=f"manage_start_{stype}",   disabled=running)
        stop_btn  = discord.ui.Button(label="⏹ Stop",            style=discord.ButtonStyle.danger,   custom_id=f"manage_stop_{stype}",    disabled=not running)
        ch_btn    = discord.ui.Button(label="📢 Change Channel", style=discord.ButtonStyle.primary,  custom_id=f"manage_channel_{stype}", row=1)
        start_btn.callback = self.start_callback
        stop_btn.callback  = self.stop_callback
        ch_btn.callback    = self.channel_callback
        self.add_item(start_btn); self.add_item(stop_btn); self.add_item(ch_btn)
        if self.stype != "vc":
            msg_btn = discord.ui.Button(label="📄 Upload Message file", style=discord.ButtonStyle.secondary, custom_id=f"manage_messages_{stype}", row=2)
            remove_btn = discord.ui.Button(label="🗑 Remove Messages", style=discord.ButtonStyle.danger, custom_id=f"manage_remove_messages_{stype}", row=2)
            msg_btn.callback = self.messages_callback
            remove_btn.callback = self.remove_messages_callback
            self.add_item(msg_btn); self.add_item(remove_btn)
        if stype == "vouch":
            uid_btn = discord.ui.Button(label="👤 Change User ID", style=discord.ButtonStyle.primary, custom_id="manage_userid_vouch", row=1)
            uid_btn.callback = self.userid_callback
            self.add_item(uid_btn)

    async def start_callback(self, interaction: discord.Interaction):
        session = sessions.get(skey(self.uid, self.stype))
        if not session:
            # If there's a redemption stored in JSON, try to create an in-memory session from it
            redemption = get_active_redemption(self.uid, self.stype)
            if redemption:
                # redemption may be a dict or legacy string
                if isinstance(redemption, dict):
                    meta = redemption
                    # Determine tokens to use
                    tokens = meta.get("tokens") or []
                    if not tokens:
                        # Fallback: read from token files
                        src = TOKENS_FILE if self.stype in ("vouch","chat","trade","reacts") else ONTOKENS_FILE
                        tokens = [t for t in read_lines(src) if is_valid_token_string(t)][:int(meta.get("tokenCount", 0) or 0)]
                    if not tokens:
                        return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description=f"> ❌ No tokens available to start the session from redemption."), ephemeral=True)

                    delay_ms = get_meta_value(meta, "delayMs")
                    if delay_ms is None:
                        delay_seconds = get_meta_value(meta, "delaySeconds", "delay_seconds", "delay")
                        if delay_seconds is not None:
                            try:
                                delay_ms = int(float(delay_seconds) * 1000)
                            except Exception:
                                delay_ms = 60000
                        else:
                            delay_ms = 60000
                    else:
                        try:
                            delay_ms = int(delay_ms)
                        except Exception:
                            delay_ms = 60000

                    sessions[skey(self.uid, self.stype)] = {
                        "type": self.stype,
                        "tokens": tokens,
                        "guildId": get_meta_value(meta, "guildId", "guild_id"),
                        "channelId": get_meta_value(meta, "channelId", "channel_id", "channel"),
                        "messageId": get_meta_value(meta, "messageId", "message_id"),
                        "emoji": get_meta_value(meta, "emoji"),
                        "targetUserId": get_meta_value(meta, "targetUserId", "target_user_id") or None,
                        "messagePool": meta.get("messages") or None,
                        "delayMs": delay_ms,
                        "running": True,
                        "tokenIndex": 0,
                        "totalSent": 0,
                        "totalConnected": 0,
                        "totalAttempts": 0,
                        "tokenUserIds": {},
                        "lastMessage": "",
                        "durationSeconds": meta.get("duration_seconds"),
                        "expiresAt": meta.get("expiresAt"),
                        "maxRetries": meta.get("maxRetries", 5),
                        "startTime": datetime.now(timezone.utc),
                        "status": "running",
                    }
                    session = sessions.get(skey(self.uid, self.stype))
                    # start presence and loops
                    if self.stype != "vc":
                        asyncio.create_task(start_presence_for_tokens(session.get("tokens", [])))
                    if self.stype == "vouch":
                        asyncio.create_task(vouch_loop(self.uid))
                    elif self.stype == "vc":
                        asyncio.create_task(vc_loop(self.uid))
                    else:
                        asyncio.create_task(text_loop(self.uid, self.stype))
                else:
                    # legacy string redemption - cannot auto-start without metadata
                    return await interaction.response.send_message(
                        embed=discord.Embed(color=discord.Color.yellow(), description=f"> ⚠️ You have an active redemption (key: {redemption}) but the session lacks metadata. Redeem again using the UI to create an active session."),
                        ephemeral=True
                    )
            else:
                return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ No active session."), ephemeral=True)
        if not session["running"]:
            session["running"] = True
            if self.stype != "vc":
                asyncio.create_task(start_presence_for_tokens(session.get("tokens", [])))
            if self.stype == "vouch":
                asyncio.create_task(vouch_loop(self.uid))
            elif self.stype == "vc":
                asyncio.create_task(vc_loop(self.uid))
            else:
                asyncio.create_task(text_loop(self.uid, self.stype))
        embed, view = build_manage_embed_and_view(self.uid, self.stype)
        await interaction.response.edit_message(embed=embed, view=view)

    async def stop_callback(self, interaction: discord.Interaction):
        session = sessions.get(skey(self.uid, self.stype))
        if not session:
            # Check if there's an active redemption but no session in memory
            redemption = get_active_redemption(self.uid, self.stype)
            if redemption:
                # Clear the active redemption
                clear_active_redemption(self.uid, self.stype)
                return await interaction.response.send_message(
                    embed=discord.Embed(
                        color=discord.Color.green(),
                        description="> ✅ Cleared the active redemption."
                    ),
                    ephemeral=True
                )
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ No active session."), ephemeral=True)
        stop_session(self.uid, self.stype)
        if self.stype == "vc":
            await disconnect_voice_connections(self.uid)
        embed, view = build_manage_embed_and_view(self.uid, self.stype)
        await interaction.response.edit_message(embed=embed, view=view)

    async def channel_callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(ChangeChannelModal(self.uid, self.stype))

    async def messages_callback(self, interaction: discord.Interaction):
        if self.stype == "trade":
            # Present a small view offering paste or upload options
            class TradeUploadView(discord.ui.View):
                def __init__(self, uid, stype):
                    super().__init__(timeout=180)
                    self.uid = uid
                    self.stype = stype
                    paste_btn = discord.ui.Button(label="Paste Messages", style=discord.ButtonStyle.secondary, custom_id=f"trade_paste_{uid}")
                    upload_btn = discord.ui.Button(label="Upload Attachment", style=discord.ButtonStyle.primary, custom_id=f"trade_upload_{uid}")
                    cancel_btn = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.danger, custom_id=f"trade_upload_cancel_{uid}")
                    paste_btn.callback = self.paste_callback
                    upload_btn.callback = self.upload_callback
                    cancel_btn.callback = self.cancel_callback
                    self.add_item(paste_btn); self.add_item(upload_btn); self.add_item(cancel_btn)

                async def paste_callback(self, interaction: discord.Interaction):
                    try:
                        await safe_send_modal(interaction, PasteMessagesModal(self.uid, self.stype))
                    except Exception as e:
                        print(f"[TradeUploadView:paste] {e}")
                        try:
                            await interaction.response.send_message("Failed to open paste modal.", ephemeral=True)
                        except Exception:
                            pass

                async def upload_callback(self, interaction: discord.Interaction):
                    await interaction.response.send_message("📄 Upload a plain text file (one message per line) in this channel or DM me within 5 minutes. Reply `cancel` to abort.", ephemeral=True)

                    def check(m: discord.Message):
                        return m.author.id == interaction.user.id and (
                            m.channel == interaction.channel or isinstance(m.channel, discord.DMChannel)
                        ) and (len(m.attachments) > 0 or (m.content and m.content.lower().strip() == "cancel"))

                    async def _wait_for_upload():
                        try:
                            msg = await bot.wait_for('message', check=check, timeout=300)
                        except asyncio.TimeoutError:
                            try:
                                await interaction.followup.send("⏱️ Timed out — no file received.", ephemeral=True)
                            except Exception:
                                pass
                            return

                        if msg.content and msg.content.lower().strip() == "cancel":
                            try:
                                await interaction.followup.send("❌ Upload cancelled.", ephemeral=True)
                            except Exception:
                                pass
                            return

                        if not msg.attachments:
                            try:
                                await interaction.followup.send("❌ No attachment found. Upload cancelled.", ephemeral=True)
                            except Exception:
                                pass
                            return

                        att = msg.attachments[0]
                        try:
                            data = await att.read()
                            text = data.decode('utf-8', errors='replace')
                        except Exception as e:
                            try:
                                await interaction.followup.send("❌ Failed to read attachment; ensure it's a text file.", ephemeral=True)
                            except Exception:
                                pass
                            print(f"[TradeUploadView:upload] Read error: {e}")
                            return

                        messages_list = [line.strip() for line in text.splitlines() if line.strip()]
                        session = sessions.get(skey(self.uid, self.stype))
                        if session:
                            session["messagePool"] = messages_list if messages_list else None
                        redemption = get_active_redemption(self.uid, self.stype)
                        if isinstance(redemption, dict):
                            redemption["messages"] = session["messagePool"] if session else (messages_list if messages_list else None)
                            set_active_redemption(self.uid, self.stype, redemption)

                        try:
                            await interaction.followup.send(embed=discord.Embed(color=discord.Color.green(), description="> ✅ Message file uploaded and saved."), ephemeral=True)
                        except Exception:
                            pass

                    asyncio.create_task(_wait_for_upload())

                async def cancel_callback(self, interaction: discord.Interaction):
                    try:
                        await interaction.response.edit_message(content="Cancelled.", view=None)
                    except Exception:
                        try:
                            await interaction.response.send_message("Cancelled.", ephemeral=True)
                        except Exception:
                            pass

            await interaction.response.send_message("Choose how you'd like to provide trade messages:", view=TradeUploadView(self.uid, self.stype), ephemeral=True)
            return

        await interaction.response.send_message(
            "Please upload a plain text file (one message per line) in this channel or DM me within 5 minutes. Reply `cancel` to abort.",
            ephemeral=True
        )

        async def _wait_for_upload():
            def check(m: discord.Message):
                return m.author.id == interaction.user.id and (
                    m.channel == interaction.channel or isinstance(m.channel, discord.DMChannel)
                ) and (len(m.attachments) > 0 or (m.content and m.content.lower().strip() == "cancel"))

            try:
                msg = await bot.wait_for('message', check=check, timeout=300)
            except asyncio.TimeoutError:
                try:
                    await interaction.followup.send("Timed out — no file received.", ephemeral=True)
                except Exception:
                    pass
                return

            if msg.content and msg.content.lower().strip() == "cancel":
                await interaction.followup.send("Upload cancelled.", ephemeral=True)
                return

            if not msg.attachments:
                await interaction.followup.send("No attachment found. Upload cancelled.", ephemeral=True)
                return

            att = msg.attachments[0]
            try:
                data = await att.read()
                text = data.decode('utf-8', errors='replace')
            except Exception:
                await interaction.followup.send("Failed to read attachment; ensure it's a text file.", ephemeral=True)
                return

            messages_list = [line.strip() for line in text.splitlines() if line.strip()]
            session = sessions.get(skey(self.uid, self.stype))
            if session:
                session["messagePool"] = messages_list if messages_list else None
            redemption = get_active_redemption(self.uid, self.stype)
            if isinstance(redemption, dict):
                redemption["messages"] = session["messagePool"] if session else (messages_list if messages_list else None)
                set_active_redemption(self.uid, self.stype, redemption)

            await interaction.followup.send(
                embed=discord.Embed(color=discord.Color.green(), description="> ✅ Message file uploaded and saved."),
                ephemeral=True
            )

        asyncio.create_task(_wait_for_upload())

    async def remove_messages_callback(self, interaction: discord.Interaction):
        session = sessions.get(skey(self.uid, self.stype))
        if session:
            session["messagePool"] = None
        redemption = get_active_redemption(self.uid, self.stype)
        if isinstance(redemption, dict):
            redemption["messages"] = None
            set_active_redemption(self.uid, self.stype, redemption)
        await interaction.response.send_message(
            embed=discord.Embed(color=discord.Color.green(), description="> ✅ Message file removed from the session."),
            ephemeral=True
        )

    async def userid_callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(ChangeUserIdModal(self.uid))

class ChangeMessagesModal(discord.ui.Modal):
    def __init__(self, uid, stype):
        super().__init__(title="Update Message Pool")
        self.uid = uid
        self.stype = stype
        self.messages = discord.ui.TextInput(
            label="Messages",
            style=discord.InputTextStyle.paragraph,
            required=False,
            placeholder="Paste one message per line. Leave empty to remove the file."
        )
        self.add_item(self.messages)

    async def on_submit(self, interaction: discord.Interaction):
        raw = self.messages.value or ""
        messages_list = [line.strip() for line in raw.splitlines() if line.strip()]
        session = sessions.get(skey(self.uid, self.stype))
        if session:
            session["messagePool"] = messages_list if messages_list else None
        redemption = get_active_redemption(self.uid, self.stype)
        if isinstance(redemption, dict):
            redemption["messages"] = session["messagePool"] if session else (messages_list if messages_list else None)
            set_active_redemption(self.uid, self.stype, redemption)
        if not session and not isinstance(redemption, dict):
            return await interaction.response.send_message(
                embed=discord.Embed(color=discord.Color.red(), description="> ❌ No active session to update."),
                ephemeral=True
            )
        description = (
            f"> ✅ Updated the session to use **{len(messages_list)}** messages from the new file."
            if messages_list else 
            "> ✅ Removed the uploaded message file from the session."
        )
        await interaction.response.send_message(
            embed=discord.Embed(color=discord.Color.green(), description=description),
            ephemeral=True
        )


class PasteMessagesModal(discord.ui.Modal):
    def __init__(self, uid, stype):
        super().__init__(title="Paste Messages")
        self.uid = uid
        self.stype = stype
        self.add_item(discord.ui.InputText(custom_id="paste_msgs", label="Messages (one per line)", style=discord.InputTextStyle.long, placeholder="message1\nmessage2\n...", required=True))

    async def on_submit(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=True)
            raw = self.children[0].value or ""
            messages_list = [line.strip() for line in raw.splitlines() if line.strip()]
            session = sessions.get(skey(self.uid, self.stype))
            if session:
                session["messagePool"] = messages_list if messages_list else None
            redemption = get_active_redemption(self.uid, self.stype)
            if isinstance(redemption, dict):
                redemption["messages"] = session["messagePool"] if session else (messages_list if messages_list else None)
                set_active_redemption(self.uid, self.stype, redemption)

            description = (
                f"> ✅ Updated the session to use **{len(messages_list)}** pasted messages." if messages_list else 
                "> ✅ Removed the pasted messages from the session."
            )
            await interaction.followup.send(embed=discord.Embed(color=discord.Color.green(), description=description), ephemeral=True)
        except Exception as e:
            tb = traceback.format_exc()
            print(f"[PasteMessagesModal:{self.uid}] Error: {e}\n{tb}")
            try:
                logs_dir = BASE_DIR / "logs"
                logs_dir.mkdir(parents=True, exist_ok=True)
                log_file = logs_dir / "modal_errors.log"
                with open(log_file, "a", encoding="utf-8") as lf:
                    lf.write(f"{datetime.now(timezone.utc).isoformat()} - PasteMessagesModal:{self.uid} - {str(e)}\n")
                    lf.write(tb + "\n\n")
            except Exception as _logexc:
                print(f"[PasteMessagesModal] Failed to write log: {_logexc}")

            try:
                await interaction.followup.send(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Unexpected error occurred while processing your request. The error has been logged."), ephemeral=True)
            except Exception:
                pass


class ChangeTradeMessagesModal(discord.ui.Modal):
    def __init__(self, uid, stype):
        super().__init__(title="Update Trade Message Source")
        self.uid = uid
        self.stype = stype
        self.add_item(discord.ui.InputText(custom_id="opt1", label="Source 1", style=discord.InputTextStyle.short,
                                          placeholder="bf | sab | mm2 | custom | mix", required=False))
        self.add_item(discord.ui.InputText(custom_id="opt2", label="Source 2", style=discord.InputTextStyle.short,
                                          placeholder="bf | sab | mm2 | custom | mix", required=False))
        self.add_item(discord.ui.InputText(custom_id="opt3", label="Source 3", style=discord.InputTextStyle.short,
                                          placeholder="bf | sab | mm2 | custom | mix", required=False))

    async def on_submit(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=True)
            
            opts = [self.children[i].value.strip().lower() for i in range(3) if self.children[i].value and self.children[i].value.strip()]
            # Map full names to short names
            alias_map = {"bloxfruits": "bf", "exchanges": "mm2"}
            opts = [alias_map.get(opt, opt) for opt in opts]
            
            valid_choices = {"bf", "sab", "mm2", "custom", "mix"}
            invalid = [opt for opt in opts if opt not in valid_choices]
            if invalid:
                return await interaction.followup.send(
                    embed=discord.Embed(color=discord.Color.red(), description=f"> ❌ Invalid source(s): {', '.join(invalid)}. Available: bf, sab, mm2, custom, mix."),
                    ephemeral=True
                )

            choices = [opt for opt in opts if opt in valid_choices]
            if not choices:
                return await interaction.followup.send(
                    embed=discord.Embed(color=discord.Color.red(), description="> ❌ Please choose at least one source."),
                    ephemeral=True
                )

            src_map = {
                "bf": "bloxfruits.txt",
                "sab": "sab.txt",
                "mm2": "mm2.txt",
            }

            async def read_custom_file():
                await interaction.followup.send(
                    "📄 **Custom Message Upload**\n\nUpload a plain text file (one message per line) in this channel or DM me within 5 minutes. Reply `cancel` to abort.",
                    ephemeral=True
                )

                def check(m: discord.Message):
                    return m.author.id == interaction.user.id and (
                        m.channel == interaction.channel or isinstance(m.channel, discord.DMChannel)
                    ) and (len(m.attachments) > 0 or (m.content and m.content.lower().strip() == "cancel"))

                try:
                    msg = await bot.wait_for('message', check=check, timeout=300)
                except asyncio.TimeoutError:
                    await interaction.followup.send("⏱️ Timed out — no file received within 5 minutes.", ephemeral=True)
                    return None

                if msg.content and msg.content.lower().strip() == "cancel":
                    await interaction.followup.send("❌ Upload cancelled.", ephemeral=True)
                    return None

                if not msg.attachments:
                    await interaction.followup.send("❌ No attachment found. Upload cancelled.", ephemeral=True)
                    return None

                att = msg.attachments[0]
                try:
                    data = await att.read()
                    text = data.decode('utf-8', errors='replace')
                    msgs = [ln.strip() for ln in text.splitlines() if ln.strip()]
                    await interaction.followup.send(f"✅ Loaded **{len(msgs)}** messages from file: `{att.filename}`", ephemeral=True)
                    return msgs
                except Exception as e:
                    await interaction.followup.send(f"❌ Failed to read attachment: `{str(e)[:100]}`", ephemeral=True)
                    return None

            messages_list = []
            loaded_sources = []
            mix_selected = "mix" in choices
            
            if mix_selected:
                # Remove mix from choices and load all sources
                choices = [c for c in choices if c != "mix"]
                for ch in ["bf", "sab", "mm2"]:
                    fname = src_map.get(ch)
                    if fname:
                        try:
                            with open(fname, 'r', encoding='utf-8', errors='replace') as f:
                                loaded = [ln.strip() for ln in f.read().splitlines() if ln.strip()]
                                messages_list.extend(loaded)
                                loaded_sources.append(f"✅ {ch.upper()}: {len(loaded)} msgs from `{fname}`")
                        except FileNotFoundError:
                            loaded_sources.append(f"⚠️ {ch.upper()}: File not found (`{fname}`)")
                        except Exception as e:
                            loaded_sources.append(f"❌ {ch.upper()}: {str(e)[:50]}")
            
            # Load remaining choices
            for choice in choices:
                if choice == "custom":
                    custom_messages = await read_custom_file()
                    if custom_messages is None:
                        return
                    messages_list.extend(custom_messages)
                    loaded_sources.append(f"✅ CUSTOM: {len(custom_messages)} msgs from upload")
                else:
                    fname = src_map.get(choice)
                    if not fname:
                        continue
                    try:
                        with open(fname, 'r', encoding='utf-8', errors='replace') as f:
                            loaded = [ln.strip() for ln in f.read().splitlines() if ln.strip()]
                            messages_list.extend(loaded)
                            loaded_sources.append(f"✅ {choice.upper()}: {len(loaded)} msgs from `{fname}`")
                    except FileNotFoundError:
                        loaded_sources.append(f"⚠️ {choice.upper()}: File not found (`{fname}`)")
                    except Exception as e:
                        loaded_sources.append(f"❌ {choice.upper()}: {str(e)[:50]}")

            if not messages_list:
                status_text = "\n".join(loaded_sources) if loaded_sources else "No valid sources selected"
                return await interaction.followup.send(
                    embed=discord.Embed(color=discord.Color.red(), description=f"> ❌ No messages were loaded.\n\n{status_text}"),
                    ephemeral=True
                )

            session = sessions.get(skey(self.uid, self.stype))
            if session:
                session["messagePool"] = messages_list
            redemption = get_active_redemption(self.uid, self.stype)
            if isinstance(redemption, dict):
                redemption["messages"] = messages_list
                set_active_redemption(self.uid, self.stype, redemption)

            status_text = "\n".join(loaded_sources)
            await interaction.followup.send(
                embed=discord.Embed(
                    color=discord.Color.green(),
                    title="✅ Trade Messages Updated",
                    description=f"> Total: **{len(messages_list)}** messages loaded\n\n{status_text}"
                ),
                ephemeral=True
            )
        except Exception as e:
            tb = traceback.format_exc()
            print(f"[ChangeTradeMessagesModal:{self.uid}] Error: {e}\n{tb}")
            try:
                logs_dir = BASE_DIR / "logs"
                logs_dir.mkdir(parents=True, exist_ok=True)
                log_file = logs_dir / "modal_errors.log"
                with open(log_file, "a", encoding="utf-8") as lf:
                    lf.write(f"{datetime.now(timezone.utc).isoformat()} - ChangeTradeMessagesModal:{self.uid} - {str(e)}\n")
                    lf.write(tb + "\n\n")
            except Exception as _logexc:
                print(f"[ChangeTradeMessagesModal] Failed to write log: {_logexc}")

            try:
                await interaction.followup.send(
                    embed=discord.Embed(color=discord.Color.red(), description="> ❌ Unexpected error occurred while processing your request. The error has been logged."),
                    ephemeral=True
                )
            except Exception:
                pass

# ─── Admin View ───────────────────────────────────────────────────────────────

class AdminView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        buttons = [
            ("➕ Add Admin",        "ap_add_admin",       discord.ButtonStyle.primary,   0),
            ("➖ Remove Admin",     "ap_remove_admin",    discord.ButtonStyle.danger,    0),
            ("🔒 Restrict User",   "ap_restrict",        discord.ButtonStyle.danger,    0),
            ("🔓 Unrestrict User", "ap_unrestrict",      discord.ButtonStyle.success,   0),
            ("🛒 Add Reseller",    "ap_add_reseller",    discord.ButtonStyle.primary,   1),
            ("🗑 Remove Reseller", "ap_remove_reseller", discord.ButtonStyle.danger,    1),
            ("💰 Add Balance",     "ap_add_balance",     discord.ButtonStyle.success,   1),
            ("🗝️ Get Keys",       "ap_get_keys",        discord.ButtonStyle.secondary, 1),
            ("📦 Restock",         "ap_restock",         discord.ButtonStyle.primary,   2),
            ("⏰ Expire Key",      "ap_expire",          discord.ButtonStyle.danger,    2),
            ("↩️ Revoke Key",     "ap_revoke",          discord.ButtonStyle.secondary, 2),
        ]
        for label, custom_id, style, row in buttons:
            btn = discord.ui.Button(label=label, custom_id=custom_id, style=style, row=row)
            btn.callback = self._make_callback(custom_id)
            self.add_item(btn)

    def _make_callback(self, custom_id):
        async def callback(interaction: discord.Interaction):
            uid = str(interaction.user.id)
            if not can_manage_bot(uid):
                return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Not authorized."), ephemeral=True)
            if custom_id in ("ap_add_admin", "ap_remove_admin") and not is_owner(uid):
                return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Only the owner can use this button."), ephemeral=True)
            modal_map = {"ap_add_admin": AddAdminModal, "ap_remove_admin": RemoveAdminModal,
                         "ap_restrict": RestrictModal, "ap_unrestrict": UnrestrictModal,
                         "ap_add_reseller": AddResellerModal, "ap_remove_reseller": RemoveResellerModal,
                         "ap_expire": ExpireKeyModal, "ap_revoke": RevokeKeyModal}
            if custom_id in modal_map:
                return await interaction.response.send_modal(modal_map[custom_id]())
            if custom_id == "ap_add_balance":
                return await interaction.response.send_modal(AddBalanceModal())
            if custom_id == "ap_get_keys":
                keys   = load_keys()
                active = [(code, v) for code, v in keys.items() if not v["used"] and not is_key_expired(v)]
                if not active:
                    return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.yellow(), description="> ℹ️ No active unused keys."), ephemeral=True)
                chunks, cur = [], ""
                for code, v in active:
                    kt   = v.get("keyType", "vouch")
                    exp  = format_expiry(v.get("expiresAt"))
                    used_by = f" | Used by: <@{v['redeemedBy']}>" if v.get("used") and v.get("redeemedBy") else ""
                    count_value = v.get('tokenCount', v.get('boostCount', 'N/A'))
                    line = f"`{code}` — {TYPE_ICONS.get(kt,'🔑')} **{kt.title()}** | Tokens: **{count_value}** | Expires: {exp}{used_by}\n"
                    if len(cur + line) > 1800:
                        chunks.append(cur); cur = ""
                    cur += line
                if cur: chunks.append(cur)
                await interaction.response.defer(ephemeral=True)
                try:
                    dm = await interaction.user.create_dm()
                    for i, chunk in enumerate(chunks):
                        title = f"🗝️ Active Keys ({i+1}/{len(chunks)})" if len(chunks) > 1 else "🗝️ Active Keys"
                        await dm.send(embed=discord.Embed(color=discord.Color.green(), title=title, description=chunk))
                    await interaction.followup.send(embed=discord.Embed(color=discord.Color.green(), description=f"> ✅ **{len(active)}** key(s) sent to your DMs."), ephemeral=True)
                except discord.Forbidden:
                    lines = "\n".join(f"`{code}`" for code, _ in active[:50])
                    await interaction.followup.send(embed=discord.Embed(color=discord.Color.red(), title="❌ DMs Closed — Keys Listed Here", description=lines), ephemeral=True)
                except Exception as e:
                    await interaction.followup.send(embed=discord.Embed(color=discord.Color.red(), description=f"> ❌ Failed to send DM: `{e}`"), ephemeral=True)
            if custom_id == "ap_restock":
                return await interaction.response.send_modal(RestockModal())
        return callback

# ─── Modals ───────────────────────────────────────────────────────────────────

class ChangeChannelModal(discord.ui.Modal):
    def __init__(self, uid, stype):
        super().__init__(title="Change Channel"); self.uid = uid; self.stype = stype
        self.add_item(discord.ui.InputText(custom_id="new_channel_id", label="New Channel ID", style=discord.InputTextStyle.short, required=True))
    async def callback(self, interaction: discord.Interaction):
        session = sessions.get(skey(self.uid, self.stype))
        new_channel = self.children[0].value.strip()
        if session:
            session["channelId"] = new_channel
            await interaction.response.send_message(embed=discord.Embed(color=discord.Color.green(), description=f"> ✅ Channel updated to <#{session['channelId']}>."), ephemeral=True)
            return

        # If session not in memory, update active redemption JSON if present
        redemption = get_active_redemption(self.uid, self.stype)
        if redemption and isinstance(redemption, dict):
            redemption["channelId"] = new_channel
            set_active_redemption(self.uid, self.stype, redemption)
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.green(), description=f"> ✅ Channel updated in active redemption to <#{new_channel}>."), ephemeral=True)

        return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ No active session."), ephemeral=True)


class ChangeUserIdModal(discord.ui.Modal):
    def __init__(self, uid):
        super().__init__(title="Change Vouching Target"); self.uid = uid
        self.add_item(discord.ui.InputText(custom_id="new_user_id", label="New User ID to vouch for", style=discord.InputTextStyle.short, required=True))
    async def callback(self, interaction: discord.Interaction):
        session = sessions.get(skey(self.uid, "vouch"))
        new_id = self.children[0].value.strip()
        if session:
            session["targetUserId"] = new_id
            await interaction.response.send_message(embed=discord.Embed(color=discord.Color.green(), description=f"> ✅ Now vouching for <@{session['targetUserId']}>."), ephemeral=True)
            return

        # If session not in memory, update redemption JSON if present
        redemption = get_active_redemption(self.uid, "vouch")
        if redemption and isinstance(redemption, dict):
            redemption["targetUserId"] = new_id
            set_active_redemption(self.uid, "vouch", redemption)
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.green(), description=f"> ✅ Updated vouch target in active redemption to <@{new_id}>."), ephemeral=True)

        return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ No active vouch session."), ephemeral=True)


class AddAdminModal(discord.ui.Modal):
    def __init__(self): super().__init__(title="Add Admin"); self.add_item(discord.ui.InputText(custom_id="user_id", label="User ID to add as Admin", style=discord.InputTextStyle.short, placeholder="Discord User ID", required=True))
    async def callback(self, interaction: discord.Interaction):
        t = self.children[0].value.strip()
        if line_exists(ADMINS_FILE, t): return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.yellow(), description=f"> ⚠️ <@{t}> is already an admin."), ephemeral=True)
        append_line(ADMINS_FILE, t)
        await interaction.response.send_message(embed=discord.Embed(color=discord.Color.green(), description=f"> ✅ <@{t}> added as **Admin**."), ephemeral=True)


class RemoveAdminModal(discord.ui.Modal):
    def __init__(self): super().__init__(title="Remove Admin"); self.add_item(discord.ui.InputText(custom_id="user_id", label="User ID to remove from Admins", style=discord.InputTextStyle.short, placeholder="Discord User ID", required=True))
    async def callback(self, interaction: discord.Interaction):
        t = self.children[0].value.strip()
        if not line_exists(ADMINS_FILE, t): return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description=f"> ❌ <@{t}> is not an admin."), ephemeral=True)
        remove_line(ADMINS_FILE, t)
        await interaction.response.send_message(embed=discord.Embed(color=discord.Color.green(), description=f"> ✅ <@{t}> removed from Admins."), ephemeral=True)


class RestrictModal(discord.ui.Modal):
    def __init__(self): super().__init__(title="Restrict User"); self.add_item(discord.ui.InputText(custom_id="user_id", label="User ID to restrict", style=discord.InputTextStyle.short, placeholder="Discord User ID", required=True))
    async def callback(self, interaction: discord.Interaction):
        t = self.children[0].value.strip()
        if line_exists(RESTRICTED_FILE, t): return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.yellow(), description=f"> ⚠️ <@{t}> is already restricted."), ephemeral=True)
        append_line(RESTRICTED_FILE, t)
        await interaction.response.send_message(embed=discord.Embed(color=discord.Color.green(), description=f"> ✅ <@{t}> restricted."), ephemeral=True)


class UnrestrictModal(discord.ui.Modal):
    def __init__(self): super().__init__(title="Unrestrict User"); self.add_item(discord.ui.InputText(custom_id="user_id", label="User ID to unrestrict", style=discord.InputTextStyle.short, placeholder="Discord User ID", required=True))
    async def callback(self, interaction: discord.Interaction):
        t = self.children[0].value.strip()
        if not line_exists(RESTRICTED_FILE, t): return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description=f"> ❌ <@{t}> is not restricted."), ephemeral=True)
        remove_line(RESTRICTED_FILE, t)
        await interaction.response.send_message(embed=discord.Embed(color=discord.Color.green(), description=f"> ✅ <@{t}> unrestricted."), ephemeral=True)


class AddResellerModal(discord.ui.Modal):
    def __init__(self): super().__init__(title="Add Reseller"); self.add_item(discord.ui.InputText(custom_id="user_id", label="User ID to add as Reseller", style=discord.InputTextStyle.short, placeholder="Discord User ID", required=True))
    async def callback(self, interaction: discord.Interaction):
        t = self.children[0].value.strip()
        if line_exists(RESELLERS_FILE, t): return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.yellow(), description=f"> ⚠️ <@{t}> is already a reseller."), ephemeral=True)
        append_line(RESELLERS_FILE, t)
        await interaction.response.send_message(embed=discord.Embed(color=discord.Color.green(), description=f"> ✅ <@{t}> added as **Reseller**. ($3 per key)"), ephemeral=True)


class RemoveResellerModal(discord.ui.Modal):
    def __init__(self): super().__init__(title="Remove Reseller"); self.add_item(discord.ui.InputText(custom_id="user_id", label="User ID to remove from Resellers", style=discord.InputTextStyle.short, placeholder="Discord User ID", required=True))
    async def callback(self, interaction: discord.Interaction):
        t = self.children[0].value.strip()
        if not line_exists(RESELLERS_FILE, t): return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description=f"> ❌ <@{t}> is not a reseller."), ephemeral=True)
        remove_line(RESELLERS_FILE, t)
        await interaction.response.send_message(embed=discord.Embed(color=discord.Color.green(), description=f"> ✅ <@{t}> removed from Resellers."), ephemeral=True)


class AddBalanceModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Add Balance")
        self.add_item(discord.ui.InputText(custom_id="user_id", label="Reseller User ID",                     style=discord.InputTextStyle.short, placeholder="Discord User ID",         required=True))
        self.add_item(discord.ui.InputText(custom_id="amount",  label="Balance to set (e.g. 5, 7, infinite)", style=discord.InputTextStyle.short, placeholder="5 | 7 | 10 | infinite",  required=True))
    async def callback(self, interaction: discord.Interaction):
        t       = self.children[0].value.strip()
        amt_raw = self.children[1].value.strip().lower().replace("$", "")
        if amt_raw == "infinite": new_bal = "infinite"
        else:
            try:
                parsed = float(amt_raw)
                if parsed < 0: raise ValueError
            except Exception:
                return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Invalid amount."), ephemeral=True)
            cur = get_balance(t); new_bal = "infinite" if cur == "infinite" else (cur + parsed)
        set_balance(t, new_bal)
        await interaction.response.send_message(embed=discord.Embed(color=discord.Color.green(), description=f"> ✅ Balance updated for <@{t}>.\n> New balance: **{format_balance(new_bal)}**"), ephemeral=True)


class RestockModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Restock Tokens")
        self.add_item(discord.ui.InputText(custom_id="tokens", label="Tokens to add (one per line)", style=discord.InputTextStyle.paragraph, placeholder="Paste tokens here, one per line", required=True))
    async def callback(self, interaction: discord.Interaction):
        token_list = [t.strip() for t in self.children[0].value.split("\n") if t.strip()]
        if not token_list:
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ No tokens provided."), ephemeral=True)
        for token in token_list: append_line(TOKENS_FILE, token)
        await interaction.response.send_message(embed=discord.Embed(color=discord.Color.green(), title="📦 Restock Complete", description=f"> ✅ **{len(token_list)}** token(s) added."), ephemeral=True)


class ExpireKeyModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Expire Key")
        self.add_item(discord.ui.InputText(custom_id="user_id",  label="User ID whose key to expire",          style=discord.InputTextStyle.short, placeholder="Discord User ID",           required=True))
        self.add_item(discord.ui.InputText(custom_id="key_type", label="Key type (vouch/chat/trade/all)",       style=discord.InputTextStyle.short, placeholder="vouch | chat | trade | all",required=True))
    async def callback(self, interaction: discord.Interaction):
        t      = self.children[0].value.strip(); kt_raw = self.children[1].value.strip().lower()
        types  = list(SESSION_TYPES) if kt_raw == "all" else ([kt_raw] if kt_raw in SESSION_TYPES else None)
        if not types:
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Type must be `vouch`, `chat`, `trade` or `all`."), ephemeral=True)
        keys = load_keys(); expired_any = False
        for stype in types:
            redemption = get_active_redemption(t, stype)
            if redemption:
                # extract key code from redemption structure
                key_code = redemption if isinstance(redemption, str) else redemption.get("key")
                stop_session(t, stype)
                if key_code:
                    keys.pop(key_code, None)
                clear_active_redemption(t, stype)
                expired_any = True
        save_keys(keys)
        if not expired_any:
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description=f"> ❌ No active **{kt_raw}** key for <@{t}>."), ephemeral=True)
        await interaction.response.send_message(embed=discord.Embed(color=discord.Color.green(), description=f"> ✅ **{kt_raw.title()}** key(s) expired for <@{t}>."), ephemeral=True)


class RevokeKeyModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Revoke Key")
        self.add_item(discord.ui.InputText(custom_id="user_id",  label="User ID whose key to revoke",          style=discord.InputTextStyle.short, placeholder="Discord User ID",           required=True))
        self.add_item(discord.ui.InputText(custom_id="key_type", label="Key type (vouch/chat/trade/all)",       style=discord.InputTextStyle.short, placeholder="vouch | chat | trade | all",required=True))
    async def callback(self, interaction: discord.Interaction):
        t      = self.children[0].value.strip(); kt_raw = self.children[1].value.strip().lower()
        types  = list(SESSION_TYPES) if kt_raw == "all" else ([kt_raw] if kt_raw in SESSION_TYPES else None)
        if not types:
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Type must be `vouch`, `chat`, `trade` or `all`."), ephemeral=True)
        keys = load_keys(); revoked_any = False
        for stype in types:
            redemption = get_active_redemption(t, stype)
            if redemption:
                key_code = redemption if isinstance(redemption, str) else redemption.get("key")
                stop_session(t, stype)
                if key_code and keys.get(key_code):
                    keys[key_code]["used"] = False; keys[key_code].pop("redeemedBy", None); keys[key_code].pop("redeemedAt", None)
                clear_active_redemption(t, stype); revoked_any = True
        save_keys(keys)
        if not revoked_any:
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description=f"> ❌ No active **{kt_raw}** key for <@{t}>."), ephemeral=True)
        await interaction.response.send_message(embed=discord.Embed(color=discord.Color.green(), description=f"> ✅ **{kt_raw.title()}** key(s) revoked from <@{t}> and are reusable."), ephemeral=True)


class GenerateKeyModal(discord.ui.Modal):
    def __init__(self, uid):
        super().__init__(title="Generate Key"); self.uid = uid
        self.add_item(discord.ui.InputText(custom_id="key_type",    label="Key Type (vouch, chat, trade, vc or reacts)",     style=discord.InputTextStyle.short, placeholder="vouch | chat | trade | vc | reacts", required=True))
        self.add_item(discord.ui.InputText(custom_id="token_count", label="How many tokens does this key use?",  style=discord.InputTextStyle.short, placeholder="e.g. 10",             required=True))
        self.add_item(discord.ui.InputText(custom_id="expires_in",  label="Expires in (1d, 7d, 1w, 1m, never)", style=discord.InputTextStyle.short, placeholder="1d | 1w | 1m | never", required=True))
    async def callback(self, interaction: discord.Interaction):
        uid      = str(interaction.user.id)
        key_type = self.children[0].value.strip().lower()
        if key_type not in SESSION_TYPES:
            return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> ❌ Key type must be `vouch`, `chat`, `trade`, `vc` or `reacts`."), ephemeral=True)
        try:
            token_count = int(self.children[1].value)
            if token_count < 1: raise ValueError
        except Exception:
            return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> ❌ Invalid token count."), ephemeral=True)
        expires_in = self.children[2].value.strip()
        if expires_in.lower() != "never" and not parse_expiry(expires_in):
            return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> ❌ Invalid expiry. Use `1d`, `7d`, `1w`, `1m`, or `never`."), ephemeral=True)
        all_tokens = get_tokens()
        if len(all_tokens) < token_count:
            return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description=f"> ❌ Not enough tokens. Need **{token_count}**, only **{len(all_tokens)}** available."), ephemeral=True)
        is_reseller_only = is_reseller(uid) and not is_owner(uid) and not is_admin(uid)
        if is_reseller_only and not deduct_balance(uid):
            return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> ❌ Insufficient balance ($3 required)."), ephemeral=True)
        key = generate_key()
        expires_at = parse_expiry(expires_in)
        keys = load_keys()
        keys[key] = {"keyType": key_type, "tokenCount": token_count, "expiresAt": expires_at, "used": False,
                     "createdBy": uid, "createdAt": datetime.now(timezone.utc).isoformat()}
        save_keys(keys)
        embed = (discord.Embed(color=discord.Color.green(), title="🔑 Key Generated")
                 .add_field(name="Key",     value=f"```{key}```")
                 .add_field(name="Type",    value=f"{TYPE_ICONS[key_type]} {key_type.title()}", inline=True)
                 .add_field(name="Tokens",  value=str(token_count),                             inline=True)
                 .add_field(name="Expires", value=format_expiry(expires_at),                    inline=True)
                 .set_footer(text=f"Redeem with /{key_type}"))
        if is_reseller_only: embed.description = f"> 💰 Remaining balance: **{format_balance(get_balance(uid))}**"
        await safe_send_message(interaction, embed=embed, ephemeral=True)


class GenerateAdvKeyModal(discord.ui.Modal):
    def __init__(self, uid):
        super().__init__(title="Generate Auto Adv Key"); self.uid = uid
        self.add_item(discord.ui.InputText(custom_id="slots",    label="Number of account slots",               style=discord.InputTextStyle.short,     placeholder="How many accounts can run (e.g. 3)", required=True))
        self.add_item(discord.ui.InputText(custom_id="dm_reply", label="Enable Auto DM Reply? (yes / no)",      style=discord.InputTextStyle.short,     placeholder="yes | no  (leave blank = no)",        required=False))
        self.add_item(discord.ui.InputText(custom_id="expires",  label="Expires in (1d, 7d, 1w, 1m, never)",   style=discord.InputTextStyle.short,     placeholder="1d | 1w | 1m | never",               required=True))
    async def callback(self, interaction: discord.Interaction):
        uid = str(interaction.user.id)
        try:
            slots = int(self.children[0].value.strip())
            if slots < 1 or slots > 50: raise ValueError
        except Exception:
            return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> ❌ Slots must be a number between 1 and 50."), ephemeral=True)
        dm_reply_raw = self.children[1].value.strip().lower()
        allow_dm   = dm_reply_raw in ("yes", "y", "true", "1")
        expires_in = self.children[2].value.strip()
        if expires_in.lower() != "never" and not parse_expiry(expires_in):
            return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> ❌ Invalid expiry. Use `1d`, `7d`, `1w`, `1m`, or `never`."), ephemeral=True)
        is_reseller_only = is_reseller(uid) and not is_owner(uid) and not is_admin(uid)
        if is_reseller_only and not deduct_balance(uid):
            return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> ❌ Insufficient balance ($3 required)."), ephemeral=True)
        key = generate_key()
        expires_at = parse_expiry(expires_in)
        keys = load_keys()
        keys[key] = {"keyType": "autoadv", "slots": slots, "allowDmReply": allow_dm,
                     "expiresAt": expires_at, "used": False,
                     "createdBy": uid, "createdAt": datetime.now(timezone.utc).isoformat()}
        save_keys(keys)
        embed = (discord.Embed(color=discord.Color.green(), title="📢 Auto Adv Key Generated")
                 .add_field(name="Key",      value=f"```{key}```")
                 .add_field(name="Slots",     value=str(slots),                                    inline=True)
                 .add_field(name="DM Reply",  value="✅ Enabled" if allow_dm else "❌ Disabled",   inline=True)
                 .add_field(name="Expires",   value=format_expiry(expires_at),                    inline=True)
                 .set_footer(text="Redeem with /autoadv"))
        if is_reseller_only: embed.description = f"> 💰 Remaining balance: **{format_balance(get_balance(uid))}**"
        await safe_send_message(interaction, embed=embed, ephemeral=True)

# ─── Shared redeem logic — tokens auto-join via invite then start session ─────

async def run_redeem(interaction, uid, key, invite_input, channel_id, delay_seconds, target_user_id, expected_type, emoji=None, message_id=None, duration_seconds=3600, max_retries=5, messages_list=None):
    invite_code = extract_invite_code(invite_input)
    if not invite_code:
        return await safe_send_message(
            interaction,
            embed=discord.Embed(color=discord.Color.red(), description="> ❌ Invalid invite link or code."), ephemeral=True)

    keys = load_keys()
    lookup_key, _ = find_key_entry(keys, key)
    if not lookup_key:
        return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> ❌ Invalid key."), ephemeral=True)
    key = lookup_key
    if keys[key]["used"]:
        return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> ❌ This key has already been redeemed."), ephemeral=True)
    if is_key_expired(keys[key]):
        return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description=f"> ❌ This key expired {format_expiry(keys[key].get('expiresAt'))}."), ephemeral=True)
    key_type = keys[key].get("keyType", "vouch")
    if key_type != expected_type:
        return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description=f"> ❌ This is a **{key_type}** key. Use `/{key_type}` to redeem it."), ephemeral=True)

    token_count = keys[key]["tokenCount"]
    all_tokens  = get_tokens()
    if len(all_tokens) < token_count:
        return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description=f"> ❌ Not enough tokens. Need **{token_count}**, only **{len(all_tokens)}** available."), ephemeral=True)

    guild_id = await resolve_invite_to_guild(invite_code)
    if not guild_id:
        return await safe_send_message(
            interaction,
            embed=discord.Embed(color=discord.Color.red(), description="> ❌ Could not resolve the invite. Make sure it's valid and not expired."), ephemeral=True)

    # For reacts type, channel_id is the channel, message_id is the message
    react_message_id = None
    if expected_type == "reacts":
        react_message_id = message_id

    keys[key]["used"] = True
    keys[key]["redeemedBy"] = uid
    keys[key]["redeemedAt"] = datetime.now(timezone.utc).isoformat()
    save_keys(keys)
    # Choose tokens for this redemption and save richer redemption metadata so /manage can act on it later
    selected_tokens = all_tokens[:token_count]
    redemption_meta = {
        "key": key,
        "tokenCount": token_count,
        "tokens": selected_tokens,
        "duration_seconds": duration_seconds,
        "expiresAt": keys[key].get("expiresAt"),
        "messages": messages_list,
        "channelId": channel_id,
        "delayMs": int(delay_seconds * 1000),
        "delaySeconds": delay_seconds,
        "delay_seconds": delay_seconds,
        "targetUserId": target_user_id,
        "messageId": message_id,
        "emoji": emoji,
        "guildId": guild_id,
        "maxRetries": max_retries
    }
    set_active_redemption(uid, expected_type, redemption_meta)
    icon            = TYPE_ICONS[expected_type]
    type_label      = TYPE_LABELS[expected_type]

    await safe_send_message(
        interaction,
        embed=discord.Embed(
            color=discord.Color.yellow(),
            title=f"🔑 {icon} {type_label} Key Redeemed!",
            description=f"> **Phase 1/2:** Joining **{token_count}** tokens to the server...\n> Invite: `discord.gg/{invite_code}`"
        ),
        ephemeral=True
    )

    joined_count  = 0
    joined_tokens = []

    for i, token in enumerate(selected_tokens):
        if joined_count >= token_count:
            break

        r = await join_server_with_token(token, guild_id)
        if r["success"]:
            joined_count += 1
            joined_tokens.append(token)

        status_str = (
            "✅ joined" if r["success"] and not r.get("alreadyIn") else
            "↩️ already in server" if r.get("alreadyIn") else
            f"❌ {r.get('reason', 'failed')}"
        )
        await safe_edit_message(
            interaction,
            embed=discord.Embed(
                color=discord.Color.yellow(),
                description=(
                    f"> **Phase 1/2: Joining tokens...**\n"
                    f"> **{joined_count}**/**{token_count}** ready\n"
                    f"> Last: **{r['username']}** — {status_str}"
                )
            )
        )
        if joined_count < token_count:
            await asyncio.sleep(1.5)

    if joined_count == 0:
        keys = load_keys()
        if keys.get(key):
            keys[key]["used"] = False
            keys[key].pop("redeemedBy", None)
            keys[key].pop("redeemedAt", None)
            save_keys(keys)
        clear_active_redemption(uid, expected_type)
        return await safe_edit_message(
            interaction,
            embed=discord.Embed(
                color=discord.Color.red(),
                title="❌ Join Failed",
                description="> No tokens could join the server.\n> **Your key has been reset** — you can try redeeming again.\n> Make sure the invite link is valid and the bot has permission to add members."
            )
        )

    if expected_type == "vc":
        # Parse voice channel ID (supports both direct ID and Discord link)
        vc_channel_id = parse_channel_id(channel_id)
        if not vc_channel_id:
            keys = load_keys()
            if keys.get(key):
                keys[key]["used"] = False
                keys[key].pop("redeemedBy", None)
                keys[key].pop("redeemedAt", None)
                save_keys(keys)
            clear_active_redemption(uid, expected_type)
            return await safe_edit_message(
                interaction,
                embed=discord.Embed(
                    color=discord.Color.red(),
                    title="❌ Invalid Voice Channel ID",
                    description="> The channel ID is invalid.\n> Please provide just the channel ID (right-click > Copy ID)\n> Or provide a full Discord channel link"
                )
            )
        
        vc_guild_id = guild_id  # Voice channel must be in the same guild as the server invite
        
        # Give Discord time to add users to the guild and replicate state
        print(f"[VC Redeem:{uid}] Waiting for guild membership to replicate...")
        await asyncio.sleep(3)
        
        # Verify all tokens are in the guild before attempting voice join
        print(f"[VC Redeem:{uid}] Verifying {len(joined_tokens)} tokens are in guild...")
        verified_tokens = []
        for attempt in range(3):  # Up to 3 attempts with backoff
            for token in joined_tokens:
                if token in verified_tokens:
                    continue  # Already verified
                in_guild, user_id = await verify_token_in_guild(token, vc_guild_id)
                if in_guild:
                    verified_tokens.append(token)
                    print(f"[VC Redeem:{uid}] ✓ Token verified in guild (attempt {attempt + 1})")
            
            if len(verified_tokens) == len(joined_tokens):
                print(f"[VC Redeem:{uid}] All {len(verified_tokens)} tokens verified in guild!")
                break
            
            if attempt < 2:
                wait_time = 2 ** (attempt + 1)  # Exponential: 4, 8 seconds
                remaining = len(joined_tokens) - len(verified_tokens)
                print(f"[VC Redeem:{uid}] Waiting {wait_time}s before retry... ({len(verified_tokens)}/{len(joined_tokens)} verified, {remaining} remaining)")
                await asyncio.sleep(wait_time)
        
        if not verified_tokens:
            print(f"[VC Redeem:{uid}] ERROR: No tokens could be verified in guild")
            await safe_edit_message(
                interaction,
                embed=discord.Embed(
                    color=discord.Color.red(),
                    title="❌ Token Verification Failed",
                    description="> Tokens could not be verified in the guild.\n> Make sure the server invite is valid and accepting new members."
                )
            )
            clear_active_redemption(uid, expected_type)
            return
        
        # Try voice join on verified tokens with full retry logic
        print(f"[VC Redeem:{uid}] Attempting to join {len(verified_tokens)} tokens to voice channel {vc_channel_id}...")
        await safe_edit_message(
            interaction,
            embed=discord.Embed(
                color=discord.Color.yellow(),
                title="🔊 Joining Voice Channel...",
                description=f"> Connecting **{len(verified_tokens)}** tokens to the voice channel...\n> This may take a moment..."
            )
        )
        
        voice_ready_tokens = []
        active_connections = []

        for i, token in enumerate(verified_tokens):
            print(f"[VC Redeem:{uid}] [{i+1}/{len(verified_tokens)}] Joining token to voice channel...")

            # Use retry logic in join_voice_channel_with_token
            result = await join_voice_channel_with_token(token, vc_guild_id, vc_channel_id, max_attempts=3)
            
            if result["success"]:
                voice_ready_tokens.append(token)
                # Store connection info to keep it alive
                connection_info = {
                    "voice_ws": result.get("voice_ws"),
                    "gateway_ws": result.get("gateway_ws"),
                    "heartbeat_task": result.get("heartbeat_task"),
                    "voice_heartbeat_task": result.get("voice_heartbeat_task"),
                    "guild_id": vc_guild_id,
                    "channel_id": vc_channel_id,
                    "joined_at": datetime.now(timezone.utc).isoformat()
                }
                active_connections.append(connection_info)
                
                # Store in global connections dict
                if uid not in ACTIVE_VOICE_CONNECTIONS:
                    ACTIVE_VOICE_CONNECTIONS[uid] = {}
                ACTIVE_VOICE_CONNECTIONS[uid][token] = connection_info
                
                print(f"[VC Redeem:{uid}] ✓ Token {i+1} joined voice successfully")
                
                # Update progress message
                await safe_edit_message(
                    interaction,
                    embed=discord.Embed(
                        color=discord.Color.yellow(),
                        title="🔊 Joining Voice Channel...",
                        description=f"> **{len(voice_ready_tokens)}/{len(verified_tokens)}** tokens connected\n> Connecting remaining tokens..."
                    )
                )

                # Brief pause between joins to avoid rate limits
                if i < len(verified_tokens) - 1:
                    await asyncio.sleep(1)
            else:
                print(f"[VC Redeem:{uid}] ✗ Token {i+1} failed: {result.get('reason')}")

        # Show final result
        if voice_ready_tokens:
            print(f"[VC Redeem:{uid}] ✓✓✓ SUCCESS! {len(voice_ready_tokens)}/{len(verified_tokens)} tokens connected")
            await safe_edit_message(
                interaction,
                embed=discord.Embed(
                    color=discord.Color.green(),
                    title="✅ Voice Channel Joined!",
                    description=f"> **{len(voice_ready_tokens)}** out of **{len(verified_tokens)}** tokens connected\n> They will stay in the voice channel until disconnected\n> Use `/vcstop` to disconnect them"
                )
            )
        else:
            print(f"[VC Redeem:{uid}] ✗✗✗ FAILED: No tokens could join voice channel")
            
            # Reset the key since the redemption failed
            keys = load_keys()
            if keys.get(key):
                keys[key]["used"] = False
                keys[key].pop("redeemedBy", None)
                keys[key].pop("redeemedAt", None)
                save_keys(keys)
                print(f"[VC Redeem:{uid}] Key reset - user can try redeeming again")
            
            await safe_edit_message(
                interaction,
                embed=discord.Embed(
                    color=discord.Color.red(),
                    title="❌ Voice Join Failed",
                    description="> No tokens could join the voice channel.\n> **Your key has been reset** — you can try redeeming again.\n> Make sure the channel ID is correct and is a voice channel."
                )
            )
            clear_active_redemption(uid, expected_type)
            return
        
        joined_tokens = voice_ready_tokens
        channel_id = vc_channel_id  # Update for session

    sessions[skey(uid, expected_type)] = {
        "type": expected_type,
        "tokens": joined_tokens,
        "guildId": guild_id,
        "channelId": channel_id,
        "messageId": react_message_id,
        "emoji": emoji,
        "targetUserId": target_user_id,
        "messagePool": messages_list if messages_list else None,
        "delayMs": delay_seconds * 1000,
        "running": True,
        "tokenIndex": 0,
        "totalSent": 0,
        "totalConnected": 0,
        "totalAttempts": 0,
        "tokenUserIds": {},
        "lastMessage": "",
        "durationSeconds": duration_seconds if expected_type == "vc" else None,
        "maxRetries": max_retries if expected_type == "vc" else None,
        "startTime": datetime.now(timezone.utc) if expected_type == "vc" else None,
        "status": "running",
    }
    persist_running_state()

    if expected_type != "vc" and joined_tokens:
        await start_presence_for_tokens(joined_tokens)

    if expected_type == "vouch":
        asyncio.create_task(vouch_loop(uid))
        final_embed = (
            discord.Embed(color=discord.Color.green(), title="✅ Auto Vouch Started!",
                          description="> Tokens will vouch indefinitely. Use `/manage` to control.")
            .add_field(name="Tokens Joined", value=f"{joined_count}/{token_count}", inline=True)
            .add_field(name="Vouching For",  value=f"<@{target_user_id}>",          inline=True)
            .add_field(name="Channel",       value=f"<#{channel_id}>",              inline=True)
            .add_field(name="Delay",         value=f"{delay_seconds}s",             inline=True)
        )
    elif expected_type == "vc":
        asyncio.create_task(vc_loop(uid))
        duration_display = "Infinite" if duration_seconds == 0 else f"{int(duration_seconds)}s"
        retry_display = f"Max {max_retries}" if max_retries > 0 else "Unlimited"
        final_embed = (
            discord.Embed(color=discord.Color.green(), title="✅ Auto VC Started!",
                          description="> Tokens intelligently reconnect to voice channel. Use `/manage` to control.")
            .add_field(name="Tokens Joined", value=f"{joined_count}/{token_count}", inline=True)
            .add_field(name="Voice Channel", value=f"<#{channel_id}>",              inline=True)
            .add_field(name="Delay",         value=f"{delay_seconds}s",             inline=True)
            .add_field(name="Duration",      value=duration_display,                inline=True)
            .add_field(name="Retries/Token", value=retry_display,                   inline=True)
        )
    elif expected_type == "reacts":
        asyncio.create_task(react_loop(uid))
        final_embed = (
            discord.Embed(color=discord.Color.green(), title="✅ Auto Reacts Completed!",
                          description="> Tokens have reacted to the message.")
            .add_field(name="Tokens Joined", value=f"{joined_count}/{token_count}", inline=True)
            .add_field(name="Channel",       value=f"<#{channel_id}>",              inline=True)
            .add_field(name="Message ID",    value=f"{react_message_id}",           inline=True)
        )
    else:
        # start appropriate loop
        asyncio.create_task(text_loop(uid, expected_type))
        titles = {"chat": "✅ Auto Chat Started!", "trade": "✅ Auto Trade Started!"}
        final_embed = (
            discord.Embed(color=discord.Color.green(), title=titles[expected_type],
                          description="> Tokens will send messages indefinitely. Use `/manage` to control.")
            .add_field(name="Tokens Joined", value=f"{joined_count}/{token_count}", inline=True)
            .add_field(name="Channel",       value=f"<#{channel_id}>",              inline=True)
            .add_field(name="Delay",         value=f"{delay_seconds}s",             inline=True)
        )

    await safe_edit_message(interaction, embed=final_embed)


# ─── Redeem modals (use invite link/code instead of server ID) ───────────────

class VouchRedeemModal(discord.ui.Modal):
    def __init__(self, uid):
        super().__init__(title="Redeem Vouch Key"); self.uid = uid
        self.add_item(discord.ui.InputText(custom_id="key",        label="Your Key",                        style=discord.InputTextStyle.short, placeholder="Paste your key",                         required=True))
        self.add_item(discord.ui.InputText(custom_id="invite",     label="Server Invite Link or Code",      style=discord.InputTextStyle.short, placeholder="discord.gg/xxx or just the code",        required=True))
        self.add_item(discord.ui.InputText(custom_id="channel_id", label="Vouch Channel ID",                style=discord.InputTextStyle.short, placeholder="Channel where vouches are sent",         required=True))
        self.add_item(discord.ui.InputText(custom_id="user_id",    label="User ID to vouch for",            style=discord.InputTextStyle.short, placeholder="Discord User ID receiving vouches",      required=True))
        self.add_item(discord.ui.InputText(custom_id="delay",      label="Delay between vouches (seconds)", style=discord.InputTextStyle.short, placeholder="e.g. 3",                                required=True))
    async def callback(self, interaction: discord.Interaction):
        uid        = str(interaction.user.id)
        key        = self.children[0].value.strip().upper()
        invite     = self.children[1].value.strip()
        channel_id = self.children[2].value.strip()
        user_id    = self.children[3].value.strip()
        try:
            delay = float(self.children[4].value)
            if delay < 1: raise ValueError
        except Exception:
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Delay must be at least 1 second."), ephemeral=True)
        await run_redeem(interaction, uid, key, invite, channel_id, delay, user_id, "vouch")


class ChatRedeemModal(discord.ui.Modal):
    def __init__(self, uid):
        super().__init__(title="Redeem Chat Key"); self.uid = uid
        self.add_item(discord.ui.InputText(custom_id="key",        label="Your Key",                         style=discord.InputTextStyle.short, placeholder="Paste your key",                        required=True))
        self.add_item(discord.ui.InputText(custom_id="invite",     label="Server Invite Link or Code",       style=discord.InputTextStyle.short, placeholder="discord.gg/xxx or just the code",       required=True))
        self.add_item(discord.ui.InputText(custom_id="channel_id", label="Chat Channel ID",                  style=discord.InputTextStyle.short, placeholder="Channel where messages are sent",        required=True))
        self.add_item(discord.ui.InputText(custom_id="delay",      label="Delay between messages (seconds)", style=discord.InputTextStyle.short, placeholder="e.g. 5",                                required=True))
    async def callback(self, interaction: discord.Interaction):
        uid        = str(interaction.user.id)
        key        = self.children[0].value.strip().upper()
        invite     = self.children[1].value.strip()
        channel_id = self.children[2].value.strip()
        try:
            delay = float(self.children[3].value)
            if delay < 1: raise ValueError
        except Exception:
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Delay must be at least 1 second."), ephemeral=True)
        await run_redeem(interaction, uid, key, invite, channel_id, delay, None, "chat")


class TradeRedeemModal(discord.ui.Modal):
    def __init__(self, uid):
        super().__init__(title="Redeem Trade Key"); self.uid = uid
        self.add_item(discord.ui.InputText(custom_id="key",        label="Your Key",                         style=discord.InputTextStyle.short, placeholder="Paste your key",                        required=True))
        self.add_item(discord.ui.InputText(custom_id="invite",     label="Server Invite Link or Code",       style=discord.InputTextStyle.short, placeholder="discord.gg/xxx or just the code",       required=True))
        self.add_item(discord.ui.InputText(custom_id="channel_id", label="Trade Channel ID",                 style=discord.InputTextStyle.short, placeholder="Channel where trade messages are sent",  required=True))
        self.add_item(discord.ui.InputText(custom_id="delay",      label="Delay between messages (seconds)", style=discord.InputTextStyle.short, placeholder="e.g. 5",                                required=True))
        self.add_item(discord.ui.InputText(custom_id="opt1",       label="Source 1",                       style=discord.InputTextStyle.short, placeholder="bloxfruits | sab | mm2 | exchanges | custom", required=False))
        self.add_item(discord.ui.InputText(custom_id="opt2",       label="Source 2",                       style=discord.InputTextStyle.short, placeholder="bloxfruits | sab | mm2 | exchanges | custom", required=False))
        self.add_item(discord.ui.InputText(custom_id="opt3",       label="Source 3",                       style=discord.InputTextStyle.short, placeholder="bloxfruits | sab | mm2 | exchanges | custom", required=False))
    async def callback(self, interaction: discord.Interaction):
        uid        = str(interaction.user.id)
        key        = self.children[0].value.strip().upper()
        invite     = self.children[1].value.strip()
        channel_id = self.children[2].value.strip()
        try:
            delay = float(self.children[3].value)
            if delay < 1: raise ValueError
        except Exception:
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Delay must be at least 1 second."), ephemeral=True)

        opts = [self.children[i].value.strip().lower() for i in (4, 5, 6) if self.children[i].value and self.children[i].value.strip()]
        valid_choices = {"bloxfruits", "sab", "mm2", "exchanges", "custom"}
        choices = [opt for opt in opts if opt in valid_choices]
        invalid = [opt for opt in opts if opt not in valid_choices]
        if invalid:
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description=f"> ❌ Invalid source(s): {', '.join(invalid)}. Available choices: bloxfruits, sab, mm2, exchanges, custom."), ephemeral=True)

        messages_list = []
        src_map = {
            "exchanges": "exchanges.txt",
            "bloxfruits": "bloxfruits.txt",
            "sab": "sab.txt",
            "mm2": "mm2.txt",
        }

        async def read_custom_file():
            await interaction.followup.send("Please upload a plain text file (one message per line) in this channel or DM me within 5 minutes. Reply `cancel` to abort.", ephemeral=True)

            def check(m: discord.Message):
                return m.author.id == interaction.user.id and (
                    m.channel == interaction.channel or isinstance(m.channel, discord.DMChannel)
                ) and (len(m.attachments) > 0 or (m.content and m.content.lower().strip() == "cancel"))

            try:
                msg = await bot.wait_for('message', check=check, timeout=300)
            except asyncio.TimeoutError:
                await interaction.followup.send("Timed out — no file received.", ephemeral=True)
                return None

            if msg.content and msg.content.lower().strip() == "cancel":
                await interaction.followup.send("Upload cancelled.", ephemeral=True)
                return None

            if not msg.attachments:
                await interaction.followup.send("No attachment found. Upload cancelled.", ephemeral=True)
                return None

            att = msg.attachments[0]
            try:
                data = await att.read()
                text = data.decode('utf-8', errors='replace')
                return [ln.strip() for ln in text.splitlines() if ln.strip()]
            except Exception:
                await interaction.followup.send("Failed to read attachment; ensure it's a text file.", ephemeral=True)
                return None

        for choice in choices:
            if choice == "custom":
                custom_messages = await read_custom_file()
                if custom_messages is None:
                    return
                messages_list.extend(custom_messages)
            else:
                fname = src_map.get(choice)
                if not fname:
                    continue
                try:
                    with open(fname, 'r', encoding='utf-8', errors='replace') as f:
                        messages_list.extend([ln.strip() for ln in f.read().splitlines() if ln.strip()])
                except FileNotFoundError:
                    await interaction.followup.send(embed=discord.Embed(color=discord.Color.orange(), description=f"> ⚠️ File not found: {fname} — skipping."), ephemeral=True)
                except Exception as e:
                    await interaction.followup.send(embed=discord.Embed(color=discord.Color.red(), description=f"> ❌ Failed reading {fname}: {e}"), ephemeral=True)

        if not messages_list:
            try:
                with open('trading.txt', 'r', encoding='utf-8', errors='replace') as f:
                    messages_list = [ln.strip() for ln in f.read().splitlines() if ln.strip()]
            except Exception:
                pass

        await run_redeem(interaction, uid, key, invite, channel_id, delay, None, "trade", messages_list=messages_list)


class VcRedeemModal(discord.ui.Modal):
    def __init__(self, uid):
        super().__init__(title="Redeem VC Key"); self.uid = uid
        self.add_item(discord.ui.InputText(custom_id="key",        label="Your Key",                         style=discord.InputTextStyle.short, placeholder="Paste your key",                        required=True))
        self.add_item(discord.ui.InputText(custom_id="invite",     label="Server Invite Link or Code",       style=discord.InputTextStyle.short, placeholder="discord.gg/xxx or just the code",       required=True))
        self.add_item(discord.ui.InputText(custom_id="vc_channel", label="Voice Channel ID",                  style=discord.InputTextStyle.short, placeholder="Channel ID (right-click channel > Copy ID)", required=True))
        self.add_item(discord.ui.InputText(custom_id="delay",      label="Delay between reconnects (s)",     style=discord.InputTextStyle.short, placeholder="e.g. 30",                               required=True))
        self.add_item(discord.ui.InputText(custom_id="duration",   label="Duration to keep in VC (s, 0=inf)",style=discord.InputTextStyle.short, placeholder="e.g. 3600 for 1hr, 0 for infinite",  required=False))
    
    async def callback(self, interaction: discord.Interaction):
        uid        = str(interaction.user.id)
        key        = self.children[0].value.strip().upper()
        invite     = self.children[1].value.strip()
        vc_channel = self.children[2].value.strip()
        
        # Validate channel ID
        if not vc_channel.isdigit():
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Invalid channel ID. Please copy the numeric ID (right-click channel > Copy ID)."), ephemeral=True)
        
        try:
            delay = float(self.children[3].value)
            if delay < 1: raise ValueError
        except Exception:
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Delay must be at least 1 second."), ephemeral=True)
        
        try:
            duration_str = (self.children[4].value or "3600").strip()
            duration = float(duration_str) if duration_str else 3600
            if duration < 0: duration = 0
        except Exception:
            duration = 3600
        
        max_retries = 5  # Use default
        await run_redeem(interaction, uid, key, invite, vc_channel, delay, None, "vc", duration_seconds=duration, max_retries=max_retries)


class AdvRedeemModal(discord.ui.Modal):
    def __init__(self, uid):
        super().__init__(title="Redeem Auto Adv Key"); self.uid = uid
        self.add_item(discord.ui.InputText(custom_id="key", label="Your Auto Adv Key", style=discord.InputTextStyle.short, placeholder="Paste your key here", required=True))
    async def callback(self, interaction: discord.Interaction):
        uid = str(interaction.user.id)
        key = self.children[0].value.strip().upper()
        keys = load_keys()
        lookup_key, _ = find_key_entry(keys, key)

        if not lookup_key:
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Invalid key."), ephemeral=True)
        key = lookup_key
        if keys[key]["used"]:
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ This key has already been redeemed."), ephemeral=True)
        if is_key_expired(keys[key]):
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description=f"> ❌ This key expired {format_expiry(keys[key].get('expiresAt'))}."), ephemeral=True)
        if keys[key].get("keyType") != "autoadv":
            kt = keys[key].get("keyType","?")
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description=f"> ❌ This is a **{kt}** key. Use `/{kt}` to redeem it."), ephemeral=True)
        if get_adv_license(uid):
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ You already have an active Auto Adv license. Use `/advpanel` to manage it."), ephemeral=True)

        slots      = keys[key]["slots"]
        allow_dm   = keys[key]["allowDmReply"]
        expires_at = keys[key].get("expiresAt")

        keys[key]["used"]       = True
        keys[key]["redeemedBy"] = uid
        keys[key]["redeemedAt"] = datetime.now(timezone.utc).isoformat()
        save_keys(keys)

        licenses      = load_adv_licenses()
        licenses[uid] = {"keyCode": key, "slots": slots, "allowDmReply": allow_dm,
                         "expiresAt": expires_at, "accounts": [],
                         "redeemedAt": datetime.now(timezone.utc).isoformat()}
        save_adv_licenses(licenses)

        embed, view = build_adv_panel(uid)
        await interaction.response.send_message(
            embed=discord.Embed(color=discord.Color.green(), title="✅ Auto Adv Key Redeemed!",
                                description=f"> **{slots}** account slot(s) unlocked.\n> DM Reply: {'✅ Enabled' if allow_dm else '❌ Disabled'}\n> Expires: {format_expiry(expires_at)}\n\n> Use the panel below to add your accounts and start advertising."),
            ephemeral=True)
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)


class ReactRedeemModal(discord.ui.Modal):
    def __init__(self, uid):
        super().__init__(title="Redeem Reacts Key"); self.uid = uid
        self.add_item(discord.ui.InputText(custom_id="key",        label="Your Key",                    style=discord.InputTextStyle.short, placeholder="Paste your key", required=True))
        self.add_item(discord.ui.InputText(custom_id="invite",     label="Server Invite Link or Code",  style=discord.InputTextStyle.short, placeholder="discord.gg/xxx or just the code", required=True))
        self.add_item(discord.ui.InputText(custom_id="channel_id", label="Channel ID",                 style=discord.InputTextStyle.short, placeholder="Channel ID where the message is", required=True))
        self.add_item(discord.ui.InputText(custom_id="message_id", label="Target Message ID",         style=discord.InputTextStyle.short, placeholder="Message ID to react to", required=True))
        self.add_item(discord.ui.InputText(custom_id="emoji",      label="Emoji (unicode or name:id)", style=discord.InputTextStyle.short, placeholder="😀 or custom_name:1234567890", required=True))
    async def callback(self, interaction: discord.Interaction):
        uid       = str(interaction.user.id)
        key       = self.children[0].value.strip().upper()
        invite    = self.children[1].value.strip()
        channel_id = self.children[2].value.strip()
        message_id = self.children[3].value.strip()
        emoji     = self.children[4].value.strip()
        # Basic validation
        if not channel_id.isdigit():
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Invalid channel ID."), ephemeral=True)
        if not message_id.isdigit():
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Invalid message ID."), ephemeral=True)
        await run_redeem(interaction, uid, key, invite, channel_id, 0, None, "reacts", emoji, message_id)

# ─── Slash commands ────────────────────────────────────────────────────────────

@bot.slash_command(name="generatekey", description="Generate a vouch, chat or trade key.")
async def generatekey(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    if is_restricted(uid): return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> 🚫 You are restricted."), ephemeral=True)
    if not can_gen_key(uid): return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> ❌ No permission to generate keys."), ephemeral=True)
    if is_reseller(uid) and not is_owner(uid) and not is_admin(uid):
        bal = get_balance(uid)
        if bal == 0 or (bal != "infinite" and bal < 3):
            return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description=f"> ❌ Insufficient balance. Need **$3**.\n> Balance: **{format_balance(bal)}**"), ephemeral=True)
    await safe_send_modal(interaction, GenerateKeyModal(uid))


@bot.slash_command(name="reaction", description="Redeem a react key to have tokens react to a message.")
async def reaction(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    if is_restricted(uid): return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> 🚫 You are restricted."), ephemeral=True)
    await safe_send_modal(interaction, ReactRedeemModal(uid))


@bot.slash_command(name="genautoadv", description="Generate an Auto Adv key.")
async def genautoadv(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    if is_restricted(uid): return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> 🚫 You are restricted."), ephemeral=True)
    if not can_gen_key(uid): return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> ❌ No permission to generate keys."), ephemeral=True)
    if is_reseller(uid) and not is_owner(uid) and not is_admin(uid):
        bal = get_balance(uid)
        if bal == 0 or (bal != "infinite" and bal < 3):
            return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description=f"> ❌ Insufficient balance. Need **$3**.\n> Balance: **{format_balance(bal)}**"), ephemeral=True)
    await safe_send_modal(interaction, GenerateAdvKeyModal(uid))


@bot.slash_command(name="genboost", description="Generate a boost key with a number of boosts.")
@discord.option("duration", description="Key duration", required=True, choices=["1month", "3month"])
@discord.option("boosts", description="Number of boosts included in the key", required=True)
async def genboost(interaction: discord.Interaction, boosts: int, duration: str):
    uid = str(interaction.user.id)
    if is_restricted(uid):
        return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> 🚫 You are restricted."), ephemeral=True)
    if not can_gen_key(uid):
        return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> ❌ No permission to generate keys."), ephemeral=True)
    if boosts < 1 or boosts > 50:
        return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> ❌ Boost count must be between 1 and 50."), ephemeral=True)
    if duration not in ("1month", "3month"):
        return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> ❌ Duration must be either 1month or 3month."), ephemeral=True)

    if is_reseller(uid) and not is_owner(uid) and not is_admin(uid):
        bal = get_balance(uid)
        if bal == 0 or (bal != "infinite" and bal < 3):
            return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description=f"> ❌ Insufficient balance. Need **$3**.\n> Balance: **{format_balance(bal)}**"), ephemeral=True)
        deduct_balance(uid)

    # Check available boosts
    booster_tokens = get_booster_tokens()
    total_available = 0
    for token in booster_tokens:
        info = await get_booster_token_status(token)
        if info["valid"]:
            total_available += info["available_boosts"]
    if total_available < boosts:
        return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description=f"> ❌ Not enough available boosts. Need **{boosts}**, found **{total_available}**."), ephemeral=True)

    key = generate_key()
    expires_at = datetime.now(timezone.utc) + timedelta(days=30 if duration == "1month" else 90)
    keys = load_keys()
    keys[key] = {
        "keyType": "boost",
        "boostCount": boosts,
        "duration": duration,
        "expiresAt": expires_at.isoformat(),
        "used": False,
        "createdBy": uid,
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }
    save_keys(keys)

    embed = (discord.Embed(color=discord.Color.green(), title="🚀 Boost Key Generated")
             .add_field(name="Key", value=f"```{key}```", inline=False)
             .add_field(name="Boosts", value=f"{boosts}", inline=True)
             .add_field(name="Duration", value=duration, inline=True)
             .add_field(name="Expires", value=format_expiry(keys[key]["expiresAt"]), inline=True)
             .set_footer(text="Redeem with /boost <key> <invite>"))
    if is_reseller(uid) and not is_owner(uid) and not is_admin(uid):
        embed.description = f"> 💰 Remaining balance: **{format_balance(get_balance(uid))}**"
    await safe_send_message(interaction, embed=embed, ephemeral=True)


@bot.slash_command(name="boost", description="Redeem a boost key and boost the server with specified boosts.")
@discord.option("key", description="Boost key to redeem", required=True)
@discord.option("invite", description="Server invite link or code", required=True)
async def boost(interaction: discord.Interaction, key: str, invite: str):
    uid = str(interaction.user.id)
    if is_restricted(uid):
        return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> 🚫 You are restricted."), ephemeral=True)
    await run_boost(interaction, uid, key.strip().upper(), invite.strip())


@bot.slash_command(name="boostcheck", description="Check boosters.txt and report boost availability.")
async def boostcheck(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    if is_restricted(uid):
        return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> 🚫 You are restricted."), ephemeral=True)
    await handle_boost_check(interaction)


@bot.slash_command(name="stock", description="Show all available stock.")
async def stock(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    if is_restricted(uid):
        return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> 🚫 You are restricted."), ephemeral=True)

    tokens_count = len([t for t in read_lines(TOKENS_FILE) if is_valid_token_string(t)])
    online_count = len(get_mem_tokens("online"))
    offline_count = len(get_mem_tokens("offline"))
    booster_count = len(get_booster_tokens())

    embed = discord.Embed(color=discord.Color.from_rgb(0, 0, 0), title="📦 Stock Available")
    embed.add_field(name="Vouch Tokens", value=f"**{tokens_count}**", inline=True)
    embed.add_field(name="Chat Tokens", value=f"**{tokens_count}**", inline=True)
    embed.add_field(name="Trade Tokens", value=f"**{tokens_count}**", inline=True)
    embed.add_field(name="VC Tokens", value=f"**{tokens_count}**", inline=True)
    embed.add_field(name="Reacts Tokens", value=f"**{tokens_count}**", inline=True)
    embed.add_field(name="Online Member Tokens", value=f"**{online_count}**", inline=True)
    embed.add_field(name="Offline Member Tokens", value=f"**{offline_count}**", inline=True)
    embed.add_field(name="Booster Tokens", value=f"**{booster_count}**", inline=False)

    await safe_send_message(interaction, embed=embed, ephemeral=True)


@bot.slash_command(name="v", description="Post a simple vouch message in channel.")
@discord.option("Seller", description="User to vouch for", type=discord.Member, required=True)
@discord.option("item", description="Purchased item description", required=True)
@discord.option("duration", description="Duration or until when (e.g. '7 days')", required=True)
@discord.option("amount", description="Amount in USD (number)", required=True)
async def v(interaction: discord.Interaction, member: discord.Member, item: str, duration: str, amount: str):
    """Post a vouch statement in the current channel.

    Format:  @user <purchased item till <duration> for <amount>$ legit seller
    """
    uid = str(interaction.user.id)
    if is_restricted(uid):
        return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> 🚫 You are restricted."), ephemeral=True)

    # Normalize amount to a simple numeric display when possible
    amt_display = None
    try:
        # accept strings like "5" or "5.00"
        num = float(str(amount).strip())
        if num.is_integer():
            amt_display = str(int(num))
        else:
            amt_display = str(num)
    except Exception:
        amt_display = str(amount).strip()

    # Build message exactly as requested
    # .upper() makes every letter uppercase
    msg = f"+rep {member.mention} bought {item} [{duration}] for {amt_display}$ legit seller".upper()

    # Send to channel (not ephemeral) so others can see the vouch
    try:
        await interaction.response.send_message(content=msg)
    except Exception:
        # fallback
        await interaction.followup.send(content=msg)


@bot.slash_command(name="genslotext", description="Generate a Slot Extension key for Auto Adv.")
@discord.option("slots", description="Number of extra Auto Adv slots to add", required=True)
async def genslotext(interaction: discord.Interaction, slots: int):
    uid = str(interaction.user.id)
    if is_restricted(uid):
        return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> 🚫 You are restricted."), ephemeral=True)
    if not can_gen_key(uid):
        return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> ❌ No permission to generate keys."), ephemeral=True)
    if slots < 1 or slots > 50:
        return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> ❌ Slots must be a number between 1 and 50."), ephemeral=True)
    if is_reseller(uid) and not is_owner(uid) and not is_admin(uid):
        bal = get_balance(uid)
        if bal == 0 or (bal != "infinite" and bal < 3):
            return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description=f"> ❌ Insufficient balance. Need **$3**.\n> Balance: **{format_balance(bal)}**"), ephemeral=True)
        deduct_balance(uid)

    key = generate_key()
    keys = load_keys()
    keys[key] = {
        "keyType": "autoadvextend",
        "slots": slots,
        "expiresAt": None,
        "used": False,
        "createdBy": uid,
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }
    save_keys(keys)

    embed = (discord.Embed(color=discord.Color.green(), title="📢 Slot Extension Key Generated")
             .add_field(name="Key", value=f"```{key}```")
             .add_field(name="Extra Slots", value=f"+{slots}", inline=True)
             .add_field(name="Expires", value="Never", inline=True)
             .set_footer(text="Redeem with /slotextend"))
    if is_reseller(uid) and not is_owner(uid) and not is_admin(uid):
        embed.description = f"> 💰 Remaining balance: **{format_balance(get_balance(uid))}**"
    await safe_send_message(interaction, embed=embed, ephemeral=True)


@bot.slash_command(name="slotextend", description="Redeem a Slot Extension key for Auto Adv.")
@discord.option("key", description="Paste your slot extension key", required=True)
async def slotextend(interaction: discord.Interaction, key: str):
    uid = str(interaction.user.id)
    if is_restricted(uid):
        return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> 🚫 You are restricted."), ephemeral=True)
    license_data = get_adv_license(uid)
    if not license_data:
        return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> ❌ You have no active Auto Adv license. Redeem one with `/autoadv`."), ephemeral=True)

    keys = load_keys()
    lookup_key, _ = find_key_entry(keys, key)
    if not lookup_key:
        return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> ❌ Invalid key."), ephemeral=True)
    key = lookup_key
    key_data = keys[key]
    if key_data.get("used"):
        return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> ❌ This key has already been redeemed."), ephemeral=True)
    if is_key_expired(key_data):
        return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description=f"> ❌ This key expired {format_expiry(key_data.get('expiresAt'))}."), ephemeral=True)
    if key_data.get("keyType") != "autoadvextend":
        kt = key_data.get("keyType", "unknown")
        return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description=f"> ❌ This is a **{kt}** key. Use `/{kt}` to redeem it."), ephemeral=True)

    extra_slots = int(key_data.get("slots", 0) or 0)
    if extra_slots < 1:
        return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> ❌ Invalid slot extension key."), ephemeral=True)

    keys[key]["used"] = True
    keys[key]["redeemedBy"] = uid
    keys[key]["redeemedAt"] = datetime.now(timezone.utc).isoformat()
    save_keys(keys)

    adv_licenses = load_adv_licenses()
    license_data = adv_licenses.get(uid, {})
    current_slots = int(license_data.get("slots", 1) or 1)
    license_data["slots"] = current_slots + extra_slots
    adv_licenses[uid] = license_data
    save_adv_licenses(adv_licenses)

    await safe_send_message(
        interaction,
        embed=discord.Embed(color=discord.Color.green(), title="✅ Slot Extension Redeemed!",
                            description=(f"> **+{extra_slots}** Auto Adv slot(s) added.\n> Total slots: **{license_data['slots']}**\n\n> Use `/advpanel` to manage your Auto Adv license.")),
        ephemeral=True)


@bot.slash_command(name="vouch", description="Redeem a vouch key — tokens join and vouch for a user.")
async def vouch(interaction: discord.Interaction, key: str, invite: str, channel_id: str, user_id: str, delay: float, messages_file: discord.Attachment = None):
    uid = str(interaction.user.id)
    if is_restricted(uid): return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> 🚫 You are restricted."), ephemeral=True)
    if get_active_redemption(uid, "vouch"): return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> ❌ You already have an active **vouch** session. Use `/manage` to control it."), ephemeral=True)

    # Validate basic inputs
    try:
        if delay < 1: raise ValueError
    except Exception:
        return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> ❌ Delay must be at least 1 second."), ephemeral=True)

    messages_list = None
    if messages_file:
        try:
            raw = await messages_file.read()
            text = raw.decode('utf-8', errors='replace')
            messages_list = [ln.strip() for ln in text.splitlines() if ln.strip()]
        except Exception as e:
            return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description=f"> ❌ Failed to read uploaded file: {e}"), ephemeral=True)

    await run_redeem(interaction, uid, key.strip().upper(), invite.strip(), channel_id.strip(), delay, user_id.strip(), "vouch", messages_list=messages_list)


@bot.slash_command(name="chat", description="Redeem a chat key — tokens join and chat naturally.")
async def chat(interaction: discord.Interaction, key: str, invite: str, channel_id: str, delay: float, messages_file: discord.Attachment = None):
    uid = str(interaction.user.id)
    if is_restricted(uid): return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> 🚫 You are restricted."), ephemeral=True)
    if get_active_redemption(uid, "chat"): return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> ❌ You already have an active **chat** session. Use `/manage` to control it."), ephemeral=True)

    try:
        if delay < 1: raise ValueError
    except Exception:
        return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> ❌ Delay must be at least 1 second."), ephemeral=True)

    messages_list = None
    if messages_file:
        try:
            raw = await messages_file.read()
            text = raw.decode('utf-8', errors='replace')
            messages_list = [ln.strip() for ln in text.splitlines() if ln.strip()]
        except Exception as e:
            return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description=f"> ❌ Failed to read uploaded file: {e}"), ephemeral=True)

    await run_redeem(interaction, uid, key.strip().upper(), invite.strip(), channel_id.strip(), delay, None, "chat", messages_list=messages_list)


@bot.slash_command(name="trade", description="Redeem a trade key — tokens join and send trading messages.")
@discord.option("opt1", description="Optional 1st message source", required=False, choices=["bf", "sab", "mm2", "custom", "mix"])
@discord.option("opt2", description="Optional 2nd message source", required=False, choices=["bf", "sab", "mm2", "custom", "mix"])
@discord.option("opt3", description="Optional 3rd message source", required=False, choices=["bf", "sab", "mm2", "custom", "mix"])
async def trade(interaction: discord.Interaction, key: str, invite: str, channel_id: str, delay: float, opt1: str = None, opt2: str = None, opt3: str = None, messages_file: discord.Attachment = None):
    uid = str(interaction.user.id)
    if is_restricted(uid): return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> 🚫 You are restricted."), ephemeral=True)
    if get_active_redemption(uid, "trade"): return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> ❌ You already have an active **trade** session. Use `/manage` to control it."), ephemeral=True)

    try:
        if delay < 1: raise ValueError
    except Exception:
        return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> ❌ Delay must be at least 1 second."), ephemeral=True)

    valid_sources = {"bf", "sab", "mm2", "custom", "mix"}
    choices = [c.lower() for c in (opt1, opt2, opt3) if c]
    invalid = [c for c in choices if c not in valid_sources]
    if invalid:
        return await safe_send_message(
            interaction,
            embed=discord.Embed(color=discord.Color.red(), description=f"> ❌ Invalid source(s): {', '.join(invalid)}. Available choices: bf, sab, mm2, custom, mix."),
            ephemeral=True
        )

    messages_list = []
    src_map = {
        "bf": "bloxfruits.txt",
        "sab": "sab.txt",
        "mm2": "mm2.txt",
    }

    async def read_attachment_from_interaction() -> list | None:
        if messages_file:
            try:
                raw = await messages_file.read()
                text = raw.decode('utf-8', errors='replace')
                return [ln.strip() for ln in text.splitlines() if ln.strip()]
            except Exception as e:
                await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description=f"> ❌ Failed to read uploaded file: {e}"), ephemeral=True)
                return None

        await interaction.response.send_message(
            "Please upload a plain text file (one message per line) in this channel or DM me within 5 minutes. Reply `cancel` to abort.",
            ephemeral=True
        )

        def check(m: discord.Message):
            return m.author.id == interaction.user.id and (
                m.channel == interaction.channel or isinstance(m.channel, discord.DMChannel)
            ) and (len(m.attachments) > 0 or (m.content and m.content.lower().strip() == "cancel"))

        try:
            msg = await bot.wait_for('message', check=check, timeout=300)
        except asyncio.TimeoutError:
            await interaction.followup.send("Timed out — no file received.", ephemeral=True)
            return None

        if msg.content and msg.content.lower().strip() == "cancel":
            await interaction.followup.send("Upload cancelled.", ephemeral=True)
            return None

        if not msg.attachments:
            await interaction.followup.send("No attachment found. Upload cancelled.", ephemeral=True)
            return None

        att = msg.attachments[0]
        try:
            data = await att.read()
            text = data.decode('utf-8', errors='replace')
            return [ln.strip() for ln in text.splitlines() if ln.strip()]
        except Exception:
            await interaction.followup.send("Failed to read attachment; ensure it's a text file.", ephemeral=True)
            return None


    mix_selected = "mix" in choices
    # If mix is selected, always use all sources and any uploaded file
    if mix_selected:
        # Remove 'mix' and 'custom' from choices to avoid duplicate loading
        choices = [c for c in choices if c not in ("mix", "custom")]
        # Add all three sources
        mix_sources = ["bf", "sab", "mm2"]
        loaded = set()
        for ch in mix_sources:
            fname = src_map[ch]
            if ch in loaded:
                continue
            loaded.add(ch)
            try:
                with open(fname, 'r', encoding='utf-8', errors='replace') as f:
                    messages_list.extend([ln.strip() for ln in f.read().splitlines() if ln.strip()])
            except FileNotFoundError:
                await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.orange(), description=f"> ⚠️ File not found: {fname} — skipping."), ephemeral=True)
            except Exception as e:
                await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description=f"> ❌ Failed reading {fname}: {e}"), ephemeral=True)
        # Add custom file if uploaded
        if messages_file:
            custom_msgs = await read_attachment_from_interaction()
            if custom_msgs is None:
                return
            messages_list.extend(custom_msgs)
    else:
        # If custom is selected directly, only load the uploaded file
        if "custom" in choices:
            custom_msgs = await read_attachment_from_interaction()
            if custom_msgs is None:
                return
            messages_list.extend(custom_msgs)
            choices = [c for c in choices if c != "custom"]
        # Load any other selected sources
        loaded = set()
        for ch in choices:
            if ch not in src_map or ch in loaded:
                continue
            loaded.add(ch)
            fname = src_map[ch]
            try:
                with open(fname, 'r', encoding='utf-8', errors='replace') as f:
                    messages_list.extend([ln.strip() for ln in f.read().splitlines() if ln.strip()])
            except FileNotFoundError:
                await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.orange(), description=f"> ⚠️ File not found: {fname} — skipping."), ephemeral=True)
            except Exception as e:
                await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description=f"> ❌ Failed reading {fname}: {e}"), ephemeral=True)

    if not messages_list and messages_file:
        try:
            raw = await messages_file.read()
            text = raw.decode('utf-8', errors='replace')
            messages_list = [ln.strip() for ln in text.splitlines() if ln.strip()]
        except Exception as e:
            return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description=f"> ❌ Failed to read uploaded file: {e}"), ephemeral=True)

    if not messages_list:
        try:
            with open('trading.txt', 'r', encoding='utf-8', errors='replace') as f:
                messages_list = [ln.strip() for ln in f.read().splitlines() if ln.strip()]
        except Exception:
            pass

    await run_redeem(interaction, uid, key.strip().upper(), invite.strip(), channel_id.strip(), delay, None, "trade", messages_list=messages_list)


@bot.slash_command(name="vc", description="Redeem a VC key — tokens join a voice channel.")
async def vc(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    if is_restricted(uid): return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> 🚫 You are restricted."), ephemeral=True)
    if get_active_redemption(uid, "vc"): return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> ❌ You already have an active **vc** session. Use `/manage` to control it."), ephemeral=True)
    await safe_send_modal(interaction, VcRedeemModal(uid))


@bot.slash_command(name="autoadv", description="Redeem an Auto Adv key — accounts advertise in channels.")
async def autoadv(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    if is_restricted(uid): return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> 🚫 You are restricted."), ephemeral=True)
    if get_adv_license(uid): return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> ❌ You already have an active Auto Adv license. Use `/advpanel` to manage it."), ephemeral=True)
    await safe_send_modal(interaction, AdvRedeemModal(uid))


member_group = discord.SlashCommandGroup("member", "Member join commands")

@member_group.command(name="stock", description="Show online/offline member stock.")
async def member_stock(interaction: discord.Interaction):
    online_count = len(get_mem_tokens("online"))
    offline_count = len(get_mem_tokens("offline"))

    embed = (discord.Embed(color=discord.Color.blurple(), title="📦 Member Stock")
             .add_field(name="Online Member Stock", value=f"**{online_count}** Online Members Available", inline=False)
             .add_field(name="Offline Member Stock", value=f"**{offline_count}** Offline Members Available", inline=False)
            )
    await safe_send_message(interaction, embed=embed, ephemeral=True)


@bot.slash_command(name="genmemkey", description="Generate a key for online/offline tokens to join a server.")
@discord.option("mode", description="Choose online or offline tokens", required=True, choices=["online", "offline"])
@discord.option("amount", description="Number of tokens to join the server", required=True)
async def genmemkey(interaction: discord.Interaction, mode: str, amount: int):
    uid = str(interaction.user.id)
    if is_restricted(uid):
        return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> 🚫 You are restricted."), ephemeral=True)
    if not can_gen_key(uid):
        return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> ❌ No permission to generate keys."), ephemeral=True)
    if amount < 1:
        return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> ❌ Amount must be at least 1."), ephemeral=True)
    tokens = get_mem_tokens(mode)
    if len(tokens) < amount:
        return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description=f"> ❌ Not enough {mode} tokens. Need **{amount}**, only **{len(tokens)}** available."), ephemeral=True)
    if is_reseller(uid) and not is_owner(uid) and not is_admin(uid):
        bal = get_balance(uid)
        if bal == 0 or (bal != "infinite" and bal < 3):
            return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description=f"> ❌ Insufficient balance. Need **$3**.\n> Balance: **{format_balance(bal)}**"), ephemeral=True)
    key = generate_key()
    key_type = f"mem-{mode}"
    keys = load_keys()
    keys[key] = {
        "keyType": key_type,
        "tokenCount": amount,
        "expiresAt": None,
        "used": False,
        "createdBy": uid,
        "createdAt": datetime.now(timezone.utc).isoformat()
    }
    save_keys(keys)

    # Generate and store order-specific content
    is_reseller_only = is_reseller(uid) and not is_owner(uid) and not is_admin(uid)
    generated_content = generate_order_content(key_type, {
        "key_id": key,
        "buyer_id": uid,
        "token_count": amount,
        "mode": mode
    })

    # Send webhook notification for member join key generation
    webhook_data = {
        "buyer_id": uid,
        "buyer_username": interaction.user.name,
        "key_id": key,
        "key_type": key_type,
        "token_count": amount,
        "mode": mode,
        "expires_at": None,
        "price": 3.0 if is_reseller_only else 0.0,
        "payment_method": "balance" if is_reseller_only else "free",
        "generated_content": generated_content
    }
    asyncio.create_task(send_webhook_notification("memkey_generated", webhook_data))

    embed = (discord.Embed(color=discord.Color.green(), title="🔑 Member Join Key Generated")
             .add_field(name="Key", value=f"```{key}```", inline=False)
             .add_field(name="Mode", value=mode.title(), inline=True)
             .add_field(name="Tokens", value=str(amount), inline=True)
             .add_field(name="Source", value="ontokens.txt" if mode == "online" else "offtokens.txt", inline=True)
             .set_footer(text="Redeem with /redeem <key> <invite>"))
    await safe_send_message(interaction, embed=embed, ephemeral=True)


async def run_mem_redeem(interaction, uid, key, invite_input):
    invite_code = extract_invite_code(invite_input)
    if not invite_code:
        return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> ❌ Invalid invite link or code."), ephemeral=True)

    keys = load_keys()
    lookup_key, _ = find_key_entry(keys, key)
    if not lookup_key:
        return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> ❌ Invalid key."), ephemeral=True)
    key = lookup_key
    if keys[key]["used"]:
        return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> ❌ This key has already been redeemed."), ephemeral=True)
    if is_key_expired(keys[key]):
        return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description=f"> ❌ This key expired {format_expiry(keys[key].get('expiresAt'))}."), ephemeral=True)

    key_type = keys[key].get("keyType", "")
    if not key_type.startswith("mem-"):
        return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description=f"> ❌ This is a **{key_type}** key. Use `/{key_type}` to redeem it."), ephemeral=True)

    mode = key_type.split("-", 1)[1]
    token_count = keys[key].get("tokenCount", 0)
    token_source = get_mem_tokens(mode)
    if len(token_source) < token_count:
        return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description=f"> ❌ Not enough {mode} tokens to redeem. Need **{token_count}**, only **{len(token_source)}** available."), ephemeral=True)

    guild_id = await resolve_invite_to_guild(invite_code)
    if not guild_id:
        return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> ❌ Could not resolve the invite. Make sure it's valid and not expired."), ephemeral=True)

    keys[key]["used"] = True
    keys[key]["redeemedBy"] = uid
    keys[key]["redeemedAt"] = datetime.now(timezone.utc).isoformat()
    save_keys(keys)

    # Create unique session ID for HTML logs
    session_id = str(uuid.uuid4())
    selected_tokens = token_source[:token_count]
    icon = TYPE_ICONS.get(key_type, "🔑")
    type_label = TYPE_LABELS.get(key_type, key_type.title())

    # Initialize join session data
    join_sessions[session_id] = {
        "uid": uid,
        "key": key,
        "mode": mode,
        "token_count": token_count,
        "invite_code": invite_code,
        "guild_id": guild_id,
        "start_time": datetime.now(timezone.utc).isoformat(),
        "joined_count": 0,
        "logs": [],
        "status": "in_progress"
    }

    # Send initial progress message
    progress_msg = await safe_send_message(
        interaction,
        embed=discord.Embed(color=discord.Color.yellow(), title=f"🔑 {icon} {type_label} Key Redeemed!",
                            description=f"> **Phase 1/1:** Joining **{token_count}** {mode} tokens to the server...\n> Invite: `discord.gg/{invite_code}`\n> **0/{token_count}** joined"),
        ephemeral=True
    )

    joined_count = 0
    join_logs = []

    for i, token in enumerate(selected_tokens):
        r = await join_server_with_token(token, guild_id)
        if r["success"]:
            joined_count += 1
        status_str = (
            "✅ joined" if r["success"] and not r.get("alreadyIn") else
            "↩️ already in server" if r.get("alreadyIn") else
            f"❌ {r.get('reason', 'failed')}"
        )

        # Log each join attempt
        timestamp = datetime.now(timezone.utc).strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] **{r['username']}** — {status_str}"
        join_logs.append(log_entry)

        # Update session data
        join_sessions[session_id]["joined_count"] = joined_count
        join_sessions[session_id]["logs"] = join_logs.copy()

        # Update progress embed
        progress_embed = discord.Embed(
            color=discord.Color.yellow(),
            title=f"🔑 {icon} {type_label} Key Redeemed!",
            description=(
                f"> **Phase 1/1:** Joining **{token_count}** {mode} tokens to the server...\n"
                f"> Invite: `discord.gg/{invite_code}`\n"
                f"> **{joined_count}/{token_count}** joined\n"
                f"> Last: {log_entry}\n"
                
            )
        )

        try:
            if progress_msg is not None and hasattr(progress_msg, 'edit'):
                await progress_msg.edit(embed=progress_embed)
            else:
                await safe_edit_message(interaction, embed=progress_embed)
        except Exception as e:
            print(f"[Join Progress] Failed to edit message: {e}")
            try:
                await interaction.followup.send(embed=progress_embed, ephemeral=True)
            except Exception as e2:
                print(f"[Join Progress] Fallback also failed: {e2}")

        if i < len(selected_tokens) - 1:
            await asyncio.sleep(1.5)

    if joined_count == 0:
        keys = load_keys()
        if keys.get(key):
            keys[key]["used"] = False
            keys[key].pop("redeemedBy", None)
            keys[key].pop("redeemedAt", None)
            save_keys(keys)

        # Mark session as failed
        join_sessions[session_id]["status"] = "failed"
        join_sessions[session_id]["end_time"] = datetime.now(timezone.utc).isoformat()
        join_sessions[session_id]["final_count"] = 0

        # Update HTML file
        html_content = generate_join_progress_html(session_id)
        if html_content:
            with open(f'join_progress_{session_id}.html', 'w', encoding='utf-8') as f:
                f.write(html_content)

        failed_embed = discord.Embed(
            color=discord.Color.red(),
            title="❌ Join Failed",
            description="> No tokens could join the server.\n> **Your key has been reset** — you can try redeeming again.\n> Make sure the invite link is valid and the bot has permission to add members."
        )
        try:
            if progress_msg is not None and hasattr(progress_msg, 'edit'):
                await progress_msg.edit(embed=failed_embed)
            else:
                await safe_edit_message(interaction, embed=failed_embed)
        except Exception as e:
            print(f"[Join Failed] Failed to edit message: {e}")
            try:
                await interaction.followup.send(embed=failed_embed, ephemeral=True)
            except Exception as e2:
                print(f"[Join Failed] Fallback also failed: {e2}")
        return

    extra_line = "" if joined_count == token_count else f"\n> {token_count - joined_count} token(s) failed to join."
    final_embed = discord.Embed(
        color=discord.Color.green(),
        title="✅ Member Join Complete!",
        description=(
            f"> **{joined_count}/{token_count}** {mode} token(s) joined successfully.\n"
            f"> Invite: `discord.gg/{invite_code}`{extra_line}\n"
            
        )
    )

    # Mark session as complete
    join_sessions[session_id]["status"] = "completed"
    join_sessions[session_id]["end_time"] = datetime.now(timezone.utc).isoformat()
    join_sessions[session_id]["final_count"] = joined_count

    # Send HTML file as attachment
    html_content = generate_join_progress_html(session_id)
    if html_content:
        import io
        file_obj = io.BytesIO(html_content.encode('utf-8'))
        file_obj.seek(0)
        file = discord.File(file_obj, filename=f'final-logs-{session_id[:8]}.html')
        try:
            await interaction.followup.send(
                content="📊 **Join Progress Complete!** Download the HTML file below to view the final logs.",
                file=file,
                ephemeral=True
            )
        except Exception as e:
            print(f"[Join Complete] Failed to send HTML file: {e}")

    try:
        if progress_msg is not None and hasattr(progress_msg, 'edit'):
            await progress_msg.edit(embed=final_embed)
        else:
            await safe_edit_message(interaction, embed=final_embed)
    except Exception as e:
        print(f"[Join Complete] Failed to edit message: {e}")
        try:
            await interaction.followup.send(embed=final_embed, ephemeral=True)
        except Exception as e2:
            print(f"[Join Complete] Fallback also failed: {e2}")


@bot.slash_command(name="redeem", description="Redeem a memkey so tokens join a server.")
@discord.option("key", description="Your redemption key", required=True)
@discord.option("invite", description="Server invite link or code", required=True)
async def redeem(interaction: discord.Interaction, key: str, invite: str):
    uid = str(interaction.user.id)
    if is_restricted(uid):
        return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> 🚫 You are restricted."), ephemeral=True)
    await run_mem_redeem(interaction, uid, key.strip().upper(), invite.strip())


@bot.slash_command(name="advpanel", description="Open your Auto Adv panel.")
async def advpanel(interaction: discord.Interaction):
    uid = str(interaction.user.id)

    if is_restricted(uid):
        return await interaction.response.send_message(
            embed=discord.Embed(
                color=discord.Color.red(),
                description="> 🚫 You are restricted."
            ),
            ephemeral=True
        )

    guide = discord.Embed(
        title="🚀 Auto Adv Setup Guide",
        description=(
            "**1.** Add Account\n"
            "**2.** Add Channels\n"
            "**3.** Add Message\n"
            "**4.** Set Delay\n"
            "**5.** Press Start\n\n"
            "⚠️ Use high delay to reduce rate limits.\n"
            "⚠️ Invalid tokens will fail automatically.\n"
            "⚠️ Keep messages clean.\n\n"
            "Opening panel in 5 seconds..."
        ),
        color=discord.Color.blurple()
    )

    await interaction.response.send_message(
        embed=guide,
        ephemeral=True
    )

    await asyncio.sleep(5)

    embed, view = build_adv_panel(uid)

    await interaction.followup.send(
        embed=embed,
        view=view if view else discord.utils.MISSING,
        ephemeral=True
    )


@bot.slash_command(name="testtoken", description="Test if an Auto Adv account token is valid.")
@discord.option("token", description="Paste the token to test", required=True)
async def testtoken(interaction: discord.Interaction, token: str):
    """Test token validity and show detailed diagnostics."""
    uid = str(interaction.user.id)
    if is_restricted(uid): 
        return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> 🚫 You are restricted."), ephemeral=True)
    
    await interaction.response.defer(ephemeral=True)
    
    is_valid, message, user_info, is_bot = await validate_adv_token(token)
    
    lines = ["🔍 **Token Validation Report**\n"]
    
    if is_valid:
        username = user_info.get("username", "Unknown")
        user_id = user_info.get("id", "Unknown")
        email = user_info.get("email", "Not shown")
        token_type = "Bot" if is_bot else "User"
        
        lines.extend([
            f"✅ **Token is VALID**\n",
            f"📊 Account Info:",
            f"  • Username: `{username}`",
            f"  • User ID: `{user_id}`",
            f"  • Token Type: {token_type}",
            f"  • Email verified: {'Yes' if user_info.get('verified') else 'No'}",
            f"\n💡 You can use this token for Auto Adv!",
        ])
    else:
        lines.extend([
            f"❌ **Token is INVALID**\n",
            f"⚠️  {message}\n",
            f"🔧 How to fix it:",
            f"  1. Go to Discord User Settings",
            f"  2. Find the app/bot that created this token",
            f"  3. Revoke and regenerate a new token",
            f"  4. Try testing again with the new token",
            f"\n📝 Make sure you're pasting the FULL token (starts with 'Bot' or a long string)",
        ])
    
    await interaction.followup.send(
        embed=discord.Embed(
            color=discord.Color.green() if is_valid else discord.Color.red(),
            description="\n".join(lines)
        ),
        ephemeral=True
    )


@bot.slash_command(name="manage", description="Manage your active vouch, chat, trade or vc session.")
@discord.option("type", description="Which session to manage", choices=["vouch", "chat", "trade", "vc"])
async def manage(interaction: discord.Interaction, type: str):
    uid = str(interaction.user.id)
    if is_restricted(uid): return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> 🚫 You are restricted."), ephemeral=True)
    embed, view = build_manage_embed_and_view(uid, type)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


@bot.slash_command(name="vcstop", description="Force disconnect all your voice connections.")
async def vcstop(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    if is_restricted(uid): return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> 🚫 You are restricted."), ephemeral=True)
    
    stop_session(uid, "vc")
    disconnected_count = await disconnect_voice_connections(uid)
    
    if disconnected_count > 0:
        embed = discord.Embed(color=discord.Color.green(), title="✅ Voice Connections Disconnected", 
                            description=f"> Successfully disconnected **{disconnected_count}** voice connection(s) and stopped your VC session.")
    else:
        embed = discord.Embed(color=discord.Color.yellow(), title="ℹ️ No Active Voice Connections", 
                            description="> You don't have any active voice connections to disconnect.")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.slash_command(name="adminpanel", description="Open the admin control panel.")
async def adminpanel(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    if is_restricted(uid): return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> 🚫 You are restricted."), ephemeral=True)
    if not can_manage_bot(uid): return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ No permission to access the admin panel."), ephemeral=True)
    embed, view = build_admin_embed_and_view()
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


balance_group = discord.SlashCommandGroup("balance", "Balance management commands")

@balance_group.command(name="add", description="Owner-only: add balance to a user.")
@discord.option("user_id", description="Discord user ID to credit", required=True)
@discord.option("amount", description="Amount to add (number or infinite)", required=True)
async def balance_add(interaction: discord.Interaction, user_id: str, amount: str):
    uid = str(interaction.user.id)
    if not is_owner(uid):
        return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Owner-only command."), ephemeral=True)

    target_id = user_id.strip()
    raw_amount = amount.strip().lower()

    if raw_amount == "infinite":
        new_balance = "infinite"
    else:
        try:
            parsed_amount = float(raw_amount)
            if parsed_amount <= 0:
                raise ValueError
        except Exception:
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Amount must be a positive number or `infinite`."), ephemeral=True)

        current_balance = get_balance(target_id)
        if current_balance == "infinite":
            new_balance = "infinite"
        else:
            new_balance = (current_balance or 0) + parsed_amount

    set_balance(target_id, new_balance)
    await interaction.response.send_message(embed=discord.Embed(color=discord.Color.green(), description=f"> ✅ Balance updated for <@{target_id}>.\n> New balance: **{format_balance(new_balance)}**"), ephemeral=True)


@balance_group.command(name="set", description="Owner-only: set a user balance.")
@discord.option("user_id", description="Discord user ID to set balance for", required=True)
@discord.option("amount", description="Balance amount (number or infinite)", required=True)
async def balance_set(interaction: discord.Interaction, user_id: str, amount: str):
    uid = str(interaction.user.id)
    if not is_owner(uid):
        return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Owner-only command."), ephemeral=True)

    target_id = user_id.strip()
    raw_amount = amount.strip().lower()

    if raw_amount == "infinite":
        new_balance = "infinite"
    else:
        try:
            parsed_amount = float(raw_amount)
            if parsed_amount < 0:
                raise ValueError
        except Exception:
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Amount must be a non-negative number or `infinite`."), ephemeral=True)
        new_balance = parsed_amount

    set_balance(target_id, new_balance)
    await interaction.response.send_message(embed=discord.Embed(color=discord.Color.green(), description=f"> ✅ Balance for <@{target_id}> set to **{format_balance(new_balance)}**."), ephemeral=True)


# Register slash command groups
bot.add_application_command(member_group)
bot.add_application_command(balance_group)

async def check_expired_adv_licenses():
    """Background task to check for expired Auto Adv licenses and stop them."""
    while True:
        try:
            await asyncio.sleep(60)  # Check every 60 seconds
            
            licenses = load_adv_licenses()
            expired_users = []
            
            for uid, lic in list(licenses.items()):
                if is_adv_license_expired(lic):
                    # Check if user has any running accounts
                    running_accs = [a for a in lic.get("accounts", []) if adv_sessions.get(skey(uid, a["id"]), {}).get("running")]
                    
                    if running_accs:
                        # Stop all accounts
                        stop_all_adv(uid)
                        expired_users.append((uid, lic))
            
            # Send notifications for expired licenses
            for uid, lic in expired_users:
                await notify_adv_license_expired(uid, lic)
                # Remove expired license
                licenses.pop(uid, None)
            
            if expired_users:
                save_adv_licenses(licenses)
                
        except Exception as e:
            print(f"[ExpireChecker] Error: {e}")

@bot.event
async def on_ready():
    print(f'Bot is ready as {bot.user}')
    print(f'Bot is in {len(bot.guilds)} guilds')
    for guild in bot.guilds:
        print(f'- {guild.name} ({guild.id})')
    try:
        await bot.sync_commands()
        print("Slash commands synced!")
    except Exception as e:
        # Don't crash the bot if command sync fails (duplicate names, etc.)
        print(f"[on_ready] Warning: sync_commands failed: {e}")
    
    # Start background task for checking expired licenses
    asyncio.create_task(check_expired_adv_licenses())

    # Attempt to restore running sessions after restart
    await load_saved_state_and_resume()
    
    # Start Flask web admin panel in a separate thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print("Web admin panel started on http://0.0.0.0:5000")


@bot.slash_command(name="extracttoken", description="Extract valid tokens from emailtokens.txt.")
@discord.option("amount", description="Number of tokens to extract", required=True)
@discord.option("format", description="Output format", required=False, choices=["with email and pass", "without email and pass"])
async def extracttoken(interaction: discord.Interaction, amount: int, format: str = "without email and pass"):
    uid = str(interaction.user.id)
    if is_restricted(uid):
        return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> 🚫 You are restricted."), ephemeral=True)
    if not can_manage_bot(uid):
        return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Admin only."), ephemeral=True)
    if amount <= 0:
        return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Amount must be a positive number."), ephemeral=True)

    include_email_pass = bool(format and format.lower().startswith("with"))
    extracted = extract_email_tokens(amount, include_email_pass=include_email_pass)
    if not extracted:
        missing_text = "email:password:token entries" if include_email_pass else "tokens"
        return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description=f"> ⚠️ No valid {missing_text} found in `emailtokens.txt`."), ephemeral=True)

    payload_text = "\n".join(extracted)
    if len(payload_text) > 1800 or len(extracted) > 20:
        buffer = BytesIO(payload_text.encode("utf-8"))
        file = discord.File(buffer, filename="extracttoken.txt")
        embed = discord.Embed(color=discord.Color.green(), description=f"> ✅ Extracted {len(extracted)} valid {'entries' if include_email_pass else 'tokens'} from `emailtokens.txt`. Output attached as a file.")
        return await interaction.response.send_message(embed=embed, file=file, ephemeral=True)

    embed = discord.Embed(color=discord.Color.green(), description=f"> ✅ Extracted {len(extracted)} valid {'entries' if include_email_pass else 'tokens'} from `emailtokens.txt`.")
    embed.add_field(name="Result", value=f"```{payload_text}```", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    content = message.content.strip()
    if not content.lower().startswith(".make /extracttoken"):
        return

    parts = content.split()
    if len(parts) < 3:
        return await message.channel.send("> ❌ Usage: `.make /extracttoken <amount> [with email and pass|without email and pass]`")

    try:
        amount = int(parts[2])
    except ValueError:
        return await message.channel.send("> ❌ Amount must be a number.")

    format_option = "without email and pass"
    if len(parts) > 3:
        format_option = " ".join(parts[3:]).strip()

    include_email_pass = format_option.lower().startswith("with")
    extracted = extract_email_tokens(amount, include_email_pass=include_email_pass)
    if not extracted:
        missing_text = "email:password:token entries" if include_email_pass else "tokens"
        return await message.channel.send(f"> ⚠️ No valid {missing_text} found in `emailtokens.txt`." )

    payload_text = "\n".join(extracted)
    if len(payload_text) > 1800 or len(extracted) > 20:
        buffer = BytesIO(payload_text.encode("utf-8"))
        file = discord.File(buffer, filename="extracttoken.txt")
        return await message.channel.send(content=f"> ✅ Extracted {len(extracted)} valid {'entries' if include_email_pass else 'tokens'} from `emailtokens.txt`. Output attached.", file=file)

    return await message.channel.send(
        f"""> ✅ Extracted {len(extracted)} valid {'entries' if include_email_pass else 'tokens'} from `emailtokens.txt`.
```{payload_text}```"""
    )


# ─── Referral Tier System Commands ────────────────────────────────────────────

@bot.slash_command(name="referral", description="Get your referral link to earn tier rewards.")
async def referral(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    if is_restricted(uid):
        return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> 🚫 You are restricted."), ephemeral=True)
    
    ref_data = get_referral_data(uid)
    level = get_referral_tier(uid)
    tier_info = REFERRAL_TIERS[level]
    referral_code = ref_data["referralId"]
    current_refs = len(ref_data.get("referrals", []))
    
    embed = discord.Embed(color=discord.Color.gold(), title="🔗 Your Referral Code")
    embed.description = f"> Share your code below to earn **{tier_info['name']}** tier rewards!\n> Others join with `/joinref {referral_code}`."
    embed.add_field(name="🏆 Your Current Tier", value=f"**{tier_info['name']}** ({REFERRAL_TIERS[level]['refs_required']}+ referrals)", inline=True)
    embed.add_field(name="📦 Your Bonus Slots", value=f"**+{tier_info['bonus_slots']}** Auto Adv slots", inline=True)
    embed.add_field(name="🔑 Your Referral Code", value=f"```{referral_code}```", inline=False)
    
    if level < 4:
        next_tier = level + 1
        next_refs_needed = REFERRAL_TIERS[next_tier]["refs_required"]
        embed.add_field(name="🎯 Next Tier", value=f"**{REFERRAL_TIERS[next_tier]['name']}** — {next_refs_needed - current_refs} more referrals needed", inline=False)
    
    if tier_info["perks"]:
        perks_text = "\n".join(f"• {perk}" for perk in tier_info["perks"])
        embed.add_field(name="✨ Your Perks", value=perks_text, inline=False)
    
    embed.set_footer(text="Referrals are tracked automatically")
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.slash_command(name="referralstats", description="View your detailed referral tier stats and progress.")
async def referralstats(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    if is_restricted(uid):
        return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> 🚫 You are restricted."), ephemeral=True)
    
    ref_data = get_referral_data(uid)
    current_refs = len(ref_data.get("referrals", []))
    current_level = get_referral_tier(uid)
    current_tier = REFERRAL_TIERS[current_level]
    
    embed = discord.Embed(color=discord.Color.blurple(), title="📊 Your Referral Stats")
    embed.add_field(name="🏆 Current Tier", value=f"**{current_tier['name']}**", inline=True)
    embed.add_field(name="👥 Total Referrals", value=f"**{current_refs}**", inline=True)
    embed.add_field(name="📦 Bonus Slots Earned", value=f"**+{current_tier['bonus_slots']}** slots", inline=True)
    
    # Show tier progression
    tier_progress = ""
    for tier_num in range(5):
        tier_data = REFERRAL_TIERS[tier_num]
        reached = "✅" if current_refs >= tier_data["refs_required"] else "⏳"
        tier_progress += f"{reached} **{tier_data['name']}** ({tier_data['refs_required']} refs)\n"
    
    embed.add_field(name="🎯 Tier Progression", value=tier_progress, inline=False)
    
    if current_level < 4:
        next_tier = REFERRAL_TIERS[current_level + 1]
        refs_needed = next_tier["refs_required"] - current_refs
        embed.add_field(name="🚀 Next Milestone", value=f"**{refs_needed}** more referrals to reach **{next_tier['name']}** tier!", inline=False)
    else:
        embed.add_field(name="👑 Status", value="You've reached **Platinum** tier! Maximum perks unlocked.", inline=False)
    
    embed.set_footer(text="Share your referral link with /referral command")
    await interaction.response.send_message(embed=embed, ephemeral=True)


# ─── Referral Tutorial (Interactive Step-by-Step) ────────────────────────────

class ReferralTutorialView(discord.ui.View):
    def __init__(self, uid: str, current_step: int = 0):
        super().__init__(timeout=120)
        self.uid = uid
        self.current_step = current_step
        self.update_buttons()
    
    def update_buttons(self):
        # Clear existing buttons
        self.clear_items()
        
        if self.current_step > 0:
            btn_prev = discord.ui.Button(label="← Previous", style=discord.ButtonStyle.secondary)
            btn_prev.callback = lambda i: self.nav_step(i, -1)
            self.add_item(btn_prev)
        
        if self.current_step < 5:
            btn_next = discord.ui.Button(label="Next →", style=discord.ButtonStyle.primary)
            btn_next.callback = lambda i: self.nav_step(i, 1)
            self.add_item(btn_next)
        
        if self.current_step == 1:
            btn_getlink = discord.ui.Button(label="🔗 Get My Link", style=discord.ButtonStyle.success)
            btn_getlink.callback = self.get_referral_link
            self.add_item(btn_getlink)
    
    async def nav_step(self, interaction: discord.Interaction, direction: int):
        uid = str(interaction.user.id)
        if uid != self.uid:
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Not your tutorial."), ephemeral=True)
        
        self.current_step += direction
        self.current_step = max(0, min(5, self.current_step))
        self.update_buttons()
        
        embed = self.build_step_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def get_referral_link(self, interaction: discord.Interaction):
        uid = str(interaction.user.id)
        if uid != self.uid:
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Not your tutorial."), ephemeral=True)
        
        ref_data = get_referral_data(uid)
        referral_code = ref_data["referralId"]
        embed = discord.Embed(color=discord.Color.green(), title="🔗 Your Referral Code")
        embed.description = f"Share this with anyone to earn referrals:\n```{referral_code}```"
        embed.set_footer(text="They'll get bonuses when they use /joinref <code>!")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    def build_step_embed(self) -> discord.Embed:
        steps = [
            {
                "title": "🎯 Referral System Explained",
                "description": "The referral system rewards you for bringing others to the bot!\n\n**How it works:**\n• Get your unique referral ID\n• Share it with friends & communities\n• Others use `/joinref <your-id>` to join\n• Each person who joins = 1 referral\n• Referrals unlock tier rewards!",
                "color": discord.Color.blurple(),
            },
            {
                "title": "🔗 Step 1: Get Your Referral ID",
                "description": "Click the **🔗 Get My Link** button below to receive your personal referral code.\n\nYour code is unique and identifies you as the referrer.\n\n**How to share:** Tell others to run `/joinref <your-code>`\n\n**Pro tip:** Share your code in communities, Discord servers, and social media to maximize referrals!",
                "color": discord.Color.gold(),
            },
            {
                "title": "👥 Step 2: Others Join Using Your ID",
                "description": "People who want to join YOUR referral network run:\n```/joinref <your-code>```\n\n**What happens:**\n• They become registered as your referral\n• You get +1 to your referral count\n• They get welcome bonuses\n• You get notified via DM\n\n**Protection:** They can only join once. If they're already a member, it blocks them!",
                "color": discord.Color.green(),
            },
            {
                "title": "📊 Step 3: Track Your Progress",
                "description": "Use `/referralstats` to see:\n• Your current tier (Rookie → Platinum)\n• Total referrals earned\n• How many more you need for next tier\n• Bonus slots unlocked\n\nEach tier unlocks new perks and features!",
                "color": discord.Color.blurple(),
            },
            {
                "title": "⭐ Step 4: Unlock Tier Rewards",
                "description": "**Tier Progression:**\n🥉 **Bronze** (5 refs) → +1 Auto Adv slot\n🥈 **Silver** (10 refs) → +2 slots, Priority queue\n🥇 **Gold** (20 refs) → +3 slots, Discord role\n👑 **Platinum** (50+ refs) → +5 slots, VIP status, Custom commands!\n\nHigher tiers = More power & features!",
                "color": discord.Color.gold(),
            },
            {
                "title": "🚀 Step 5: Compete & Track",
                "description": "**Leaderboard:** Admins run `/refleaderboard` to see top referrers!\n\n**Tips to Maximize Referrals:**\n• Share in Discord communities & servers\n• Post on trading forums\n• Tell your Discord friends\n• Create content highlighting the benefits\n• Show off your tier achievements\n\nEvery referral gets you closer to **Platinum** status! 👑",
                "color": discord.Color.green(),
            },
        ]
        
        step = steps[self.current_step]
        embed = discord.Embed(color=step["color"], title=step["title"])
        embed.description = step["description"]
        embed.set_footer(text=f"Tutorial: Step {self.current_step + 1} of 6")
        return embed


@bot.slash_command(name="referraltutorial", description="Interactive tutorial for the referral tier system.")
async def referraltutorial(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    if is_restricted(uid):
        return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> 🚫 You are restricted."), ephemeral=True)
    
    view = ReferralTutorialView(uid, current_step=0)
    embed = view.build_step_embed()
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


# ─── Referral Leaderboard (Admin) ──────────────────────────────────────────

class RefLeaderboardView(discord.ui.View):
    def __init__(self, admin_uid: str):
        super().__init__(timeout=None)
        self.admin_uid = admin_uid
    
    @discord.ui.button(label="🔄 Refresh", style=discord.ButtonStyle.primary)
    async def refresh_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        uid = str(interaction.user.id)
        if uid != self.admin_uid:
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Not your leaderboard."), ephemeral=True)
        
        embed = build_referral_leaderboard_embed()
        await interaction.response.edit_message(embed=embed, view=self)


def build_referral_leaderboard_embed() -> discord.Embed:
    """Build the referral leaderboard embed"""
    all_refs = load_referrals()
    
    # Sort by referral count
    referrers = []
    for user_id, data in all_refs.items():
        ref_count = len(data.get("referrals", []))
        if ref_count > 0:  # Only show users with at least 1 referral
            tier = get_referral_tier(user_id)
            tier_name = REFERRAL_TIERS[tier]["name"]
            referrers.append({
                "uid": user_id,
                "count": ref_count,
                "tier": tier_name,
                "tier_num": tier
            })
    
    # Sort by count (descending)
    referrers.sort(key=lambda x: x["count"], reverse=True)
    
    # Build leaderboard
    embed = discord.Embed(color=discord.Color.gold(), title="🏆 Referral Leaderboard")
    embed.description = "> Top referrers ranked by total referrals earned"
    
    if not referrers:
        embed.add_field(name="Empty", value="No referrals yet!", inline=False)
        return embed
    
    # Show top 10
    leaderboard_text = ""
    for i, ref in enumerate(referrers[:10], 1):
        medal = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else f"{i:02d}."
        tier_icon = {"Rookie": "🌱", "Bronze": "🥉", "Silver": "🥈", "Gold": "🥇", "Platinum": "👑"}[ref["tier"]]
        leaderboard_text += f"{medal} <@{ref['uid']}> — **{ref['count']}** refs | {tier_icon} **{ref['tier']}**\n"
    
    embed.add_field(name="Top 10 Referrers", value=leaderboard_text or "No data", inline=False)
    
    # Stats
    total_referrals = sum(ref["count"] for ref in referrers)
    total_referrers = len(referrers)
    platinum_count = sum(1 for ref in referrers if ref["tier_num"] == 4)
    
    stats_text = f"> **Total Referrals:** {total_referrals}\n> **Total Referrers:** {total_referrers}\n> **Platinum Tier:** {platinum_count}"
    embed.add_field(name="📊 Stats", value=stats_text, inline=False)
    
    embed.set_footer(text=f"Updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} | Auto-refreshed when referrals change")
    return embed


@bot.slash_command(name="refleaderboard", description="View the referral leaderboard (Admin only).")
async def refleaderboard(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    
    # Admin only
    if not can_manage_bot(uid):
        return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Admin only."), ephemeral=True)
    
    embed = build_referral_leaderboard_embed()
    view = RefLeaderboardView(uid)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=False)
    try:
        message = await interaction.original_response()
        entry = {"admin_uid": uid, "channel_id": message.channel.id, "message_id": message.id}
        if entry not in REFERRAL_LEADERBOARD_MESSAGES:
            REFERRAL_LEADERBOARD_MESSAGES.append(entry)
    except Exception:
        pass


# ─── Referral Link Usage (Users join with referrer ID) ─────────────────────

@bot.slash_command(name="joinref", description="Join the bot using a referral code from /referral")
@discord.option("referrer_id", description="The referrer's referral code", required=True)
async def joinref(interaction: discord.Interaction, referrer_id: str):
    """User joins the bot network using a referrer's code"""
    new_user_id = str(interaction.user.id)
    referrer_code = referrer_id.strip()
    
    if is_restricted(new_user_id):
        return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> 🚫 You are restricted."), ephemeral=True)
    
    if not referrer_code.isdigit() or len(referrer_code) != REFERRAL_CODE_LENGTH:
        return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Invalid referral code. Use the 8-digit code from `/referral`."), ephemeral=True)
    
    all_refs = load_referrals()
    if new_user_id in all_refs:
        existing_referrer = all_refs[new_user_id].get("referrer")
        already_since = all_refs[new_user_id].get("createdAt")
        if existing_referrer:
            return await interaction.response.send_message(
                embed=discord.Embed(color=discord.Color.orange(), description=f"> ⚠️ You already joined through a referral link!\n> Your referrer: <@{existing_referrer}>"),
                ephemeral=True)
        return await interaction.response.send_message(
            embed=discord.Embed(color=discord.Color.orange(), title="👤 Already a Member", description="> You already have a bot profile and cannot use `/joinref` again."),
            ephemeral=True)
    
    referrer_uid = find_referrer_by_code(referrer_code)
    if not referrer_uid:
        return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Invalid referral code. Make sure you copied it correctly."), ephemeral=True)
    if referrer_uid == new_user_id:
        return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ You can't refer yourself!"), ephemeral=True)
    
    record_referral(referrer_uid, new_user_id)
    
    # Get updated tier for referrer
    referrer_tier = get_referral_tier(referrer_uid)
    referrer_tier_info = REFERRAL_TIERS[referrer_tier]
    new_refs_count = len(get_referral_data(referrer_uid).get("referrals", []))
    
    # New user welcome
    new_user_embed = discord.Embed(color=discord.Color.green(), title="✨ Welcome! You've Been Referred")
    new_user_embed.description = f"> Welcome to the bot network! You joined through a referral code.\n> Your referrer: **<@{referrer_uid}>**"
    new_user_embed.add_field(name="🎯 What's Next?", value="> • Use `/free` to claim a free 30-min trial\n> • Use `/vouch`, `/chat`, or `/trade` to start sessions\n> • Check out `/referral` to refer others!", inline=False)
    
    # Referrer notification
    try:
        referrer_user = await bot.fetch_user(int(referrer_uid))
        referrer_embed = discord.Embed(color=discord.Color.gold(), title="🎉 New Referral!")
        referrer_embed.description = f"> <@{new_user_id}> joined using your referral code!"
        referrer_embed.add_field(name="📊 Your Stats", value=f"> • Total referrals: **{new_refs_count}**\n> • Tier: **{referrer_tier_info['name']}**\n> • Bonus slots: **+{referrer_tier_info['bonus_slots']}**", inline=False)
        
        if referrer_tier < 4:
            next_tier = REFERRAL_TIERS[referrer_tier + 1]
            refs_to_next = next_tier["refs_required"] - new_refs_count
            referrer_embed.add_field(name="🚀 Next Tier", value=f"> **{refs_to_next}** more referrals to reach **{next_tier['name']}**!", inline=False)
        
        try:
            await referrer_user.send(embed=referrer_embed)
        except discord.Forbidden:
            pass  # User has DMs closed
    except:
        pass  # Could not fetch referrer
    
    await interaction.response.send_message(embed=new_user_embed, ephemeral=True)
    refresh_referral_leaderboards()


@bot.slash_command(name="validtokens", description="Check how many tokens in tokens.txt are valid.")

async def validtokens(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    if not can_manage_bot(uid):
        return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> ❌ Admin only."), ephemeral=True)

    all_tokens = get_tokens()
    if not all_tokens:
        return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.yellow(), description="> ℹ️ No tokens in tokens.txt."), ephemeral=True)

    await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.blue(), description=f"> 🔍 Checking {len(all_tokens)} tokens..."), ephemeral=True)

    valid_count = 0
    invalid_count = 0
    BASE = "https://discord.com/api/v9"

    async with aiohttp.ClientSession() as http:
        for token in all_tokens:
            try:
                async with http.get(f"{BASE}/users/@me", headers=_token_headers(token), timeout=aiohttp.ClientTimeout(total=5)) as res:
                    if res.status == 200:
                        valid_count += 1
                    else:
                        invalid_count += 1
            except Exception:
                invalid_count += 1

    embed = discord.Embed(color=discord.Color.green() if valid_count > 0 else discord.Color.red(),
                          title="Token Validation Results",
                          description=f"**Valid:** {valid_count}\n**Invalid:** {invalid_count}")
    await safe_edit_message(interaction, embed=embed)


@bot.slash_command(name="clean", description="Admin: remove invalid tokens from token files")
async def clean(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    if not can_manage_bot(uid):
        return await safe_send_message(interaction, embed=discord.Embed(color=discord.Color.red(), description="> ❌ Admin only."), ephemeral=True)

    await interaction.response.defer(ephemeral=True)

    files = [
        (TOKENS_FILE, "tokens.txt"),
        (ONTOKENS_FILE, "ontokens.txt"),
        (OFFTOKENS_FILE, "offtokens.txt"),
        (BOOSTERS_FILE, "boosters.txt"),
    ]

    summary_lines = []

    async with aiohttp.ClientSession() as http:
        for path, display in files:
            lines = [l for l in read_lines(path) if l.strip()]
            if not lines:
                summary_lines.append(f"> **{display}**: No tokens found.")
                continue

            valid_tokens = []
            invalid_tokens = []

            for token in lines:
                # quick format check
                if not is_valid_token_string(token):
                    invalid_tokens.append(token)
                    continue

                try:
                    async with http.get("https://discord.com/api/v9/users/@me", headers=_token_headers(token), timeout=aiohttp.ClientTimeout(total=5)) as res:
                        if res.status == 200:
                            valid_tokens.append(token)
                        else:
                            invalid_tokens.append(token)
                except Exception:
                    invalid_tokens.append(token)

            # overwrite file with valid tokens only
            if valid_tokens:
                path.write_text("\n".join(valid_tokens) + "\n", encoding="utf-8")
            else:
                # clear file
                path.write_text("", encoding="utf-8")

            summary_lines.append(f"> **{display}**: Kept **{len(valid_tokens)}**, Removed **{len(invalid_tokens)}**")

    embed = discord.Embed(color=discord.Color.green(), title="🧹 Token Clean Complete",
                          description="\n".join(summary_lines))
    await interaction.followup.send(embed=embed, ephemeral=True)


@bot.slash_command(name="ping", description="Check if the bot is online.")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(embed=discord.Embed(color=discord.Color.green(), description=f"> 🏓 Pong! Latency: **{round(bot.latency*1000)}ms**"), ephemeral=True)

@bot.slash_command(name="help", description="Show all available bot commands.")
async def help(interaction: discord.Interaction):
    commands = sorted(COMMANDS, key=lambda c: c["name"])
    if not commands:
        return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.yellow(), description="> ℹ️ No available commands found."), ephemeral=True)
    lines = [f"`/{cmd['name']}` — {cmd['description']}" for cmd in commands]
    embed = discord.Embed(color=discord.Color.blurple(), title="Bot Commands", description="\n".join(lines))
    await interaction.response.send_message(embed=embed, ephemeral=True)


# ─── Free Trial Adv Panel ──────────────────────────────────────────────────────

class FreeAdvClaimView(discord.ui.View):
    def __init__(self, uid: str):
        super().__init__(timeout=None)
        self.uid = uid
    
    @discord.ui.button(label="🎁 Claim Free Adv Trial", style=discord.ButtonStyle.success)
    async def claim_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        uid = str(interaction.user.id)
        if is_restricted(uid):
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> 🚫 You are restricted."), ephemeral=True)
        
        # Check if user already claimed trial
        if has_claimed_trial(uid):
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ You have already claimed the free trial!"), ephemeral=True)
        
        # Generate 30-minute trial key
        trial_expiry = (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat()
        key = generate_key()
        keys = load_keys()
        keys[key] = {
            "keyType": "autoadv",
            "slots": 1,
            "allowDmReply": False,
            "duration": "trial",
            "variant": "trial",
            "used": False,
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "expiresAt": trial_expiry,
            "redeemedBy": None,
            "accounts": [],
            "isTrial": True
        }
        save_keys(keys)
        
        # Record the claim
        record_trial_claim(uid)
        
        embed = discord.Embed(color=discord.Color.gold(), title="⏰ Free Trial Auto Adv Key — 30 Minutes")
        embed.description = "> Your free trial key is ready! Redeem it quickly before it expires.\n> Starting now, you have **30 minutes** to use this key."
        embed.add_field(name="🔑 Your Key", value=f"```{key}```", inline=False)
        embed.add_field(name="⏱️ Expires", value=format_expiry(trial_expiry), inline=True)
        embed.add_field(name="📦 Slots", value="**1 account slot**", inline=True)
        embed.add_field(name="💬 Auto DM Reply", value="**Disabled**", inline=True)
        embed.set_footer(text="Redeem with /autoadv")
        
        await interaction.response.send_message(embed=embed, ephemeral=False)


@bot.slash_command(name="free", description="Open the free Auto Adv trial panel")
async def free(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    
    if is_restricted(uid):
        return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> 🚫 You are restricted."), ephemeral=True)
    
    embed = discord.Embed(color=discord.Color.blurple(), title="🎁 Free Auto Adv Trial")
    embed.description = "> Get a **free 30-minute trial** of Auto Adv!\n> Run up to **1 account** with no auto-reply for a limited time.\n\n**Don't miss out — expires in 30 minutes after claim!**"
    embed.add_field(name="✨ What You Get", value="> • 1 Auto Adv account slot\n> • 30-minute access\n> • Limited time only", inline=False)
    
    view = FreeAdvClaimView(uid)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=False)


# ─── Adv User / Balance System ────────────────────────────────────────────────

ADV_USERS_FILE = BASE_DIR / "adv_users.json"
LTC_ADDR_FILE  = BASE_DIR / "ltcaddress.txt"

ADV_PRICES = {
    "1w":       {"V1": 1, "V2": 1.65, "V3": 2.5},
    "1m":       {"V1": 2.00, "V2": 2.75, "V3": 3.50},
    "lifetime": {"V1": 3.50, "V2": 5.50, "V3": 9.00},
}
ADV_TIER_PERKS = {
    "V1": {"slots": 1, "allowDmReply": False, "name": "Starter"},
    "V2": {"slots": 2, "allowDmReply": True,  "name": "Standard"},
    "V3": {"slots": 5, "allowDmReply": True,  "name": "Pro"},
}
ADV_DURATION_LABELS = {"1w": "1 Week", "1m": "1 Month", "lifetime": "Lifetime"}
RESELLER_KEY_PRICE  = 3.0

def load_adv_users():
    if not ADV_USERS_FILE.exists():
        return []
    try:
        return json.loads(ADV_USERS_FILE.read_text("utf-8"))
    except Exception:
        return []

def save_adv_users(users):
    ADV_USERS_FILE.write_text(json.dumps(users, indent=2), "utf-8")

def get_adv_user(uid: str) -> dict:
    users = load_adv_users()
    u = next((x for x in users if x["id"] == uid), None)
    if not u:
        u = {"id": uid, "balance": 0.0, "infiniteBalance": False, "generatedAdvKeys": 0, "generatedResellerKeys": 0}
        users.append(u)
        save_adv_users(users)
    return u

def update_adv_user(uid: str, **kwargs) -> dict:
    users = load_adv_users()
    u = next((x for x in users if x["id"] == uid), None)
    if not u:
        u = {"id": uid, "balance": 0.0, "infiniteBalance": False, "generatedAdvKeys": 0, "generatedResellerKeys": 0}
        users.append(u)
    u.update(kwargs)
    save_adv_users(users)
    return u

def fmt_bal(u: dict) -> str:
    return "∞" if u.get("infiniteBalance") else f"${u.get('balance', 0):.2f}"

def get_ltc_address() -> str:
    if LTC_ADDR_FILE.exists():
        v = LTC_ADDR_FILE.read_text("utf-8").strip()
        if v:
            return v
    return os.environ.get("LTC_ADDRESS", "")

def set_ltc_address(addr: str):
    LTC_ADDR_FILE.write_text(addr.strip(), "utf-8")

# ─── Admin Adv Manage ─────────────────────────────────────────────────────────

class AdminAdvDashboardView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

def build_adv_admin_dashboard_embed():
    users    = load_adv_users()
    lics     = load_adv_licenses()
    all_keys = load_keys()
    adv_keys = [v for v in all_keys.values() if v.get("keyType") == "autoadv" and not v.get("used") and not is_key_expired(v)]
    resellers = [u for u in users if u.get("isReseller")]
    total_bal = sum(u.get("balance", 0) for u in users if not u.get("infiniteBalance"))
    lic_list = list(lics.values())
    active_lics = [
    l for l in lic_list
    if not l.get("revoked")
    and (
        not l.get("expiresAt")
        or datetime.fromisoformat(l["expiresAt"]).replace(tzinfo=timezone.utc) > datetime.now(timezone.utc)
    )
] 
    inf_users = [u for u in users if u.get("infiniteBalance")]
    e = discord.Embed(title="📊 Admin Dashboard — Auto Adv", color=discord.Color.blurple())
    e.add_field(name="Licenses", value=f"Total: `{len(lics)}`\nActive: `{len(active_lics)}`\nRevoked: `{len(lics) - len(active_lics)}`", inline=True)
    e.add_field(name="Unused Adv Keys", value=f"`{len(adv_keys)}`", inline=True)
    e.add_field(name="Resellers", value=f"`{len(resellers)}`", inline=True)
    e.add_field(name="Balances", value=f"Total Held: `${total_bal:.2f}`\nInfinite Users: `{len(inf_users)}`", inline=True)
    e.add_field(name="LTC Address", value=f"`{get_ltc_address() or 'Not set'}`", inline=False)
    e.set_footer(text=f"Updated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    return e

class AdminAdvAddBalModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Add Balance")
        self.add_item(discord.ui.InputText(label="User ID", placeholder="Discord user ID", required=True))
        self.add_item(discord.ui.InputText(label="Amount ($)", placeholder="e.g. 5.00", required=True))
    async def callback(self, interaction: discord.Interaction):
        uid    = self.children[0].value.strip()
        try:   amt = float(self.children[1].value.strip())
        except ValueError:
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Invalid amount."), ephemeral=True)
        if amt <= 0:
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Amount must be positive."), ephemeral=True)
        u = get_adv_user(uid)
        new_bal = u.get("balance", 0) + amt
        update_adv_user(uid, balance=new_bal)
        await interaction.response.send_message(embed=discord.Embed(color=discord.Color.green(), description=f"> ✅ Added **${amt:.2f}** to <@{uid}>.\n> New balance: **${new_bal:.2f}**"), ephemeral=True)

class AdminAdvSetBalModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Set Balance")
        self.add_item(discord.ui.InputText(label="User ID", placeholder="Discord user ID", required=True))
        self.add_item(discord.ui.InputText(label="Amount ($)", placeholder="e.g. 10.00", required=True))
    async def callback(self, interaction: discord.Interaction):
        uid    = self.children[0].value.strip()
        try:   amt = float(self.children[1].value.strip())
        except ValueError:
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Invalid amount."), ephemeral=True)
        if amt < 0:
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Amount cannot be negative."), ephemeral=True)
        update_adv_user(uid, balance=amt, infiniteBalance=False)
        await interaction.response.send_message(embed=discord.Embed(color=discord.Color.green(), description=f"> ✅ Set balance of <@{uid}> to **${amt:.2f}**."), ephemeral=True)

class AdminAdvRemoveBalModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Remove Balance")
        self.add_item(discord.ui.InputText(label="User ID", placeholder="Discord user ID", required=True))
        self.add_item(discord.ui.InputText(label="Amount ($)", placeholder="e.g. 2.00", required=True))
    async def callback(self, interaction: discord.Interaction):
        uid = self.children[0].value.strip()
        try: amt = float(self.children[1].value.strip())
        except ValueError:
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Invalid amount."), ephemeral=True)
        u = get_adv_user(uid)
        new_bal = max(0.0, u.get("balance", 0) - amt)
        update_adv_user(uid, balance=new_bal)

        u = get_adv_user(uid)
        new_bal = max(0.0, u.get("balance", 0) - amt)
        update_adv_user(uid, balance=new_bal)
        await interaction.response.send_message(embed=discord.Embed(color=discord.Color.green(), description=f"> ✅ Removed **${amt:.2f}** from <@{uid}>.\n> New balance: **${new_bal:.2f}**"), ephemeral=True)

class AdminAdvBulkKeyModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Generate Bulk Adv Keys")
        self.add_item(discord.ui.InputText(label="Duration (1w / 1m / lifetime)", placeholder="1w", required=True))
        self.add_item(discord.ui.InputText(label="Variant (V1 / V2 / V3)", placeholder="V1", required=True))
        self.add_item(discord.ui.InputText(label="Amount (1–50)", placeholder="5", required=True))
        self.add_item(discord.ui.InputText(label="Allow DM Reply? (yes/no)", placeholder="no  (leave blank = no)", required=False))
    async def callback(self, interaction: discord.Interaction):
        dur    = self.children[0].value.strip().lower()
        var    = self.children[1].value.strip().upper()
        try:   amt = max(1, min(50, int(self.children[2].value.strip())))
        except ValueError:
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Invalid amount."), ephemeral=True)
        allow_dm = self.children[3].value.strip().lower() in ("yes", "y", "true", "1")
        if dur not in ADV_DURATION_LABELS:
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Duration must be `1w`, `1m`, or `lifetime`."), ephemeral=True)
        if var not in ADV_TIER_PERKS:
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Variant must be `V1`, `V2`, or `V3`."), ephemeral=True)
        perks = ADV_TIER_PERKS[var]
        await interaction.response.defer(ephemeral=True)
        keys_data = load_keys()
        generated = []
        for _ in range(amt):
            k = str(uuid.uuid4()).upper()[:16]
            keys_data[k] = {
                "keyType": "autoadv", "used": False, "slots": perks["slots"],
                "allowDmReply": allow_dm, "duration": dur, "variant": var,
                "createdAt": datetime.now(timezone.utc).isoformat(),
                "expiresAt": None, "redeemedBy": None, "accounts": []
            }
            generated.append(k)
        save_keys(keys_data)
        try:
            dm = await interaction.user.create_dm()
            chunks, cur = [], ""
            for k in generated:
                line = f"`{k}`\n"
                if len(cur + line) > 1800: chunks.append(cur); cur = ""
                cur += line
            if cur: chunks.append(cur)
            for i, c in enumerate(chunks):
                title = f"🔑 Bulk Adv Keys ({i+1}/{len(chunks)})" if len(chunks) > 1 else "🔑 Bulk Adv Keys"
                await dm.send(embed=discord.Embed(color=discord.Color.green(), title=title, description=c))
            await interaction.followup.send(embed=discord.Embed(color=discord.Color.green(), description=f"> ✅ **{amt}** `{var}` {ADV_DURATION_LABELS[dur]} adv key(s) sent to your DMs."), ephemeral=True)
        except discord.Forbidden:
            key_txt = "\n".join(f"`{k}`" for k in generated[:30])
            await interaction.followup.send(embed=discord.Embed(color=discord.Color.orange(), title="🔑 Keys Generated (DMs Closed)", description=key_txt), ephemeral=True)

class AdminAdvInfBalModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Give Infinite Balance")
        self.add_item(discord.ui.InputText(label="User ID", placeholder="Discord user ID", required=True))
    async def callback(self, interaction: discord.Interaction):
        uid = self.children[0].value.strip()
        update_adv_user(uid, infiniteBalance=True)
        await interaction.response.send_message(embed=discord.Embed(color=discord.Color.green(), description=f"> ✅ <@{uid}> now has **infinite balance**."), ephemeral=True)

class AdminAdvResetUserModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Reset User")
        self.add_item(discord.ui.InputText(label="User ID", placeholder="Discord user ID", required=True))
    async def callback(self, interaction: discord.Interaction):
        uid = self.children[0].value.strip()
        users = load_adv_users()
        users = [u for u in users if u["id"] != uid]
        save_adv_users(users)
        lics = load_adv_licenses()
        lics.pop(uid, None)
        save_adv_licenses(lics)
        await interaction.response.send_message(embed=discord.Embed(color=discord.Color.green(), description=f"> ✅ All adv data reset for <@{uid}>."), ephemeral=True)

class AdminAdvSetLtcModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Set LTC Deposit Address")
        self.add_item(discord.ui.InputText(label="LTC Address", placeholder="Ltc...", required=True))
    async def callback(self, interaction: discord.Interaction):
        addr = self.children[0].value.strip()
        set_ltc_address(addr)
        await interaction.response.send_message(embed=discord.Embed(color=discord.Color.green(), description=f"> ✅ LTC deposit address set to:\n`{addr}`"), ephemeral=True)

class AdminAdvEditUserModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Edit User Auto Adv")
        self.add_item(discord.ui.InputText(label="User ID", placeholder="123456789012345678", required=True))
    async def callback(self, interaction: discord.Interaction):
        try:
            user_id = int(self.children[0].value.strip())
        except ValueError:
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Invalid user ID."), ephemeral=True)
        
        licenses = load_adv_licenses()
        lic = licenses.get(str(user_id))
        if not lic:
            # Check if user has redeemed an adv key
            keys = load_keys()
            user_keys = [k for k, v in keys.items() if v.get("redeemedBy") == str(user_id) and v.get("keyType") == "autoadv"]
            if user_keys:
                # Recreate license from the last redeemed key
                key = user_keys[-1]
                v = keys[key]
                slots = v.get("slots", 1)
                allow_dm = v.get("allowDmReply", False)
                expires_at = v.get("expiresAt")
                licenses[str(user_id)] = {"keyCode": key, "slots": slots, "allowDmReply": allow_dm,
                                         "expiresAt": expires_at, "accounts": []}
                save_adv_licenses(licenses)
                lic = licenses[str(user_id)]
            else:
                return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ User has no Auto Adv license or redeemed key."), ephemeral=True)
        
        # Show user edit view
        view = AdminAdvEditUserView(str(user_id), lic)
        embed = discord.Embed(color=discord.Color.blurple(), title=f"Editing <@{user_id}>")
        embed.add_field(name="Expires", value=format_expiry(lic.get("expiresAt")), inline=True)
        embed.add_field(name="Slots", value=f"{len(lic.get('accounts', []))}/{lic.get('slots', 1)}", inline=True)
        embed.add_field(name="Accounts", value=len(lic.get("accounts", [])), inline=True)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class AdminAdvEditUserView(discord.ui.View):
    def __init__(self, user_id: str, lic: dict):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.lic = lic
        
    @discord.ui.button(label="Edit License", style=discord.ButtonStyle.primary, row=0)
    async def edit_license(self, button: discord.ui.Button, interaction: discord.Interaction):
        await safe_send_modal(interaction, AdminAdvEditLicenseModal(self.user_id, self.lic))
    
    @discord.ui.button(label="Add Account", style=discord.ButtonStyle.success, row=0)
    async def add_account(self, button: discord.ui.Button, interaction: discord.Interaction):
        await safe_send_modal(interaction, AddAdvAccountModal(self.user_id, allow_dm=True))
    
    @discord.ui.button(label="Manage Accounts", style=discord.ButtonStyle.secondary, row=0)
    async def manage_accounts(self, button: discord.ui.Button, interaction: discord.Interaction):
        accounts = self.lic.get("accounts", [])
        if not accounts:
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.yellow(), description="> ℹ️ No accounts configured."), ephemeral=True)
        options = [discord.SelectOption(label=acc.get("name", f"Account {i+1}")[:100], value=acc["id"]) for i, acc in enumerate(accounts)]
        select = discord.ui.Select(placeholder="Select account to manage", options=options[:25])
        async def select_cb(sel_interaction: discord.Interaction):
            acc_id = select.values[0]
            acc = next((a for a in accounts if a["id"] == acc_id), None)
            if not acc:
                return await sel_interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Account not found."), ephemeral=True)
            view = AdvPanelView(self.user_id, acc_id)
            embed, _ = build_adv_panel(self.user_id)
            await sel_interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        select.callback = select_cb
        view = discord.ui.View()
        view.add_item(select)
        await interaction.response.send_message("Select an account to manage:", view=view, ephemeral=True)
    
    @discord.ui.button(label="Delete License", style=discord.ButtonStyle.danger, row=1)
    async def delete_license(self, button: discord.ui.Button, interaction: discord.Interaction):
        # Confirm deletion
        view = ConfirmDeleteView(self.user_id)
        await interaction.response.send_message(
            embed=discord.Embed(color=discord.Color.red(), title="⚠️ Confirm Deletion", 
                               description=f"Are you sure you want to delete <@{self.user_id}>'s Auto Adv license?\nThis will stop all accounts and remove all data."),
            view=view, ephemeral=True
        )

class ConfirmDeleteView(discord.ui.View):
    def __init__(self, user_id: str):
        super().__init__(timeout=60)
        self.user_id = user_id
    
    @discord.ui.button(label="Yes, Delete", style=discord.ButtonStyle.danger)
    async def confirm_delete(self, button: discord.ui.Button, interaction: discord.Interaction):
        licenses = load_adv_licenses()
        if self.user_id in licenses:
            # Stop all accounts
            stop_all_adv(self.user_id)
            del licenses[self.user_id]
            save_adv_licenses(licenses)
            await interaction.response.send_message(embed=discord.Embed(color=discord.Color.green(), description=f"> ✅ <@{self.user_id}>'s license deleted."), ephemeral=True)
        else:
            await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ License not found."), ephemeral=True)
    
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel_delete(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message(embed=discord.Embed(color=discord.Color.blue(), description="> ℹ️ Deletion cancelled."), ephemeral=True)

class AdminAdvEditLicenseModal(discord.ui.Modal):
    def __init__(self, user_id: str, lic: dict):
        super().__init__(title=f"Edit License for <@{user_id}>")
        self.user_id = user_id
        self.lic = lic
        self.add_item(discord.ui.InputText(label="Expires At (ISO format)", value=lic.get("expiresAt", ""), placeholder="2026-12-31T23:59:59", required=True))
        self.add_item(discord.ui.InputText(label="Slots", value=str(lic.get("slots", 1)), placeholder="1", required=True))
    async def callback(self, interaction: discord.Interaction):
        expires_at = self.children[0].value.strip()
        try:
            slots = int(self.children[1].value.strip())
        except ValueError:
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Invalid slots number."), ephemeral=True)
        
        licenses = load_adv_licenses()
        if self.user_id in licenses:
            licenses[self.user_id]["expiresAt"] = expires_at
            licenses[self.user_id]["slots"] = slots
            save_adv_licenses(licenses)
            await interaction.response.send_message(embed=discord.Embed(color=discord.Color.green(), description=f"> ✅ License updated for <@{self.user_id}>."), ephemeral=True)
        else:
            await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ License not found."), ephemeral=True)

class AdminAdvViewResellersConfirm(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)

class AdminAdvManageView(discord.ui.View):
    def __init__(self, uid: str):
        super().__init__(timeout=120)
        self.uid = uid
        buttons = [
            ("📊 Dashboard",        "aam_dashboard",  discord.ButtonStyle.blurple,   0),
            ("➕ Add Balance",      "aam_addbal",     discord.ButtonStyle.success,   0),
            ("💰 Set Balance",      "aam_setbal",     discord.ButtonStyle.secondary, 0),
            ("💸 Remove Balance",   "aam_removebal",  discord.ButtonStyle.danger,    0),
            ("🔑 Bulk Adv Key",     "aam_bulkkey",    discord.ButtonStyle.primary,   1),
            ("♾️ Infinite Bal",     "aam_infbal",     discord.ButtonStyle.success,   1),
            ("🔄 Reset User",       "aam_resetuser",  discord.ButtonStyle.danger,    1),
            ("📋 View Resellers",   "aam_resellers",  discord.ButtonStyle.secondary, 1),
            ("🏦 Set LTC Address",  "aam_setltc",     discord.ButtonStyle.primary,   2),
            ("🗑️ Full Reset",       "aam_fullreset",  discord.ButtonStyle.danger,    2),
            ("👤 Edit User",        "aam_edituser",   discord.ButtonStyle.primary,   2),
        ]
        for label, cid, style, row in buttons:
            btn = discord.ui.Button(label=label, custom_id=cid, style=style, row=row)
            btn.callback = self._make_cb(cid)
            self.add_item(btn)

    def _make_cb(self, cid: str):
        async def cb(interaction: discord.Interaction):
            uid = str(interaction.user.id)
            if not can_manage_bot(uid):
                return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Not authorized."), ephemeral=True)
            if cid == "aam_dashboard":
                e = build_adv_admin_dashboard_embed()
                return await interaction.response.send_message(embed=e, ephemeral=True)
            if cid == "aam_addbal":
                await safe_send_modal(interaction, AdminAdvAddBalModal())
                return
            if cid == "aam_setbal":
                await safe_send_modal(interaction, AdminAdvSetBalModal())
                return
            if cid == "aam_removebal":
                await safe_send_modal(interaction, AdminAdvRemoveBalModal())
                return
            if cid == "aam_bulkkey":
                await safe_send_modal(interaction, AdminAdvBulkKeyModal())
                return
            if cid == "aam_infbal":
                await safe_send_modal(interaction, AdminAdvInfBalModal())
                return
            if cid == "aam_resetuser":
                return await interaction.response.send_modal(AdminAdvResetUserModal())
            if cid == "aam_setltc":
                return await interaction.response.send_modal(AdminAdvSetLtcModal())
            if cid == "aam_resellers":
                users = load_adv_users()
                if not users:
                    return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.yellow(), description="> ℹ️ No users in the balance system yet."), ephemeral=True)
                await interaction.response.defer(ephemeral=True)
                chunks, cur = [], ""
                for u in users:
                    bal   = fmt_bal(u)
                    line  = f"<@{u['id']}> — Bal: **{bal}** | Adv Keys: `{u.get('generatedAdvKeys',0)}` | Reseller Keys: `{u.get('generatedResellerKeys',0)}`\n"
                    if len(cur + line) > 1800: chunks.append(cur); cur = ""
                    cur += line
                if cur: chunks.append(cur)
                try:
                    dm = await interaction.user.create_dm()
                    for i, c in enumerate(chunks):
                        t = f"📋 Reseller Users ({i+1}/{len(chunks)})" if len(chunks) > 1 else "📋 Reseller Users"
                        await dm.send(embed=discord.Embed(color=discord.Color.blurple(), title=t, description=c))
                    return await interaction.followup.send(embed=discord.Embed(color=discord.Color.green(), description=f"> ✅ **{len(users)}** user(s) sent to your DMs."), ephemeral=True)
                except discord.Forbidden:
                    txt = "\n".join(f"<@{u['id']}> — **{fmt_bal(u)}**" for u in users[:30])
                    return await interaction.followup.send(embed=discord.Embed(color=discord.Color.blurple(), title="📋 Reseller Users", description=txt or "None"), ephemeral=True)
            if cid == "aam_fullreset":
                if not is_owner(uid):
                    return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Only the **owner** can perform a full reset."), ephemeral=True)
                await interaction.response.defer(ephemeral=True)
                save_adv_users([])
                save_adv_licenses({})
                keys_data = load_keys()
                cleared = {k: v for k, v in keys_data.items() if v.get("keyType") != "autoadv"}
                save_keys(cleared)
                await interaction.followup.send(embed=discord.Embed(color=discord.Color.red(), title="⚠️ Full Reset Complete", description="> All adv users, licenses, and unused adv keys have been wiped."), ephemeral=True)
            if cid == "aam_edituser":
                await safe_send_modal(interaction, AdminAdvEditUserModal())
                return
        return cb

# ─── Reseller Adv Panel ────────────────────────────────────────────────────────

class ResellerAdvGenKeyModal(discord.ui.Modal):
    def __init__(self, uid: str):
        super().__init__(title="Generate Adv Key")
        self.uid = uid
        self.add_item(discord.ui.InputText(label="Duration (1w / 1m / lifetime)", placeholder="1w", required=True))
        self.add_item(discord.ui.InputText(label="Variant (V1 / V2 / V3)", placeholder="V1", required=True))
        self.add_item(discord.ui.InputText(label="Amount (1–10)", placeholder="1", required=True))
    async def callback(self, interaction: discord.Interaction):
        dur = self.children[0].value.strip().lower()
        var = self.children[1].value.strip().upper()
        try: amt = max(1, min(10, int(self.children[2].value.strip())))
        except ValueError:
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Invalid amount."), ephemeral=True)
        if dur not in ADV_PRICES:
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Duration must be `1w`, `1m`, or `lifetime`."), ephemeral=True)
        if var not in ADV_TIER_PERKS:
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Variant must be `V1`, `V2`, or `V3`."), ephemeral=True)
        unit_price  = ADV_PRICES[dur][var]
        total_cost  = unit_price * amt
        u = get_adv_user(self.uid)
        if not u.get("infiniteBalance") and u.get("balance", 0) < total_cost:
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description=f"> ❌ Insufficient balance.\n> Need: **${total_cost:.2f}** | Have: **{fmt_bal(u)}**"), ephemeral=True)
        await interaction.response.defer(ephemeral=True)
        if not u.get("infiniteBalance"):
            update_adv_user(self.uid, balance=u["balance"] - total_cost, generatedAdvKeys=u.get("generatedAdvKeys", 0) + amt)
        else:
            update_adv_user(self.uid, generatedAdvKeys=u.get("generatedAdvKeys", 0) + amt)
        perks = ADV_TIER_PERKS[var]
        keys_data = load_keys()
        generated = []
        for _ in range(amt):
            k = str(uuid.uuid4()).upper()[:16]
            keys_data[k] = {
                "keyType": "autoadv", "used": False, "slots": perks["slots"],
                "allowDmReply": perks["allowDmReply"], "duration": dur, "variant": var,
                "createdAt": datetime.now(timezone.utc).isoformat(),
                "expiresAt": None, "redeemedBy": None, "accounts": []
            }
            generated.append(k)
        save_keys(keys_data)
        u2 = get_adv_user(self.uid)
        try:
            dm = await interaction.user.create_dm()
            for k in generated:
                await dm.send(embed=discord.Embed(color=discord.Color.green(), title="🔑 Your Adv Key", description=f"`{k}`\n**{var}** — {ADV_DURATION_LABELS[dur]}"))
            await interaction.followup.send(embed=discord.Embed(color=discord.Color.green(), description=f"> ✅ **{amt}** key(s) sent to your DMs.\n> Remaining balance: **{fmt_bal(u2)}**"), ephemeral=True)
        except discord.Forbidden:
            key_txt = "\n".join(f"`{k}`" for k in generated)
            await interaction.followup.send(embed=discord.Embed(color=discord.Color.orange(), title="🔑 Keys (DMs Closed)", description=key_txt + f"\n\nRemaining balance: **{fmt_bal(u2)}**"), ephemeral=True)

class ResellerAdvView(discord.ui.View):
    def __init__(self, uid: str):
        super().__init__(timeout=120)
        self.uid = uid
        buttons = [
            ("👤 Profile",         "rsa_profile",  discord.ButtonStyle.blurple,   0),
            ("💰 Deposit LTC",     "rsa_deposit",  discord.ButtonStyle.success,   0),
            ("🔑 Generate Key",    "rsa_genkey",   discord.ButtonStyle.primary,   0),
            ("💵 Prices",          "rsa_prices",   discord.ButtonStyle.secondary, 0),
        ]
        for label, cid, style, row in buttons:
            btn = discord.ui.Button(label=label, custom_id=cid, style=style, row=row)
            btn.callback = self._make_cb(cid)
            self.add_item(btn)

    def _make_cb(self, cid: str):
        async def cb(interaction: discord.Interaction):
            if str(interaction.user.id) != self.uid:
                return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Not your panel."), ephemeral=True)
            u = get_adv_user(self.uid)
            if cid == "rsa_profile":
                e = discord.Embed(title="👤 Reseller Profile — Auto Adv", color=discord.Color.blurple())
                e.add_field(name="Balance",    value=f"**{fmt_bal(u)}**",                         inline=True)
                e.add_field(name="Adv Keys Generated", value=f"`{u.get('generatedAdvKeys', 0)}`", inline=True)
                return await interaction.response.send_message(embed=e, ephemeral=True)
            if cid == "rsa_deposit":
                addr = get_ltc_address()
                if not addr:
                    return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ No LTC deposit address is set. Contact the owner."), ephemeral=True)
                e = discord.Embed(title="💰 Deposit LTC", color=discord.Color.green())
                e.description = f"> Send LTC to the address below.\n> Once confirmed, the owner will add your balance manually."
                e.add_field(name="LTC Address", value=f"```{addr}```", inline=False)
                e.set_footer(text="After sending, DM the owner with your txid and amount.")
                return await interaction.response.send_message(embed=e, ephemeral=True)
            if cid == "rsa_genkey":
                await safe_send_modal(interaction, ResellerAdvGenKeyModal(self.uid))
                return
            if cid == "rsa_prices":
                p = ADV_PRICES
                e = discord.Embed(title="💵 Adv Key Prices (Reseller)", color=discord.Color.blurple())
                e.add_field(name="1 Week",   value=f"V1: **${p['1w']['V1']}** | V2: **${p['1w']['V2']}** | V3: **${p['1w']['V3']}**",             inline=False)
                e.add_field(name="1 Month",  value=f"V1: **${p['1m']['V1']}** | V2: **${p['1m']['V2']}** | V3: **${p['1m']['V3']}**",             inline=False)
                e.add_field(name="Lifetime", value=f"V1: **${p['lifetime']['V1']}** | V2: **${p['lifetime']['V2']}** | V3: **${p['lifetime']['V3']}**", inline=False)
                e.add_field(name="Tiers",    value="V1: 1 slot, no auto-reply\nV2: 2 slots, auto-reply\nV3: 5 slots, auto-reply",                  inline=False)
                return await interaction.response.send_message(embed=e, ephemeral=True)
        return cb

def build_reseller_adv_embed(uid: str):
    u = get_adv_user(uid)
    e = discord.Embed(title="🤖 Reseller — Auto Adv Panel", color=discord.Color.blurple())
    e.add_field(name="Balance",            value=f"**{fmt_bal(u)}**",                        inline=True)
    e.add_field(name="Adv Keys Generated", value=f"`{u.get('generatedAdvKeys', 0)}`",         inline=True)
    e.set_footer(text="Use the buttons below to manage your adv keys.")
    return e

# ─── Reseller Panel (Vouch / Chat / Trade) ────────────────────────────────────

class ResellerGenKeyModal(discord.ui.Modal):
    def __init__(self, uid: str):
        super().__init__(title="Generate Key")
        self.uid = uid
        self.add_item(discord.ui.InputText(label="Type (vouch / chat / trade)", placeholder="vouch", required=True))
        self.add_item(discord.ui.InputText(label="Token Count", placeholder="e.g. 3", required=True))
        self.add_item(discord.ui.InputText(label="Amount (1–10)", placeholder="1", required=True))
    async def callback(self, interaction: discord.Interaction):
        ktype = self.children[0].value.strip().lower()
        if ktype not in ("vouch", "chat", "trade"):
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Type must be `vouch`, `chat`, or `trade`."), ephemeral=True)
        try:
            token_count = max(1, int(self.children[1].value.strip()))
            amt         = max(1, min(10, int(self.children[2].value.strip())))
        except ValueError:
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Invalid number."), ephemeral=True)
        total_cost = RESELLER_KEY_PRICE * amt
        u = get_adv_user(self.uid)
        if not u.get("infiniteBalance") and u.get("balance", 0) < total_cost:
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description=f"> ❌ Insufficient balance.\n> Need: **${total_cost:.2f}** | Have: **{fmt_bal(u)}**"), ephemeral=True)
        await interaction.response.defer(ephemeral=True)
        if not u.get("infiniteBalance"):
            update_adv_user(self.uid, balance=u["balance"] - total_cost, generatedResellerKeys=u.get("generatedResellerKeys", 0) + amt)
        else:
            update_adv_user(self.uid, generatedResellerKeys=u.get("generatedResellerKeys", 0) + amt)
        keys_data = load_keys()
        generated = []
        for _ in range(amt):
            k = str(uuid.uuid4()).upper().replace("-", "")[:16]
            keys_data[k] = {
                "keyType": ktype, "used": False, "tokenCount": token_count,
                "createdAt": datetime.now(timezone.utc).isoformat(),
                "expiresAt": None, "redeemedBy": None,
            }
            generated.append(k)
        save_keys(keys_data)
        u2 = get_adv_user(self.uid)
        try:
            dm = await interaction.user.create_dm()
            for k in generated:
                await dm.send(embed=discord.Embed(color=discord.Color.green(), title=f"🔑 {ktype.title()} Key", description=f"`{k}`\nTokens: **{token_count}**"))
            await interaction.followup.send(embed=discord.Embed(color=discord.Color.green(), description=f"> ✅ **{amt}** {ktype} key(s) sent to DMs.\n> Remaining balance: **{fmt_bal(u2)}**"), ephemeral=True)
        except discord.Forbidden:
            key_txt = "\n".join(f"`{k}`" for k in generated)
            await interaction.followup.send(embed=discord.Embed(color=discord.Color.orange(), title="🔑 Keys Generated (DMs Closed)", description=key_txt), ephemeral=True)

class ResellerExpireKeyModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Expire Key")
        self.add_item(discord.ui.InputText(label="Key Code", placeholder="Paste the key to expire", required=True))
    async def callback(self, interaction: discord.Interaction):
        code = self.children[0].value.strip().upper()
        keys_data = load_keys()
        if code not in keys_data:
            return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Key not found."), ephemeral=True)
        keys_data[code]["expiresAt"] = datetime.now(timezone.utc).isoformat()
        save_keys(keys_data)
        await interaction.response.send_message(embed=discord.Embed(color=discord.Color.green(), description=f"> ✅ Key `{code}` has been expired."), ephemeral=True)

class ResellerPanelView(discord.ui.View):
    def __init__(self, uid: str):
        super().__init__(timeout=120)
        self.uid = uid
        buttons = [
            ("👤 Profile",         "rsp_profile",  discord.ButtonStyle.blurple,   0),
            ("💰 Deposit LTC",     "rsp_deposit",  discord.ButtonStyle.success,   0),
            ("🔑 Generate Key",    "rsp_genkey",   discord.ButtonStyle.primary,   0),
            ("⏰ Expire Key",      "rsp_expire",   discord.ButtonStyle.danger,    0),
            ("💵 Prices",          "rsp_prices",   discord.ButtonStyle.secondary, 1),
        ]
        for label, cid, style, row in buttons:
            btn = discord.ui.Button(label=label, custom_id=cid, style=style, row=row)
            btn.callback = self._make_cb(cid)
            self.add_item(btn)

    def _make_cb(self, cid: str):
        async def cb(interaction: discord.Interaction):
            if str(interaction.user.id) != self.uid:
                return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Not your panel."), ephemeral=True)
            u = get_adv_user(self.uid)
            if cid == "rsp_profile":
                e = discord.Embed(title="👤 Reseller Profile", color=discord.Color.blurple())
                e.add_field(name="Balance",           value=f"**{fmt_bal(u)}**",                               inline=True)
                e.add_field(name="Keys Generated",    value=f"`{u.get('generatedResellerKeys', 0)}`",           inline=True)
                e.add_field(name="Adv Keys",          value=f"`{u.get('generatedAdvKeys', 0)}`",               inline=True)
                return await interaction.response.send_message(embed=e, ephemeral=True)
            if cid == "rsp_deposit":
                addr = get_ltc_address()
                if not addr:
                    return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ No LTC deposit address set. Contact the owner."), ephemeral=True)
                e = discord.Embed(title="💰 Deposit LTC", color=discord.Color.green())
                e.description = "> Send LTC to the address below to fund your reseller balance.\n> The owner will manually credit your account after confirmation."
                e.add_field(name="LTC Address",    value=f"```{addr}```",                      inline=False)
                e.add_field(name="Key Price",      value=f"**${RESELLER_KEY_PRICE:.2f}** per vouch/chat/trade key", inline=False)
                e.set_footer(text="DM the owner with your txid + amount after sending.")
                return await interaction.response.send_message(embed=e, ephemeral=True)
            if cid == "rsp_genkey":
                await safe_send_modal(interaction, ResellerGenKeyModal(self.uid))
                return
            if cid == "rsp_expire":
                await safe_send_modal(interaction, ResellerExpireKeyModal())
                return
            if cid == "rsp_prices":
                e = discord.Embed(title="💵 Reseller Key Prices", color=discord.Color.blurple())
                e.add_field(name="Vouch / Chat / Trade Key", value=f"**${RESELLER_KEY_PRICE:.2f}** per key",      inline=False)
                e.add_field(name="Auto Adv Keys",            value=f"V1 1w: **${ADV_PRICES['1w']['V1']}** | V2 1w: **${ADV_PRICES['1w']['V2']}** | V3 1w: **${ADV_PRICES['1w']['V3']}**\nV1 1m: **${ADV_PRICES['1m']['V1']}** | V2 1m: **${ADV_PRICES['1m']['V2']}** | V3 1m: **${ADV_PRICES['1m']['V3']}**\nLifetime: V1 **${ADV_PRICES['lifetime']['V1']}** | V2 **${ADV_PRICES['lifetime']['V2']}** | V3 **${ADV_PRICES['lifetime']['V3']}**", inline=False)
                return await interaction.response.send_message(embed=e, ephemeral=True)
        return cb

def build_reseller_panel_embed(uid: str):
    u = get_adv_user(uid)
    e = discord.Embed(title="🛒 Reseller Panel — Vouch / Chat / Trade", color=discord.Color.blurple())
    e.add_field(name="Balance",        value=f"**{fmt_bal(u)}**",                             inline=True)
    e.add_field(name="Keys Generated", value=f"`{u.get('generatedResellerKeys', 0)}`",         inline=True)
    e.add_field(name="Price per Key",  value=f"**${RESELLER_KEY_PRICE:.2f}**",                 inline=True)
    e.set_footer(text="Use the buttons below to generate or expire keys.")
    return e

# ─── New Slash Commands ────────────────────────────────────────────────────────

@bot.slash_command(name="adminadvmanage", description="Admin panel for the Auto Adv system.")
async def adminadvmanage(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    if is_restricted(uid):
        return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> 🚫 You are restricted."), ephemeral=True)
    if not can_manage_bot(uid):
        return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ Admin only."), ephemeral=True)
    e = build_adv_admin_dashboard_embed()
    view = AdminAdvManageView(uid)
    await interaction.response.send_message(embed=e, view=view, ephemeral=True)


@bot.slash_command(name="resellerautoadv", description="Reseller panel for Auto Adv key generation.")
async def resellerautoadv(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    if is_restricted(uid):
        return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> 🚫 You are restricted."), ephemeral=True)
    if not line_exists(RESELLERS_FILE, uid) and not can_manage_bot(uid):
        return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ This command is for **resellers** only."), ephemeral=True)
    e    = build_reseller_adv_embed(uid)
    view = ResellerAdvView(uid)
    await interaction.response.send_message(embed=e, view=view, ephemeral=True)


@bot.slash_command(name="resellerpanel", description="Reseller panel for Vouch, Chat and Trade key management.")
async def resellerpanel(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    if is_restricted(uid):
        return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> 🚫 You are restricted."), ephemeral=True)
    if not line_exists(RESELLERS_FILE, uid) and not can_manage_bot(uid):
        return await interaction.response.send_message(embed=discord.Embed(color=discord.Color.red(), description="> ❌ This command is for **resellers** only."), ephemeral=True)
    e    = build_reseller_panel_embed(uid)
    view = ResellerPanelView(uid)
    await interaction.response.send_message(embed=e, view=view, ephemeral=True)


# ─── Login ─────────────────────────────────────────────────────────────────────

WEBHOOK_TASK_STARTED = False

@bot.event
async def on_connect():
    global WEBHOOK_TASK_STARTED
    if not WEBHOOK_TASK_STARTED:
        WEBHOOK_TASK_STARTED = True
        asyncio.create_task(start_webhook_server())

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "generate_key":
            key_type = sys.argv[2] if len(sys.argv) > 2 else "vouch"
            if key_type == "autoadv":
                duration = sys.argv[3] if len(sys.argv) > 3 else "1w"
                slots = int(sys.argv[4]) if len(sys.argv) > 4 else 1
                variant = "V1" if slots == 1 else "V2" if slots == 2 else "V3"
                key = str(uuid.uuid4()).upper()[:16]
                keys = load_keys()
                keys[key] = {
                    "keyType": "autoadv", "used": False, "slots": slots,
                    "allowDmReply": variant != "V1", "duration": duration, "variant": variant,
                    "createdAt": datetime.now(timezone.utc).isoformat(),
                    "expiresAt": None, "redeemedBy": None, "accounts": []
                }
                save_keys(keys)
                print(key)
            else:
                status = sys.argv[2] if len(sys.argv) > 2 else "active"
                key = generate_key()
                persist_generated_key(key, status)
                print(key)
            sys.exit(0)
        elif command == "run":
            token = get_bot_token()
            if not token:
                print("Error: No bot token found. Set CLIENT_TOKEN, DISCORD_TOKEN, BOT_TOKEN, TOKEN, or DISCORD_BOT_TOKEN in the environment.")
                sys.exit(1)
            try:
                bot.run(token)
            except Exception as e:
                print(f"Error running bot: {e}")
                sys.exit(1)
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
    else:
        token = get_bot_token()
        if not token:
            print("Error: No bot token found. Set CLIENT_TOKEN, DISCORD_TOKEN, BOT_TOKEN, TOKEN, or DISCORD_BOT_TOKEN in the environment.")
            sys.exit(1)
        try:
            bot.run(token)
        except Exception as e:
            print(f"Error running bot: {e}")
            sys.exit(1)
