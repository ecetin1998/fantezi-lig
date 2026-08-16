import streamlit as st
import json
import os
import base64
import requests

st.set_page_config(page_title="TFF Fantezi Takip", page_icon="⚽", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');

:root {
  --bg0:#0A0A14; --bg1:#120A24; --card:#171528; --card2:#1E1B33;
  --line:rgba(255,255,255,0.08);
  --violet:#8B5CF6; --violet2:#A78BFA; --green:#34D399; --green2:#10B981;
  --text:#ECEAF6; --muted:#9B97B5; --amber:#FBBF24;
}
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
h1, h2, h3, h4 { font-family: 'Space Grotesk', sans-serif !important; letter-spacing:-0.2px; }

.stApp {
  background:
    radial-gradient(1100px 500px at 15% -10%, rgba(139,92,246,0.18), transparent 60%),
    radial-gradient(900px 500px at 100% 0%, rgba(52,211,153,0.12), transparent 55%),
    linear-gradient(180deg, #0A0A14 0%, #0D0A1A 100%);
}
[data-testid="stHeader"] { background: transparent; }

h1 {
  background: linear-gradient(90deg, var(--violet2), var(--green));
  -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
  text-transform:uppercase; font-weight:700 !important;
}
h2, h3, h4 { color: var(--text) !important; }
p, span, label, .stMarkdown, li { color: var(--text); }

[data-testid="stTabs"] { border-bottom:1px solid var(--line); }
[data-testid="stTabs"] button {
  font-family:'Space Grotesk', sans-serif; font-weight:600;
  color: var(--muted); text-transform:uppercase; letter-spacing:0.5px; font-size:13px;
}
[data-testid="stTabs"] button[aria-selected="true"] {
  color: var(--violet2) !important; border-bottom-color: var(--violet) !important;
}

[data-testid="stMetric"] {
  background: linear-gradient(135deg, rgba(139,92,246,0.12), rgba(52,211,153,0.08));
  border:1px solid var(--line); border-radius:14px; padding:14px 18px;
}
[data-testid="stMetricValue"] {
  background: linear-gradient(90deg, var(--violet2), var(--green));
  -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
  font-family:'Space Grotesk', sans-serif; font-weight:700;
}
[data-testid="stMetricLabel"] { color: var(--muted) !important; }

.stButton button {
  background: linear-gradient(90deg, var(--violet), var(--green2)) !important;
  color:#0A0A14 !important; font-weight:700 !important; border:none !important;
  border-radius:12px !important; text-transform:uppercase; letter-spacing:0.4px;
  box-shadow:0 6px 20px rgba(139,92,246,0.28);
}
.stButton button:hover { filter:brightness(1.1); }

[data-testid="stExpander"] {
  background: var(--card); border:1px solid var(--line); border-radius:14px;
}
[data-testid="stDataFrame"] { border-radius:12px; overflow:hidden; }
hr { border-color: var(--line) !important; }

/* ---- Pitch (saha) ---- */
.pitch-wrap {
  position:relative; width:100%; max-width:520px; margin:8px auto 4px;
  aspect-ratio: 68/100;
  background:
    linear-gradient(180deg, rgba(52,211,153,0.10), rgba(139,92,246,0.06)),
    repeating-linear-gradient(180deg, #0f2a1f 0px, #0f2a1f 48px, #123527 48px, #123527 96px);
  border:1px solid rgba(52,211,153,0.30); border-radius:18px; overflow:hidden;
  box-shadow: inset 0 0 60px rgba(0,0,0,0.5), 0 10px 40px rgba(0,0,0,0.4);
}
.pitch-wrap::before {
  content:""; position:absolute; left:8%; right:8%; top:6%; bottom:6%;
  border:2px solid rgba(255,255,255,0.14); border-radius:8px;
}
.pitch-wrap::after {
  content:""; position:absolute; left:34%; right:34%; top:calc(50% - 40px); height:80px;
  border:2px solid rgba(255,255,255,0.12); border-radius:50%;
}
.pitch-row {
  position:absolute; left:0; right:0; display:flex; justify-content:space-evenly;
  padding:0 6%;
}
.pp {
  display:flex; flex-direction:column; align-items:center; gap:3px; width:74px; text-align:center;
}
.pp .dot {
  width:44px; height:44px; border-radius:50%;
  background: linear-gradient(135deg, var(--violet), var(--green2));
  display:flex; align-items:center; justify-content:center;
  font-family:'Space Grotesk'; font-weight:700; font-size:13px; color:#0A0A14;
  border:2px solid rgba(255,255,255,0.35); box-shadow:0 4px 14px rgba(0,0,0,0.45);
}
.pp .dot.c { background: linear-gradient(135deg, var(--amber), #F97316); }
.pp .nm {
  font-size:11px; font-weight:600; color:#fff; line-height:1.1;
  max-width:78px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;
  text-shadow:0 1px 3px rgba(0,0,0,0.8);
}
.pp .tm { font-size:9px; color:var(--green); text-shadow:0 1px 2px rgba(0,0,0,0.8); }
.cap-badge { font-size:9px; }

/* ---- Player scoreboard cards ---- */
.pcard {
  display:flex; align-items:center; gap:12px;
  background: linear-gradient(135deg, var(--card), var(--card2));
  border:1px solid var(--line); border-radius:14px; padding:12px 14px; margin-bottom:8px;
  transition: border-color .15s;
}
.pcard:hover { border-color: rgba(139,92,246,0.5); }
.pcard.bench { opacity:0.72; }
.pc-pos {
  min-width:44px; height:44px; border-radius:11px; flex-shrink:0;
  display:flex; align-items:center; justify-content:center;
  font-family:'Space Grotesk'; font-weight:700; font-size:13px; color:#fff;
}
.pc-pos.GK { background:linear-gradient(135deg,#F59E0B,#D97706); }
.pc-pos.DEF{ background:linear-gradient(135deg,#3B82F6,#2563EB); }
.pc-pos.MID{ background:linear-gradient(135deg,#8B5CF6,#7C3AED); }
.pc-pos.FWD{ background:linear-gradient(135deg,#EF4444,#DC2626); }
.pc-body { flex:1; min-width:0; }
.pc-name { font-family:'Space Grotesk'; font-weight:600; font-size:15px; color:#fff; }
.pc-name .cbadge {
  font-size:10px; font-weight:700; padding:1px 6px; border-radius:6px; margin-left:6px;
  background:linear-gradient(135deg,var(--amber),#F97316); color:#0A0A14; vertical-align:middle;
}
.pc-name .vbadge {
  font-size:10px; font-weight:700; padding:1px 6px; border-radius:6px; margin-left:6px;
  background:rgba(255,255,255,0.15); color:#fff; vertical-align:middle;
}
.pc-team { font-size:12px; color:var(--muted); }
.pc-pts {
  font-family:'Space Grotesk'; font-weight:700; font-size:20px; flex-shrink:0;
  background:linear-gradient(90deg,var(--violet2),var(--green));
  -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
}
.pc-bar-wrap { height:5px; background:rgba(255,255,255,0.07); border-radius:3px; margin-top:6px; overflow:hidden; }
.pc-bar { height:100%; background:linear-gradient(90deg,var(--violet),var(--green)); border-radius:3px; }
.section-eyebrow {
  font-family:'Space Grotesk'; font-size:12px; font-weight:600; letter-spacing:1.5px;
  text-transform:uppercase; color:var(--violet2); margin:18px 0 8px;
}
</style>
""", unsafe_allow_html=True)

DATA_DIR = "data"
WEEKS_FILE = os.path.join(DATA_DIR, "weeks.json")
SQUAD_FILE = os.path.join(DATA_DIR, "squad.json")

GITHUB_REPO = st.secrets.get("GITHUB_REPO", "")   # ör: "kullaniciadi/tff-fantezi-takip"
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "")
GITHUB_BRANCH = st.secrets.get("GITHUB_BRANCH", "main")

FOTMOB_LEAGUE_URL = "https://www.fotmob.com/leagues/71/matches/super-lig"
FOTMOB_BASE = "https://www.fotmob.com"
FOTMOB_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
}

DEFAULT_SQUAD = [
    {"id": "sengezer", "name": "Muhammed Şengezer", "team": "Başakşehir", "pos": "GK", "role": "starter"},
    {"id": "fofana", "name": "Yahia Fofana", "team": "Çaykur Rizespor", "pos": "GK", "role": "bench"},
    {"id": "hadergjonaj", "name": "Florent Hadergjonaj", "team": "Alanyaspor", "pos": "DEF", "role": "starter"},
    {"id": "operi", "name": "Christopher Opéri", "team": "Başakşehir", "pos": "DEF", "role": "starter"},
    {"id": "eminbayram", "name": "Emin Bayram", "team": "Başakşehir", "pos": "DEF", "role": "starter"},
    {"id": "sallai", "name": "Roland Sallai", "team": "Galatasaray", "pos": "DEF", "role": "starter"},
    {"id": "andzouana", "name": "Yhoan Andzouana", "team": "Konyaspor", "pos": "DEF", "role": "bench"},
    {"id": "orkunkokcu", "name": "Orkun Kökçü", "team": "Beşiktaş", "pos": "MID", "role": "starter"},
    {"id": "sara", "name": "Gabriel Sara", "team": "Galatasaray", "pos": "MID", "role": "starter"},
    {"id": "aralsimsir", "name": "Doğuhan Aral Şimşir", "team": "Trabzonspor", "pos": "MID", "role": "starter"},
    {"id": "greenwood", "name": "Mason Greenwood", "team": "Fenerbahçe", "pos": "MID", "role": "starter"},
    {"id": "laci", "name": "Qazim Laçi", "team": "Çaykur Rizespor", "pos": "MID", "role": "bench"},
    {"id": "talisca", "name": "Anderson Talisca", "team": "Fenerbahçe", "pos": "FWD", "role": "starter", "captain": True},
    {"id": "osimhen", "name": "Victor Osimhen", "team": "Galatasaray", "pos": "FWD", "role": "starter", "vice": True},
    {"id": "oh", "name": "Oh Hyeon-gyu", "team": "Beşiktaş", "pos": "FWD", "role": "bench"},
]
FORMATION = "4-3-3"
POS_LABEL = {"GK": "Kaleci", "DEF": "Defans", "MID": "Orta Saha", "FWD": "Forvet"}

# Formasyon -> her hat için oyuncu sayısı (DEF, MID, FWD)
FORMATIONS = {
    "3-5-2": (3, 5, 2),
    "3-4-3": (3, 4, 3),
    "4-3-3": (4, 3, 3),
    "4-4-2": (4, 4, 2),
    "4-5-1": (4, 5, 1),
    "5-4-1": (5, 4, 1),
    "5-3-2": (5, 3, 2),
    "5-2-3": (5, 2, 3),
}
# Sahada dikey konum (üstten % olarak): FWD üstte, GK altta
ROW_Y = {"FWD": 14, "MID": 40, "DEF": 66, "GK": 88}
GOAL_PTS = {"GK": 10, "DEF": 6, "MID": 5, "FWD": 4}
CARD_LABELS = {
    "none": "Yok",
    "tripleks": "Tripleks Kaptan (x3)",
    "dortdortluk": "Dört Dörtlük Kaptan (x4)",
    "tumtakim": "Tüm Takım Sahaya (yedekler dahil)",
}

# ---------- GitHub persistence ----------

def github_enabled():
    return bool(GITHUB_REPO and GITHUB_TOKEN)

def _gh_headers():
    return {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github+json"}

def github_get_file(path):
    if not github_enabled():
        return None, None
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}?ref={GITHUB_BRANCH}"
    r = requests.get(url, headers=_gh_headers(), timeout=15)
    if r.status_code == 200:
        j = r.json()
        content = base64.b64decode(j["content"]).decode("utf-8")
        return content, j["sha"]
    return None, None

def github_put_file(path, content_str, message):
    if not github_enabled():
        return False
    _, sha = github_get_file(path)
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}"
    payload = {
        "message": message,
        "content": base64.b64encode(content_str.encode("utf-8")).decode("utf-8"),
        "branch": GITHUB_BRANCH,
    }
    if sha:
        payload["sha"] = sha
    r = requests.put(url, headers=_gh_headers(), json=payload, timeout=15)
    return r.status_code in (200, 201)

# ---------- Local + GitHub data load/save ----------

def ensure_local_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

def load_json_smart(local_path, github_path, default):
    ensure_local_dir()
    if os.path.exists(local_path):
        try:
            with open(local_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    content, _ = github_get_file(github_path)
    if content:
        try:
            data = json.loads(content)
            with open(local_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return data
        except Exception:
            pass
    return default

def save_json_smart(local_path, github_path, data, commit_message):
    ensure_local_dir()
    with open(local_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    ok = github_put_file(github_path, json.dumps(data, ensure_ascii=False, indent=2), commit_message)
    return ok

@st.cache_data(ttl=5)
def load_squad():
    return load_json_smart(SQUAD_FILE, "data/squad.json", DEFAULT_SQUAD)

@st.cache_data(ttl=5)
def load_weeks():
    return load_json_smart(WEEKS_FILE, "data/weeks.json", {})

def save_weeks(weeks):
    ok = save_json_smart(WEEKS_FILE, "data/weeks.json", weeks, "Hafta verisi güncellendi")
    st.cache_data.clear()
    return ok

# ---------- Fotmob (otomatik istatistik çekme, bedava) ----------

import re as _re

def apisports_enabled():
    # Fotmob key gerektirmez, otomatik çekme her zaman açık.
    return True

def _fotmob_get_html(url):
    r = requests.get(url, headers=FOTMOB_HEADERS, timeout=25)
    r.raise_for_status()
    return r.text

def _extract_next_data(html):
    m = _re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, _re.DOTALL)
    if not m:
        raise RuntimeError("Fotmob sayfa yapısı beklenenden farklı (__NEXT_DATA__ yok).")
    return json.loads(m.group(1))

def get_available_rounds():
    """Fotmob lig sayfasındaki mevcut hafta (round) numaralarını döndürür."""
    if "sl_rounds" in st.session_state:
        return st.session_state["sl_rounds"]
    html = _fotmob_get_html(FOTMOB_LEAGUE_URL)
    data = _extract_next_data(html)
    pp = data.get("props", {}).get("pageProps", {})
    all_matches = (pp.get("fixtures", {}) or {}).get("allMatches", []) or []
    rounds = sorted({m.get("round") for m in all_matches if m.get("round") is not None})
    st.session_state["sl_rounds"] = rounds
    st.session_state["sl_all_matches"] = all_matches
    return rounds

def get_round_fixtures(round_no):
    """Belirtilen haftadaki maçların (matchId, home, away) listesini döndürür."""
    cache_key = f"fixtures_round_{round_no}"
    if cache_key in st.session_state:
        return st.session_state[cache_key]
    if "sl_all_matches" not in st.session_state:
        get_available_rounds()
    all_matches = st.session_state.get("sl_all_matches", [])
    fixtures = []
    for m in all_matches:
        if str(m.get("round")) != str(round_no):
            continue
        url = m.get("pageUrl") or m.get("id") or ""
        match_id = None
        if isinstance(url, str) and "#" in url:
            match_id = url.split("#")[-1]
        elif "id" in m:
            match_id = str(m.get("id"))
        home = m.get("home", {})
        away = m.get("away", {})
        fixtures.append({
            "match_id": match_id,
            "url": url,
            "home": home.get("name") if isinstance(home, dict) else home,
            "away": away.get("name") if isinstance(away, dict) else away,
        })
    st.session_state[cache_key] = fixtures
    return fixtures

def get_fixture_players(match_id):
    """Bir maçın tüm oyuncularının ham istatistiklerini (playerStats) döndürür."""
    cache_key = f"fixture_players_{match_id}"
    if cache_key in st.session_state:
        return st.session_state[cache_key]
    url = f"{FOTMOB_BASE}/matches/x/{match_id}"
    # Fotmob # sonrası id ile doğrudan matchDetails HTML'i döndürür; ama en güvenli yol
    # lig sayfasındaki pageUrl'ü kullanmak. Burada match sayfasını çekiyoruz.
    html = _fotmob_get_html(url)
    data = _extract_next_data(html)
    content = data.get("props", {}).get("pageProps", {}).get("content", {})
    player_stats = content.get("playerStats", {}) or {}
    st.session_state[cache_key] = player_stats
    return player_stats

def get_fixture_players_by_url(page_url, match_id):
    cache_key = f"fixture_players_{match_id}"
    if cache_key in st.session_state:
        return st.session_state[cache_key]
    full = page_url
    if isinstance(page_url, str) and page_url.startswith("/"):
        full = FOTMOB_BASE + page_url
    html = _fotmob_get_html(full)
    data = _extract_next_data(html)
    content = data.get("props", {}).get("pageProps", {}).get("content", {})
    player_stats = content.get("playerStats", {}) or {}
    st.session_state[cache_key] = player_stats
    return player_stats

TR_MAP = str.maketrans({"ç": "c", "ş": "s", "ğ": "g", "ü": "u", "ö": "o", "ı": "i", "İ": "i",
                         "Ç": "c", "Ş": "s", "Ğ": "g", "Ü": "u", "Ö": "o"})

def normalize(s):
    s = (s or "").translate(TR_MAP).lower()
    return "".join(ch for ch in s if ch.isalnum())

def _player_full_name(pdata):
    name = pdata.get("name", {})
    if isinstance(name, dict):
        return name.get("fullName") or (name.get("firstName","") + " " + name.get("lastName","")).strip()
    return str(name or "")

def _stat_value(stat_groups, wanted_title):
    """playerStats[id]['stats'] listesinde başlığa göre değer bulur."""
    for group in stat_groups or []:
        stats = group.get("stats", {})
        if isinstance(stats, dict):
            for title, obj in stats.items():
                if title == wanted_title:
                    st_obj = obj.get("stat", {})
                    return st_obj.get("value")
    return None

def map_fotmob_stats(pdata, events_index=None, player_id=None):
    stat_groups = pdata.get("stats", [])
    minutes = pdata.get("minutesPlayed") or _stat_value(stat_groups, "Minutes played") or 0
    goals = _stat_value(stat_groups, "Goals") or 0
    assists = _stat_value(stat_groups, "Assists") or 0
    saves = _stat_value(stat_groups, "Saves") or _stat_value(stat_groups, "Goalkeeper saves") or 0
    conceded = _stat_value(stat_groups, "Goals conceded") or 0

    # Kartlar ve kendi kalesine gol: events index'ten (matchFacts.events) gelir
    yellow = red = own = 0
    pen_missed = pen_saved = False
    if events_index and player_id is not None:
        ev = events_index.get(str(player_id), {})
        yellow = ev.get("yellow", 0)
        red = ev.get("red", 0)
        own = ev.get("ownGoal", 0)
        pen_missed = ev.get("penMissed", False)
        pen_saved = ev.get("penSaved", False)

    return {
        "minutes": int(minutes or 0),
        "goals": int(goals or 0),
        "assists": int(assists or 0),
        "conceded": int(conceded or 0),
        "saves": int(saves or 0),
        "penSaved": bool(pen_saved),
        "penMissed": bool(pen_missed),
        "yellow": int(yellow or 0),
        "red": int(red or 0),
        "ownGoal": bool(own),
        "bonus": 0,
    }

def _build_events_index(match_id, page_url):
    """matchFacts.events'ten oyuncu bazlı kart/kk-golü/penaltı index'i kurar."""
    cache_key = f"events_{match_id}"
    if cache_key in st.session_state:
        return st.session_state[cache_key]
    full = page_url
    if isinstance(page_url, str) and page_url.startswith("/"):
        full = FOTMOB_BASE + page_url
    try:
        html = _fotmob_get_html(full)
        data = _extract_next_data(html)
        content = data.get("props", {}).get("pageProps", {}).get("content", {})
        events = (content.get("matchFacts", {}) or {}).get("events", {}) or {}
        ev_list = events.get("events", []) if isinstance(events, dict) else events
        idx = {}
        for e in ev_list or []:
            pid = e.get("player", {}).get("id") if isinstance(e.get("player"), dict) else e.get("playerId")
            if pid is None:
                continue
            pid = str(pid)
            entry = idx.setdefault(pid, {"yellow":0,"red":0,"ownGoal":0,"penMissed":False,"penSaved":False})
            etype = (e.get("type") or e.get("card") or "").lower()
            if "yellow" in etype:
                entry["yellow"] += 1
            if "red" in etype:
                entry["red"] += 1
            if e.get("isOwnGoal") or "own" in etype:
                entry["ownGoal"] += 1
            if "penalty" in etype and ("miss" in etype or e.get("isMissed")):
                entry["penMissed"] = True
        st.session_state[cache_key] = idx
        return idx
    except Exception:
        st.session_state[cache_key] = {}
        return {}

def _find_player_stats(player_stats, player_name):
    target = normalize(player_name)
    parts = player_name.split()
    target_last = normalize(parts[-1]) if parts else target
    for pid, pdata in player_stats.items():
        pname = normalize(_player_full_name(pdata))
        if not pname:
            continue
        if target == pname or target in pname or pname in target or (len(target_last) >= 4 and target_last in pname):
            return pid, pdata
    return None, None

def auto_fetch_week(round_no, squad):
    fixtures = get_round_fixtures(round_no)
    if not fixtures:
        return {}, "Bu hafta için Fotmob'da maç bulunamadı (hafta numarasını kontrol et)."
    results = {}
    misses = []
    # her maçı bir kez çek, playerStats + events index hazırla
    match_cache = {}
    for fx in fixtures:
        mid = fx["match_id"]
        if not mid:
            continue
        try:
            ps = get_fixture_players_by_url(fx["url"], mid)
            ev = _build_events_index(mid, fx["url"])
            match_cache[mid] = (ps, ev)
        except Exception:
            continue

    for p in squad:
        found = False
        for fx in fixtures:
            mid = fx["match_id"]
            if mid not in match_cache:
                continue
            ps, ev = match_cache[mid]
            pid, pdata = _find_player_stats(ps, p["name"])
            if pdata is not None:
                results[p["id"]] = map_fotmob_stats(pdata, ev, pid)
                found = True
                break
        if not found:
            misses.append(p["name"])
    msg = None
    if misses:
        msg = "Şunlar için veri bulunamadı (oynamamış olabilir): " + ", ".join(misses)
    return results, msg

def fetch_league_wide_week(round_no, squad):
    fixtures = get_round_fixtures(round_no)
    if not fixtures:
        return [], "Bu hafta için Fotmob'da maç bulunamadı."
    my_names = {normalize(p["name"]) for p in squad}
    results = []
    for fx in fixtures:
        mid = fx["match_id"]
        if not mid:
            continue
        try:
            ps = get_fixture_players_by_url(fx["url"], mid)
            ev = _build_events_index(mid, fx["url"])
        except Exception:
            continue
        for pid, pdata in ps.items():
            pname = _player_full_name(pdata)
            if normalize(pname) in my_names:
                continue
            mapped = map_fotmob_stats(pdata, ev, pid)
            if mapped["minutes"] <= 0:
                continue
            role = (pdata.get("role") or "").lower()
            pos = {"keeper":"GK","goalkeeper":"GK","defender":"DEF","midfielder":"MID","attacker":"FWD","forward":"FWD"}.get(role, "MID")
            pts = calc_points(pos, mapped)
            team_name = pdata.get("teamName", "")
            results.append({
                "Oyuncu": pname, "Takım": team_name, "Mevki": pos,
                "Dakika": mapped["minutes"], "Puan": pts,
            })
    results.sort(key=lambda r: r["Puan"], reverse=True)
    return results, None


# ---------- Scoring ----------

def calc_points(pos, s):
    pts = 0
    minutes = s.get("minutes", 0) or 0
    if minutes > 60:
        pts += 2
    elif minutes >= 60:
        pts += 1

    pts += (s.get("goals", 0) or 0) * GOAL_PTS.get(pos, 0)
    pts += (s.get("assists", 0) or 0) * 3

    conceded = s.get("conceded", 0) or 0
    if minutes >= 60:
        if pos in ("GK", "DEF") and conceded == 0:
            pts += 4
        if pos == "MID" and conceded == 0:
            pts += 1
    if pos in ("GK", "DEF"):
        pts -= conceded // 2

    if pos == "GK":
        pts += (s.get("saves", 0) or 0) // 3
        if s.get("penSaved"):
            pts += 5

    if s.get("penMissed"):
        pts -= 2
    pts -= (s.get("yellow", 0) or 0) * 1
    pts -= (s.get("red", 0) or 0) * 3
    if s.get("ownGoal"):
        pts -= 2
    pts += s.get("bonus", 0) or 0
    return pts

def compute_week_total(points, card, squad):
    multiplier = {"tripleks": 3, "dortdortluk": 4}.get(card, 2)
    total = 0
    for p in squad:
        if p["role"] == "bench" and card != "tumtakim":
            continue
        pts = points.get(p["id"], 0)
        if p.get("captain"):
            pts *= multiplier
        total += pts
    return total

def empty_stat():
    return {"minutes": 0, "goals": 0, "assists": 0, "conceded": 0, "saves": 0,
             "penSaved": False, "penMissed": False, "yellow": 0, "red": 0,
             "ownGoal": False, "bonus": 0}

# ---------- UI ----------

squad = load_squad()
weeks = load_weeks()

st.title("⚽ TFF Fantezi Takip")
st.caption(f"2026-27 Süper Lig · {len(squad)} Oyuncu Kadro · Fotmob'dan otomatik puanlama")

if not github_enabled():
    st.warning(
        "GITHUB_TOKEN / GITHUB_REPO secrets tanımlı değil — veriler sadece bu oturumda tutulur, "
        "uygulama yeniden başladığında silinebilir. Kalıcı olması için Streamlit Cloud > Settings > Secrets "
        "kısmına GITHUB_TOKEN ve GITHUB_REPO ekle.",
        icon="⚠️",
    )

tab_kadro, tab_giris, tab_gecmis, tab_toplam, tab_lig = st.tabs(
    ["Kadro", "Hafta Girişi", "Geçmiş", "Sezon Toplamı", "Öneriler"]
)

# --- Kadro ---
def render_pitch(starters, formation):
    """Seçili formasyona göre oyuncuları yeşil saha üstünde konumlandırır."""
    def_n, mid_n, fwd_n = FORMATIONS.get(formation, (4, 3, 3))
    gk = [p for p in starters if p["pos"] == "GK"]
    de = [p for p in starters if p["pos"] == "DEF"]
    mi = [p for p in starters if p["pos"] == "MID"]
    fw = [p for p in starters if p["pos"] == "FWD"]

    rows_html = ""
    for pos, players in [("FWD", fw), ("MID", mi), ("DEF", de), ("GK", gk)]:
        if not players:
            continue
        y = ROW_Y[pos]
        cells = ""
        for p in players:
            initials = "".join([w[0] for w in p["name"].split()[:2]]).upper()
            dot_cls = "dot c" if p.get("captain") else "dot"
            cap = "<span class='cap-badge'>©</span>" if p.get("captain") else ("<span class='cap-badge'>Ⓥ</span>" if p.get("vice") else "")
            cells += (
                f"<div class='pp'>"
                f"<div class='{dot_cls}'>{initials}</div>"
                f"<div class='nm'>{p['name'].split()[-1]} {cap}</div>"
                f"<div class='tm'>{p.get('team','')}</div>"
                f"</div>"
            )
        rows_html += f"<div class='pitch-row' style='top:{y}%'>{cells}</div>"
    return f"<div class='pitch-wrap'>{rows_html}</div>"


def pcard_html(p, pts=None, maxpts=1, bench=False):
    cbadge = "<span class='cbadge'>C</span>" if p.get("captain") else ("<span class='vbadge'>VC</span>" if p.get("vice") else "")
    pts_html = ""
    if pts is not None:
        width = int((pts / maxpts) * 100) if maxpts > 0 else 0
        width = max(0, min(100, width))
        pts_html = (
            f"<div class='pc-pts'>{pts}</div>"
        )
        bar = f"<div class='pc-bar-wrap'><div class='pc-bar' style='width:{width}%'></div></div>"
    else:
        bar = ""
    return (
        f"<div class='pcard {'bench' if bench else ''}'>"
        f"<div class='pc-pos {p['pos']}'>{p['pos']}</div>"
        f"<div class='pc-body'>"
        f"<div class='pc-name'>{p['name']}{cbadge}</div>"
        f"<div class='pc-team'>{p.get('team','')}</div>"
        f"{bar}"
        f"</div>"
        f"{pts_html}"
        f"</div>"
    )


with tab_kadro:
    starters = [p for p in squad if p["role"] == "starter"]
    bench = [p for p in squad if p["role"] == "bench"]

    # Formasyon seçimi (her hafta değişebilir)
    saved_formation = st.session_state.get("formation", FORMATION)
    formation = st.selectbox(
        "Diziliş",
        options=list(FORMATIONS.keys()),
        index=list(FORMATIONS.keys()).index(saved_formation) if saved_formation in FORMATIONS else 2,
    )
    st.session_state["formation"] = formation

    # Uyarı: seçilen formasyon kadrodaki oyuncu dağılımına uyuyor mu?
    def_n, mid_n, fwd_n = FORMATIONS[formation]
    have = {
        "DEF": len([p for p in starters if p["pos"] == "DEF"]),
        "MID": len([p for p in starters if p["pos"] == "MID"]),
        "FWD": len([p for p in starters if p["pos"] == "FWD"]),
    }
    if (have["DEF"], have["MID"], have["FWD"]) != (def_n, mid_n, fwd_n):
        st.caption(
            f"ℹ️ Seçtiğin diziliş {def_n}-{mid_n}-{fwd_n} ama ilk 11'inde "
            f"{have['DEF']} def / {have['MID']} orta / {have['FWD']} forvet var. "
            "Saha yine de mevcut oyuncularla çiziliyor."
        )

    st.markdown(render_pitch(starters, formation), unsafe_allow_html=True)

    # Sezon toplam puanlarını çek (bar için)
    season_totals = {p["id"]: 0 for p in squad}
    for wk, wdata in weeks.items():
        for pid, pts in wdata.get("points", {}).items():
            season_totals[pid] = season_totals.get(pid, 0) + pts
    max_total = max(season_totals.values()) if season_totals and max(season_totals.values()) > 0 else 1

    st.markdown("<div class='section-eyebrow'>İlk 11</div>", unsafe_allow_html=True)
    order = {"GK": 0, "DEF": 1, "MID": 2, "FWD": 3}
    for p in sorted(starters, key=lambda x: order.get(x["pos"], 9)):
        st.markdown(pcard_html(p, season_totals.get(p["id"], 0), max_total), unsafe_allow_html=True)

    st.markdown("<div class='section-eyebrow'>Yedekler</div>", unsafe_allow_html=True)
    for p in sorted(bench, key=lambda x: order.get(x["pos"], 9)):
        st.markdown(pcard_html(p, season_totals.get(p["id"], 0), max_total, bench=True), unsafe_allow_html=True)

    st.caption("Puan çubukları sezon toplamına göredir. Kaptan x2 sayılır; Hafta Girişi'nde güç kartıyla x3/x4 yapabilirsin.")

# --- Hafta Girişi ---
with tab_giris:
    week_no = st.text_input("Hafta No", value="1", key="week_no_input")
    existing = weeks.get(week_no, {})
    existing_stats = existing.get("stats", {})
    card = st.selectbox(
        "Güç Kartı",
        options=list(CARD_LABELS.keys()),
        format_func=lambda k: CARD_LABELS[k],
        index=list(CARD_LABELS.keys()).index(existing.get("card", "none")),
    )

    st.caption("Veriler Fotmob'dan otomatik çekilir — ücretsiz, ekstra kurulum gerekmez.")
    if st.button("🔄 Bu Haftayı Fotmob'dan Otomatik Çek", type="secondary"):
        with st.spinner("Fotmob'dan maçlar ve oyuncu istatistikleri çekiliyor..."):
            try:
                fetched, msg = auto_fetch_week(week_no, squad)
            except (requests.exceptions.RequestException, RuntimeError) as e:
                fetched, msg = {}, f"Fotmob'a erişilemedi: {e}"
            for pid, s in fetched.items():
                st.session_state[f"min_{week_no}_{pid}"] = s["minutes"]
                st.session_state[f"g_{week_no}_{pid}"] = s["goals"]
                st.session_state[f"a_{week_no}_{pid}"] = s["assists"]
                st.session_state[f"c_{week_no}_{pid}"] = s["conceded"]
                st.session_state[f"s_{week_no}_{pid}"] = s["saves"]
                st.session_state[f"ps_{week_no}_{pid}"] = s["penSaved"]
                st.session_state[f"pm_{week_no}_{pid}"] = s["penMissed"]
                st.session_state[f"y_{week_no}_{pid}"] = s["yellow"]
                st.session_state[f"r_{week_no}_{pid}"] = s["red"]
                st.session_state[f"og_{week_no}_{pid}"] = s["ownGoal"]
            if fetched:
                st.success(f"{len(fetched)} oyuncu için veri çekildi. Aşağıdan kontrol edip kaydet.")
            if msg:
                st.warning(msg)

    st.divider()
    stats_input = {}
    for pos in ["GK", "DEF", "MID", "FWD"]:
        st.markdown(f"### {POS_LABEL[pos]}")
        for p in [x for x in squad if x["pos"] == pos]:
            prev = existing_stats.get(p["id"], empty_stat())
            with st.expander(f"{p['name']} — {p.get('team','')} ({'İlk 11' if p['role']=='starter' else 'Yedek'})", expanded=False):
                c1, c2, c3, c4 = st.columns(4)
                minutes = c1.number_input("Dakika", 0, 120, prev.get("minutes", 0), key=f"min_{week_no}_{p['id']}")
                goals = c2.number_input("Gol", 0, 10, prev.get("goals", 0), key=f"g_{week_no}_{p['id']}")
                assists = c3.number_input("Asist", 0, 10, prev.get("assists", 0), key=f"a_{week_no}_{p['id']}")
                conceded = c4.number_input("Yenilen Gol", 0, 10, prev.get("conceded", 0), key=f"c_{week_no}_{p['id']}")

                c5, c6, c7, c8 = st.columns(4)
                saves = c5.number_input("Kurtarış", 0, 20, prev.get("saves", 0), key=f"s_{week_no}_{p['id']}", disabled=(pos != "GK"))
                yellow = c6.number_input("Sarı Kart", 0, 2, prev.get("yellow", 0), key=f"y_{week_no}_{p['id']}")
                red = c7.number_input("Kırmızı Kart", 0, 1, prev.get("red", 0), key=f"r_{week_no}_{p['id']}")
                bonus = c8.number_input("Bonus (maç en iyisi)", 0, 3, prev.get("bonus", 0), key=f"b_{week_no}_{p['id']}")

                c9, c10, c11 = st.columns(3)
                pen_saved = c9.checkbox("Penaltı Kurtardı", prev.get("penSaved", False), key=f"ps_{week_no}_{p['id']}", disabled=(pos != "GK"))
                pen_missed = c10.checkbox("Penaltı Kaçırdı", prev.get("penMissed", False), key=f"pm_{week_no}_{p['id']}")
                own_goal = c11.checkbox("Kendi Kalesine Gol", prev.get("ownGoal", False), key=f"og_{week_no}_{p['id']}")

                s = {"minutes": minutes, "goals": goals, "assists": assists, "conceded": conceded,
                     "saves": saves, "penSaved": pen_saved, "penMissed": pen_missed,
                     "yellow": yellow, "red": red, "ownGoal": own_goal, "bonus": bonus}
                stats_input[p["id"]] = s
                st.caption(f"Bu haftaki ham puan: **{calc_points(pos, s)}**")

    points_preview = {pid: calc_points(next(p["pos"] for p in squad if p["id"] == pid), s) for pid, s in stats_input.items()}
    total_preview = compute_week_total(points_preview, card, squad)

    st.divider()
    st.metric(f"Hafta {week_no} Toplam Puan (kart: {CARD_LABELS[card]})", total_preview)

    if st.button("💾 Haftayı Kaydet", type="primary"):
        weeks[week_no] = {"stats": stats_input, "points": points_preview, "total": total_preview, "card": card}
        ok = save_weeks(weeks)
        if ok or not github_enabled():
            st.success(f"Hafta {week_no} kaydedildi. Toplam: {total_preview} puan.")
        else:
            st.error("GitHub'a yazılamadı, sadece bu oturumda kaydedildi. Token/repo bilgilerini kontrol et.")

# --- Geçmiş ---
with tab_gecmis:
    if not weeks:
        st.info("Henüz kayıtlı hafta yok.")
    else:
        for wk in sorted(weeks.keys(), key=lambda x: int(x) if x.isdigit() else 0):
            data = weeks[wk]
            with st.expander(f"Hafta {wk} — {data.get('total', 0)} puan (kart: {CARD_LABELS.get(data.get('card','none'))})"):
                rows = []
                for p in squad:
                    raw = data.get("points", {}).get(p["id"], 0)
                    rows.append({"Oyuncu": p["name"], "Takım": p.get("team",""), "Mevki": p["pos"], "Ham Puan": raw})
                st.dataframe(rows, use_container_width=True, hide_index=True)

# --- Sezon Toplamı ---
with tab_toplam:
    totals = {p["id"]: 0 for p in squad}
    season_total = 0
    for wk, data in weeks.items():
        for pid, pts in data.get("points", {}).items():
            totals[pid] = totals.get(pid, 0) + pts
        season_total += data.get("total", 0)

    c1, c2, c3 = st.columns(3)
    c1.metric("Hafta Sayısı", len(weeks))
    c2.metric("Sezon Toplamı", season_total)
    c3.metric("Haftalık Ortalama", round(season_total / len(weeks), 1) if weeks else 0)

    sorted_squad = sorted(squad, key=lambda p: totals.get(p["id"], 0), reverse=True)
    max_total = max([totals.get(p["id"], 0) for p in sorted_squad], default=1) or 1

    st.markdown("<div class='section-eyebrow'>Oyuncu Sıralaması</div>", unsafe_allow_html=True)
    medals = {0: "🥇", 1: "🥈", 2: "🥉"}
    for i, p in enumerate(sorted_squad):
        pts = totals.get(p["id"], 0)
        rank = medals.get(i, f"{i+1}.")
        cbadge = "<span class='cbadge'>C</span>" if p.get("captain") else ("<span class='vbadge'>VC</span>" if p.get("vice") else "")
        width = max(0, min(100, int((pts / max_total) * 100)))
        st.markdown(
            f"<div class='pcard'>"
            f"<div class='pc-pos {p['pos']}' style='font-size:16px;'>{rank}</div>"
            f"<div class='pc-body'>"
            f"<div class='pc-name'>{p['name']}{cbadge}"
            f"<span style='color:var(--muted);font-weight:400;font-size:12px;'> · {p['pos']}</span></div>"
            f"<div class='pc-team'>{p.get('team','')}</div>"
            f"<div class='pc-bar-wrap'><div class='pc-bar' style='width:{width}%'></div></div>"
            f"</div>"
            f"<div class='pc-pts'>{pts}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

# --- Öneriler (Lig Geneli) ---
with tab_lig:
    st.subheader("Bu Hafta Lig Genelinde En Çok Puan Alanlar")
    st.caption("Kendi kadrondaki oyuncular bu listeye dahil edilmez — transfer fikri için bakabilirsin.")

    colA, colB = st.columns([2, 1])
    lig_hafta = colA.text_input("Hafta No", value=week_no, key="lig_hafta_input")
    pos_filter = colB.selectbox("Mevki Filtresi", ["Tümü", "GK", "DEF", "MID", "FWD"], key="lig_pos_filter")

    if st.button("🔍 Bu Haftayı Tara", type="primary", key="lig_scan_btn"):
        with st.spinner("Lig genelindeki tüm maçlar Fotmob'dan taranıyor, bu biraz sürebilir..."):
            try:
                league_results, err = fetch_league_wide_week(lig_hafta, squad)
            except (requests.exceptions.RequestException, RuntimeError) as e:
                league_results, err = [], f"Fotmob'a erişilemedi: {e}"
            st.session_state["lig_results"] = league_results
            st.session_state["lig_err"] = err

    league_results = st.session_state.get("lig_results", [])
    err = st.session_state.get("lig_err")
    if err:
        st.warning(err)
    if league_results:
        filtered = league_results if pos_filter == "Tümü" else [r for r in league_results if r["Mevki"] == pos_filter]
        st.dataframe(filtered[:30], use_container_width=True, hide_index=True)
        st.caption(f"Toplam {len(filtered)} oyuncu listelendi, en iyi 30 tanesi gösteriliyor.")
