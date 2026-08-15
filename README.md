# TFF Fantezi Takip

## Kurulum (senin diğer Streamlit projelerinle aynı akış)

1. GitHub'da yeni bir repo aç (ör. `tff-fantezi-takip`), bu klasördeki
   `app.py`, `requirements.txt`, `data/squad.json`, `data/weeks.json`
   dosyalarını web arayüzünden yükle.
2. https://share.streamlit.io üzerinden "New app" → repo/branch/`app.py` seçip deploy et.
3. **Kalıcı veri için (önerilir):** Streamlit Cloud → App → Settings → Secrets kısmına şunu ekle:

   ```toml
   GITHUB_REPO = "kullaniciadi/tff-fantezi-takip"
   GITHUB_TOKEN = "ghp_xxx..."   # repo yazma izinli bir GitHub Personal Access Token
   GITHUB_BRANCH = "main"
   ```

   Token oluşturmak için: GitHub → Settings → Developer settings → Personal access tokens →
   Fine-grained token, ilgili repoya **Contents: Read and write** izni ver.

   Bu ayarlanmazsa uygulama çalışır ama veriler sadece o oturumda kalır, yeniden
   başlatıldığında (Streamlit Cloud uykuya dalıp uyandığında) sıfırlanabilir.

4. Mobil tarayıcından (Safari/Chrome) Streamlit Cloud linkine girip aynı şekilde
   kullanabilirsin, giriş yaptığın veri her cihazdan GitHub'a yazılıp oradan okunur.

## Kullanım

- **Kadro**: ilk 11 + yedekler, kaptan/VC rozetli.
- **Hafta Girişi**: hafta no yaz, güç kartı seç (Tripleks / Dört Dörtlük / Tüm Takım Sahaya),
  her oyuncu için dakika/gol/asist/kart vb. gir, kaydet.
- **Geçmiş**: kaydedilen haftaların dökümü.
- **Sezon Toplamı**: oyuncu bazlı ve genel toplam puan tablosu.

Puan kuralları `app.py` içindeki `calc_points` fonksiyonunda; kaptan çarpanı ve
"tüm takım sahaya" kartı `compute_week_total` fonksiyonunda.
