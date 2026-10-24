# 🌊 SuGözü — Atatürk Barajı Erken Uyarı Sistemi

**Hidrolojik verinin yapay zekayla okunduğu, kuraklığın aylar önceden görünür kılındığı bir erken uyarı ve karar-destek sistemi.**

[🔗 Canlı Demo](https://sugozuai.streamlit.app/) · Fırat havzası, Atatürk Barajı pilot uygulaması

---

## Problem

Türkiye'de kuraklık kaynaklı hidroelektrik açığı, ancak **gerçekleştiğinde** fark ediliyor ve bu yüzden en pahalı yoldan (son dakika doğalgaz alımı) kapatılıyor — bu da yılda ortalama **1,8 milyar dolarlık** öngörülebilir ama önlenemeyen bir maliyete yol açıyor. Aynı öngörülemezlik, yenilenebilir enerji entegrasyonunu ve yeşil hidrojen gibi planlama gerektiren yatırımları da riskli kılıyor.

Kök sorun veri eksikliği değil — hidrolojik risk sinyalleri (baraj seviyesi, yağış, kar) ile enerji/yatırım kararları arasında sistematik, veriye dayalı bir bağlantının kurulmamış olması.

## Çözüm

SuGözü, baraj su seviyesini **3 ay önceden** olasılıksal olarak tahmin eden ve bu tahmini hem bir erken uyarı göstergesine hem de somut bir **yeşil hidrojen / CO2 etkisi** hesabına bağlayan, uçtan uca çalışan bir sistem.

Girdiler (DAHITI + NASA POWER)
↓
Akış tahmini (LightGBM, kuantil regresyon: q05 / q50 / q95)
↓
Risk göstergesi (tarihsel yüzdelik dilimlere dayalı eşik tablosu)
↓
Temiz enerji / yeşil hidrojen potansiyeli (fizik formülleri + sektör katsayıları)


## Nasıl Çalışıyor

1. **Tahmin:** Model, geçmiş 3 ayın su seviyesi + o ayın iklim verisinden (yağış, sıcaklık, kar, toprak nemi), önümüzdeki 3. ayın su seviyesini kötümser/en olası/iyimser senaryo olarak tahmin ediyor.
2. **Risk bandı:** Tahmin, barajın 2002-2020 arası tarihsel dağılımına göre dört banda (Normal / Erken Uyarı / Hazırlık / Kriz) yerleştiriliyor.
3. **Etki hesabı:** Seviye sapması, düşü yüksekliği üzerinden elektrik üretim sapmasına (GWh), oradan elektrolizör verimliliğiyle yeşil hidrojen potansiyeline (ton), oradan da gri hidrojene kıyasla önlenebilir CO2'ye (ton) çevriliyor.

Dashboard'daki **"Tarihe Göre İncele"** ile bu zincirin herhangi bir ay için tam çıktısı görülebilir; **"Vaka Analizi"** bölümünde ise modelin 2021 kuraklığını 9 ay önceden nasıl aşamalı olarak doğru işaret ettiği gösteriliyor.

## Veri Kaynakları

| Kaynak | Ne için | Neden seçildi |
|---|---|---|
| [DAHITI](https://dahiti.dgfi.tum.de/) (uydu altimetrisi) | Baraj su seviyesi, 2002-2026 | DSİ'nin açık verisi yıllık/havza düzeyinde kalıyordu; DAHITI aylık/baraj bazlı gerçek ölçüm sağlıyor |
| [NASA POWER](https://power.larc.nasa.gov/) | Yağış, sıcaklık, kar derinliği, toprak nemi | Kayıt/API anahtarı gerektirmiyor, bölgesel sorgu destekliyor |

## Model ve Doğrulama

- **Model:** LightGBM, kuantil regresyon (q05 / q50 / q95)
- **Doğrulama:** Walk-forward backtesting, 2020-2026 arası 7 dönem — her dönem yalnızca kendinden önceki veriyle eğitildi (veri sızıntısı önlendi)
- **Sonuç:** Model, "değişmeyecek" varsayan basit bir referans yönteme göre tahmin hatasını **%23** azalttı

## Bilinen Sınırlamalar

Dürüstlük, bu projenin bir parçası — şu anki haliyle sistemin bilinen sınırları:

- Tahmin aralığı (q05-q95), hedeflenen %90 kapsama yerine şu an ~%72-80 arası gerçekleşiyor
- Geçmişe dönük doğrulama, 2020 sonrası yalnızca 7 yıllık bir test dönemine dayanıyor
- Elektrik üretimi / hidrojen hesabı, resmi kaynaklardan alınan düşü yüksekliği (144 m) ve sektör ortalaması katsayılarla (elektrolizör verimliliği, emisyon faktörü) kurulmuş bir **gösterge niteliğinde yaklaşıklık** — kesin bir mühendislik hesabı değil
- Bu prototip yalnızca Atatürk Barajı için kuruldu; Karakaya, Keban ve çok havzalı genişletme sonraki aşama

## Teknoloji

- **Veri işleme:** Python, pandas
- **Modelleme:** LightGBM
- **Arayüz:** Streamlit
- **Görselleştirme:** Plotly / Altair
- **Geliştirme:** Claude (araştırma, metodoloji doğrulama, kod) — projenin kendi AI bileşeni değil, geliştirme sürecinde kullanılan bir araç

## Proje Yapısı

app.py # Streamlit dashboard
notebooks/ # Veri hazırlama, model eğitimi, doğrulama
data/ # İşlenmiş veri setleri (DAHITI, NASA POWER, tahmin sonuçları)
requirements.txt # Bağımlılıklar


## Kurulum

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Küresel Gündeme Bağlantı

- **COP31:** Elektrifikasyon ve yeşil hidrojen hedefleri
- **Siemens:** Karbonsuzlaştırma ve Enerji etki alanı
- **BM SDG:** Hedef 7 (Erişilebilir ve Temiz Enerji), Hedef 13 (İklim Eylemi)

---

*Climathon (Siemens / YGA / UP School) kapsamında geliştirilmiştir.*
