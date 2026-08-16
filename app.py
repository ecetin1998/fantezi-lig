"""
Fotmob __NEXT_DATA__ testi (2. yöntem).
Eski /api/matches yolu öldü ama maç SAYFASININ HTML'i içinde
<script id="__NEXT_DATA__"> JSON bloğu var — tüm oyuncu statları orada.
Bu script onu Streamlit Cloud'dan çekebiliyor muyuz onu test eder.

Test için Galatasaray-Çorum FK (14.08.2026) maç sayfası kullanılıyor.
"""
import streamlit as st
import requests
import json
import re

st.title("Fotmob __NEXT_DATA__ Testi")
st.caption("Maç sayfası HTML'inden oyuncu statı çekilebiliyor mu?")

# Örnek: bir Süper Lig maç URL'si. Fotmob URL formatı: /matches/<slug>/<shortId>
# Kullanıcı isterse kendi bulduğu bir maç linkini yapıştırabilir.
default_url = st.text_input(
    "Fotmob maç URL'si",
    value="https://www.fotmob.com/matches/galatasaray-vs-corum-fk/2wj9k1",
    help="fotmob.com'da maçı aç, adres çubuğundaki linki buraya yapıştır."
)

ua = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
}

if st.button("Test Et", type="primary"):
    try:
        r = requests.get(default_url, headers=ua, timeout=25)
        st.write(f"HTTP Durum: {r.status_code}")
        if r.status_code != 200:
            st.error("Sayfa açılmadı. İçerik ilk 300 karakter:")
            st.code(r.text[:300])
        else:
            m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', r.text, re.DOTALL)
            if not m:
                st.error("__NEXT_DATA__ bloğu bulunamadı. Fotmob yapıyı değiştirmiş olabilir.")
                st.code(r.text[:300])
            else:
                data = json.loads(m.group(1))
                general = data.get("props", {}).get("pageProps", {}).get("general", {})
                content = data.get("props", {}).get("pageProps", {}).get("content", {})
                st.success("__NEXT_DATA__ bulundu ve parse edildi!")
                st.write("Maç:", general.get("matchName", "?"))
                st.write("Lig:", general.get("leagueName", "?"))

                # Oyuncu statlarını bulmaya çalış
                lineup = content.get("lineup", {}) or content.get("lineup2", {})
                if lineup:
                    st.success("Kadro/oyuncu stat verisi MEVCUT — bu yöntem çalışıyor!")
                    st.json({"lineup_anahtarlari": list(lineup.keys())})

                    # İlk bulabildiğimiz oyuncunun tam stat yapısını dök
                    def find_first_player(obj):
                        if isinstance(obj, dict):
                            # fotmob oyuncu objesi genelde 'stats' veya 'performance' içerir
                            if ("name" in obj or "id" in obj) and ("stats" in obj or "performance" in obj or "minutesPlayed" in obj):
                                return obj
                            for v in obj.values():
                                res = find_first_player(v)
                                if res:
                                    return res
                        elif isinstance(obj, list):
                            for item in obj:
                                res = find_first_player(item)
                                if res:
                                    return res
                        return None

                    sample = find_first_player(lineup)
                    if sample:
                        st.subheader("Örnek bir oyuncunun ham veri yapısı:")
                        st.json(sample)
                    else:
                        st.warning("Oyuncu objesi otomatik bulunamadı, lineup'ın tamamını döküyorum:")
                        st.json(lineup)
                else:
                    st.warning("Maç metadatası geldi ama detaylı oyuncu statı (lineup) bu maçta boş olabilir. Bitmiş bir maç linkiyle tekrar dene.")
    except Exception as e:
        st.error(f"Hata: {e}")

    st.divider()
    st.info("'__NEXT_DATA__ bulundu' + 'oyuncu stat verisi MEVCUT' görürsen: tamamen bedava otomasyonu bunun üstüne kurarım, Apify'a bile gerek kalmaz.")
