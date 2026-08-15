import streamlit as st
import json
import os
import base64
import requests

st.set_page_config(page_title="TFF Fantezi Takip", page_icon="⚽", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@500;700&family=Inter:wght@400;600&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
h1, h2, h3 { font-family: 'Oswald', sans-serif !important; letter-spacing: 0.3px; }

.stApp {
  background: linear-gradient(180deg, #0B1F3A 0%, #0E2A4A 100%);
}
[data-testid="stHeader"] { background: transparent; }

h1 { color: #F5B841 !important; text-transform: uppercase; }
h2, h3 { color: #EAF1FB !important; }
p, span, label, .stMarkdown { color: #D7E2F0; }

[data-testid="stTabs"] button {
  font-family: 'Oswald', sans-serif;
  font-weight: 600;
  color: #B9C7DC;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
[data-testid="stTabs"] button[aria-selected="true"] {
  color: #F5B841 !important;
  border-bottom-color: #F5B841 !important;
}

[data-testid="stMetric"] {
  background: rgba(245, 184, 65, 0.08);
  border: 1px solid rgba(245, 184, 65, 0.35);
  border-radius: 10px;
  padding: 12px 16px;
}
[data-testid="stMetricValue"] { color: #F5B841 !important; font-family: 'Oswald', sans-serif; }
[data-testid="stMetricLabel"] { color: #B9C7DC !important; }

.stButton button {
  background: #F5B841 !important;
  color: #0B1F3A !important;
  font-weight: 700 !important;
  border-radius: 8px !important;
  border: none !important;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.stButton button:hover { background: #ffcb63 !important; }

[data-testid="stExpander"] {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 8px;
}

[data-testid="stDataFrame"] { border-radius: 8px; overflow: hidden; }

hr { border-color: rgba(255,255,255,0.1) !important; }
</style>
""", unsafe_allow_html=True)

DATA_DIR = "data"
WEEKS_FILE = os.path.join(DATA_DIR, "weeks.json")
SQUAD_FILE = os.path.join(DATA_DIR, "squad.json")

GITHUB_REPO = st.secrets.get("GITHUB_REPO", "")   # ör: "kullaniciadi/tff-fantezi-takip"
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "")
GITHUB_BRANCH = st.secrets.get("GITHUB_BRANCH", "main")

APISPORTS_KEY = st.secrets.get("APISPORTS_KEY", "")
APISPORTS_SEASON = int(st.secrets.get("APISPORTS_SEASON", 2026))
APISPORTS_BASE = "https://v3.football.api-sports.io"

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

# ---------- API-Football (otomatik istatistik çekme) ----------

def apisports_enabled():
    return bool(APISPORTS_KEY)

def _api_headers():
    return {"x-apisports-key": APISPORTS_KEY}

def _api_get(path, params):
    r = requests.get(f"{APISPORTS_BASE}{path}", headers=_api_headers(), params=params, timeout=20)
    r.raise_for_status()
    return r.json()

def get_league_id():
    if "sl_league_id" in st.session_state:
        return st.session_state["sl_league_id"]
    data = _api_get("/leagues", {"name": "Super Lig", "country": "Turkey"})
    league_id = None
    for item in data.get("response", []):
        if item.get("league", {}).get("type") == "League":
            league_id = item["league"]["id"]
            break
    if league_id is None:
        league_id = 203  # bilinen Süper Lig id'si, arama başarısız olursa yedek
    st.session_state["sl_league_id"] = league_id
    return league_id

def get_round_fixtures(round_no):
    cache_key = f"fixtures_round_{round_no}"
    if cache_key in st.session_state:
        return st.session_state[cache_key]
    league_id = get_league_id()
    data = _api_get("/fixtures", {
        "league": league_id,
        "season": APISPORTS_SEASON,
        "round": f"Regular Season - {round_no}",
    })
    fixtures = data.get("response", [])
    st.session_state[cache_key] = fixtures
    return fixtures

def get_fixture_players(fixture_id):
    cache_key = f"fixture_players_{fixture_id}"
    if cache_key in st.session_state:
        return st.session_state[cache_key]
    data = _api_get("/fixtures/players", {"fixture": fixture_id})
    result = data.get("response", [])
    st.session_state[cache_key] = result
    return result

TR_MAP = str.maketrans({"ç": "c", "ş": "s", "ğ": "g", "ü": "u", "ö": "o", "ı": "i", "İ": "i",
                         "Ç": "c", "Ş": "s", "Ğ": "g", "Ü": "u", "Ö": "o"})

def normalize(s):
    s = (s or "").translate(TR_MAP).lower()
    return "".join(ch for ch in s if ch.isalnum())

def find_team_fixture(team_name, fixtures):
    target = normalize(team_name)
    for fx in fixtures:
        home = normalize(fx["teams"]["home"]["name"])
        away = normalize(fx["teams"]["away"]["name"])
        if target in home or home in target or target in away or away in target:
            return fx["fixture"]["id"]
    return None

def find_player_in_fixture(fixture_players, player_name):
    target = normalize(player_name)
    target_last = normalize(player_name.split()[-1])
    for team_block in fixture_players:
        for entry in team_block.get("players", []):
            pname = normalize(entry.get("player", {}).get("name", ""))
            if target == pname or target in pname or pname in target or target_last in pname:
                stats = entry.get("statistics", [{}])[0]
                return stats
    return None

def map_api_stats(stats):
    games = stats.get("games") or {}
    goals = stats.get("goals") or {}
    cards = stats.get("cards") or {}
    penalty = stats.get("penalty") or {}
    return {
        "minutes": games.get("minutes") or 0,
        "goals": goals.get("total") or 0,
        "assists": goals.get("assists") or 0,
        "conceded": goals.get("conceded") or 0,
        "saves": goals.get("saves") or 0,
        "penSaved": (penalty.get("saved") or 0) > 0,
        "penMissed": (penalty.get("missed") or 0) > 0,
        "yellow": cards.get("yellow") or 0,
        "red": (cards.get("red") or 0) + (cards.get("yellowred") or 0),
        "ownGoal": False,  # API bu alanı doğrudan vermiyor, gerekirse elle işaretle
        "bonus": 0,
    }

def auto_fetch_week(round_no, squad):
    fixtures = get_round_fixtures(round_no)
    if not fixtures:
        return {}, "Bu hafta için fikstür bulunamadı (round numarasını veya sezonu kontrol et)."
    results = {}
    misses = []
    for p in squad:
        team = p.get("team", "")
        fid = find_team_fixture(team, fixtures)
        if fid is None:
            misses.append(p["name"])
            continue
        fixture_players = get_fixture_players(fid)
        stat = find_player_in_fixture(fixture_players, p["name"])
        if stat is None:
            misses.append(p["name"])
            continue
        results[p["id"]] = map_api_stats(stat)
    msg = None
    if misses:
        msg = "Şunlar için veri bulunamadı, elle kontrol et: " + ", ".join(misses)
    return results, msg

API_POS_MAP = {"G": "GK", "D": "DEF", "M": "MID", "F": "FWD"}

def squad_name_set(squad):
    return {normalize(p["name"]) for p in squad}

def fetch_league_wide_week(round_no, squad):
    fixtures = get_round_fixtures(round_no)
    if not fixtures:
        return [], "Bu hafta için fikstür bulunamadı."
    my_names = squad_name_set(squad)
    results = []
    for fx in fixtures:
        fid = fx["fixture"]["id"]
        try:
            fixture_players = get_fixture_players(fid)
        except requests.exceptions.RequestException:
            continue
        for team_block in fixture_players:
            team_name = team_block.get("team", {}).get("name", "")
            for entry in team_block.get("players", []):
                pname = entry.get("player", {}).get("name", "")
                if normalize(pname) in my_names:
                    continue  # kendi kadronda olan oyuncuyu önerme
                stats_list = entry.get("statistics", [{}])
                if not stats_list:
                    continue
                stats = stats_list[0]
                games = stats.get("games") or {}
                minutes = games.get("minutes") or 0
                if minutes <= 0:
                    continue  # oynamayanları listeleme
                api_pos = (games.get("position") or "")[:1].upper()
                pos = API_POS_MAP.get(api_pos, "MID")
                mapped = map_api_stats(stats)
                pts = calc_points(pos, mapped)
                results.append({
                    "Oyuncu": pname, "Takım": team_name, "Mevki": pos,
                    "Dakika": minutes, "Puan": pts,
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
st.caption(f"2026-27 Süper Lig · {len(squad)} Oyuncu · {FORMATION}")

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
with tab_kadro:
    starters = [p for p in squad if p["role"] == "starter"]
    bench = [p for p in squad if p["role"] == "bench"]

    st.subheader(f"İlk 11 · {FORMATION}")
    cols = st.columns(4)
    for i, pos in enumerate(["GK", "DEF", "MID", "FWD"]):
        with cols[i]:
            st.markdown(f"**{POS_LABEL[pos]}**")
            for p in [x for x in starters if x["pos"] == pos]:
                tag = " 🅲" if p.get("captain") else (" 🆅" if p.get("vice") else "")
                st.write(f"- **{p['name']}**{tag}  \n  <span style='color:gray;font-size:0.85em;'>{p.get('team','')}</span>", unsafe_allow_html=True)

    st.subheader("Yedekler")
    st.write(", ".join(f"{p['name']} ({p.get('team','')})" for p in bench))
    st.caption("Kaptan puanı varsayılan x2 sayılır; Hafta Girişi'nde güç kartıyla x3/x4'e çıkarabilirsin.")

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

    if apisports_enabled():
        if st.button("🔄 Bu Haftayı API'den Otomatik Çek", type="secondary"):
            with st.spinner("İstatistikler çekiliyor..."):
                try:
                    fetched, msg = auto_fetch_week(week_no, squad)
                except requests.exceptions.RequestException as e:
                    fetched, msg = {}, f"API isteği başarısız: {e}"
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
    else:
        st.caption(
            "Otomatik çekme kapalı — Streamlit Cloud Secrets'a `APISPORTS_KEY` eklersen "
            "(api-football.com'dan ücretsiz alınabilir, günde 100 istek) bu haftayı tek tuşla çekebilirsin."
        )

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
    rows = [{"Oyuncu": p["name"], "Takım": p.get("team",""), "Mevki": p["pos"], "Toplam Puan": totals.get(p["id"], 0)} for p in sorted_squad]
    st.dataframe(rows, use_container_width=True, hide_index=True)

# --- Öneriler (Lig Geneli) ---
with tab_lig:
    st.subheader("Bu Hafta Lig Genelinde En Çok Puan Alanlar")
    st.caption("Kendi kadrondaki oyuncular bu listeye dahil edilmez — transfer fikri için bakabilirsin.")

    if not apisports_enabled():
        st.info(
            "Bu özellik API-Football'a bağlı. Streamlit Cloud Secrets'a `APISPORTS_KEY` "
            "ekledikten sonra burada aktif olur."
        )
    else:
        colA, colB = st.columns([2, 1])
        lig_hafta = colA.text_input("Hafta No", value=week_no, key="lig_hafta_input")
        pos_filter = colB.selectbox("Mevki Filtresi", ["Tümü", "GK", "DEF", "MID", "FWD"], key="lig_pos_filter")

        if st.button("🔍 Bu Haftayı Tara", type="primary", key="lig_scan_btn"):
            with st.spinner("Lig genelindeki tüm maçlar taranıyor, bu biraz sürebilir..."):
                try:
                    league_results, err = fetch_league_wide_week(lig_hafta, squad)
                except requests.exceptions.RequestException as e:
                    league_results, err = [], f"API isteği başarısız: {e}"
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
