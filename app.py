"""
Fotmob erişim testi.
Bunu Streamlit'e ayrı bir sayfa olarak koy (ya da geçici olarak app.py yerine çalıştır),
'Test Et' butonuna bas. Amaç: Streamlit Cloud sunucusundan Fotmob'un iç API'sine
erişilebiliyor mu görmek. Erişilirse tüm otomasyonu buna göre kurarız.
"""
import streamlit as st
import requests
import json

st.title("Fotmob Erişim Testi")
st.caption("Amaç: Streamlit Cloud'dan Fotmob verisi çekilebiliyor mu görmek.")

DATE = st.text_input("Tarih (YYYYAAGG)", value="20260815")

def try_method(name, url, headers):
    try:
        r = requests.get(url, headers=headers, timeout=20)
        status = r.status_code
        if status == 200:
            try:
                data = r.json()
                leagues = data.get("leagues", [])
                tr = [l for l in leagues if "Süper" in l.get("name","") or "Super Lig" in l.get("name","") or str(l.get("ccode",""))=="TUR"]
                info = f"OK — {len(leagues)} lig döndü."
                if tr:
                    info += f" Süper Lig bulundu, {len(tr[0].get('matches',[]))} maç."
                return True, status, info
            except Exception as e:
                return True, status, f"200 döndü ama JSON parse edilemedi: {e}"
        else:
            return False, status, r.text[:200]
    except Exception as e:
        return False, "EXC", str(e)

if st.button("Test Et", type="primary"):
    base = f"https://www.fotmob.com/api/matches?date={DATE}&timezone=Europe/Istanbul"

    st.subheader("Yöntem 1: Düz istek (header yok)")
    ok, status, info = try_method("plain", base, {})
    st.write(f"Durum: {status}")
    st.code(info)

    st.subheader("Yöntem 2: Tarayıcı taklidi (User-Agent header)")
    ua = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
        "Accept": "application/json",
    }
    ok, status, info = try_method("ua", base, ua)
    st.write(f"Durum: {status}")
    st.code(info)

    st.subheader("Yöntem 3: Alternatif domain (data.fotmob.com)")
    alt = f"https://data.fotmob.com/api/matches?date={DATE}&timezone=Europe/Istanbul"
    ok, status, info = try_method("alt", alt, ua)
    st.write(f"Durum: {status}")
    st.code(info)

    st.divider()
    st.info("Herhangi birinde 'Durum: 200' ve 'Süper Lig bulundu' görürsen, o yöntemle tam otomasyonu kurabiliriz. Hepsinde 403/hata dönerse Fotmob bu yolu kapatmış demektir.")
