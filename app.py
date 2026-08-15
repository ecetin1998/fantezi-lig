import streamlit as st
import json
import os
import base64
import requests

st.set_page_config(page_title="TFF Fantezi Takip", page_icon="⚽", layout="wide")

DATA_DIR = "data"
WEEKS_FILE = os.path.join(DATA_DIR, "weeks.json")
SQUAD_FILE = os.path.join(DATA_DIR, "squad.json")

GITHUB_REPO = st.secrets.get("GITHUB_REPO", "")   # ör: "kullaniciadi/tff-fantezi-takip"
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "")
GITHUB_BRANCH = st.secrets.get("GITHUB_BRANCH", "main")

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

tab_kadro, tab_giris, tab_gecmis, tab_toplam = st.tabs(
    ["Kadro", "Hafta Girişi", "Geçmiş", "Sezon Toplamı"]
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
