"""
Fotmob LİG sayfası testi.
Süper Lig'in lig sayfasından o haftanın maç linklerini bulabiliyor muyuz?
Fotmob Süper Lig ID'si = 71 (leagues/71).
Fikstür verisi __NEXT_DATA__ içinde matches/fixtures altında durur.
"""
import streamlit as st
import requests
import json
import re

st.title("Fotmob Lig Sayfası Testi")

league_url = st.text_input(
    "Süper Lig fixtures URL",
    value="https://www.fotmob.com/leagues/71/matches/super-lig",
    help="Fotmob'da Süper Lig sayfasını açıp linkini yapıştır."
)
round_no = st.text_input("Hangi hafta? (round)", value="1")

ua = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
}

if st.button("Test Et", type="primary"):
    try:
        r = requests.get(league_url, headers=ua, timeout=25)
        st.write(f"HTTP Durum: {r.status_code}")
        if r.status_code != 200:
            st.error("Sayfa açılmadı.")
            st.code(r.text[:300])
        else:
            m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', r.text, re.DOTALL)
            if not m:
                st.error("__NEXT_DATA__ yok.")
            else:
                data = json.loads(m.group(1))
                pp = data.get("props", {}).get("pageProps", {})

                # Fikstür/maç verisini bulmaya çalış
                st.subheader("pageProps üst anahtarları:")
                st.code(", ".join(pp.keys()))

                # 'matches' veya 'fixtures' altındaki round bilgisini ara
                found = []

                def walk(obj, path=""):
                    if isinstance(obj, dict):
                        # bir maç objesi: home/away + id + pageUrl benzeri
                        if ("home" in obj and "away" in obj and ("id" in obj or "pageUrl" in obj)):
                            rnd = obj.get("roundName") or obj.get("round") or obj.get("matchRound")
                            home = obj.get("home", {})
                            away = obj.get("away", {})
                            hn = home.get("name") if isinstance(home, dict) else home
                            an = away.get("name") if isinstance(away, dict) else away
                            url = obj.get("pageUrl") or obj.get("id")
                            found.append({"round": rnd, "home": hn, "away": an, "url": url, "path": path})
                        for k, v in obj.items():
                            walk(v, f"{path}.{k}")
                    elif isinstance(obj, list):
                        for i, item in enumerate(obj):
                            walk(item, f"{path}[{i}]")

                walk(pp, "pageProps")

                st.subheader(f"Bulunan toplam maç: {len(found)}")
                if found:
                    # round eşleşenleri göster
                    matching = [f for f in found if str(f.get("round")) == str(round_no)]
                    st.write(f"Round {round_no} maçları: {len(matching)}")
                    st.json(matching[:12] if matching else found[:12])
                    st.caption("Yol (path) bilgisi, otomasyonda maçları doğru yerden okumam için önemli.")
    except Exception as e:
        st.error(f"Hata: {e}")

    st.divider()
    st.info("Round'a göre maç listesi + her maçın url/id'si geldiyse: tam otomasyonu kuruyorum.")
