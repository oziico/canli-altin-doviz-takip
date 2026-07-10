# 📈 Canlı Altın ve Döviz Takip Alarm Sistemi

Python, Streamlit ve SQLite kullanılarak geliştirilen canlı altın ve döviz takip uygulaması.

Bu proje, ücretsiz finans API'lerinden altın ve döviz verilerini belirli aralıklarla çekerek SQLite veritabanında saklar. Kullanıcı tarafından belirlenen kurallara göre alarm üretir ve tüm verileri Streamlit arayüzü üzerinden grafikler ve tablolar ile gösterir.

---

## 🚀 Özellikler

- 📊 Canlı döviz kuru takibi (USD/TRY, EUR/TRY, GBP/TRY)
- 🪙 Canlı ons ve gram altın takibi
- 💾 SQLite veritabanına fiyat geçmişi kaydı
- 🚨 Eşik ve yüzdesel değişime göre alarm sistemi
- 📈 Streamlit ile grafiksel analiz paneli
- 🕒 Otomatik veri çekme (APScheduler)

---

## 🛠️ Kullanılan Teknolojiler

- Python
- Streamlit
- SQLite
- Pandas
- Requests
- Plotly
- APScheduler
- Pytest

---

## 📂 Proje Yapısı

```
Canli-Altin-Doviz-Takip/
│
├── app.py
├── api.py
├── database.py
├── alerts.py
├── scheduler.py
├── config.py
├── models.py
├── data/
├── tests/
├── requirements.txt
└── README.md
```

---

## ⚙️ Kurulum

1. Projeyi klonlayın.

```bash
git clone https://github.com/KULLANICI_ADIN/canli-altin-doviz-takip.git
```

2. Proje klasörüne girin.

```bash
cd canli-altin-doviz-takip
```

3. Sanal ortam oluşturun ve etkinleştirin.

```bash
python3 -m venv venv
source venv/bin/activate
```

4. Gerekli paketleri yükleyin.

```bash
pip install -r requirements.txt
```

5. Uygulamayı çalıştırın.

```bash
streamlit run app.py
```

---

## 📌 Geliştirme Durumu

🚧 Proje aktif olarak geliştirilmektedir.

Planlanan modüller:

- [ ] API entegrasyonu
- [ ] SQLite veritabanı
- [ ] Alarm sistemi
- [ ] Streamlit arayüzü
- [ ] Grafikler
- [ ] Birim testleri
- [ ] Dokümantasyon

---

