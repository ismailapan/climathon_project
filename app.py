import altair as alt
import pandas as pd
import pickle
import streamlit as st

# --- Veri yükleme ---
all_results = pd.read_csv('walk_forward_results.csv', parse_dates=['date'])
with open('percentiles.pkl', 'rb') as f:
    percentiles = pickle.load(f)

# --- Sayfa ayarları ---
st.set_page_config(page_title="SuGözü — Atatürk Barajı Erken Uyarı Sistemi", layout="wide")

# --- Görünüm ---
BAND_STYLES = {
    'Normal':      {'bg': '#DCFCE7', 'fg': '#166534', 'border': '#86EFAC'},
    'Erken Uyarı': {'bg': '#FEF9C3', 'fg': '#854D0E', 'border': '#FDE047'},
    'Hazırlık':    {'bg': '#FFEDD5', 'fg': '#9A3412', 'border': '#FDBA74'},
    'Kriz':        {'bg': '#FEE2E2', 'fg': '#991B1B', 'border': '#FCA5A5'},
}
NEUTRAL_STYLE = {'bg': '#E2E8F0', 'fg': '#334155', 'border': '#CBD5E1'}

COLOR_BAND = '#2563EB'
COLOR_FORECAST = '#2563EB'
COLOR_ACTUAL = '#000000'
COLOR_THRESHOLD = '#B45309'

st.markdown(
    """
    <style>
    .block-container { padding-top: 2.5rem; max-width: 1200px; }
    h2, h3 { letter-spacing: -0.01em; }
    .hero { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.25rem; }
    .hero-icon { font-size: 2.4rem; line-height: 1; }
    .hero-title { margin: 0; padding: 0; font-size: clamp(1.5rem, 3.4vw, 2.5rem); font-weight: 800;
                  letter-spacing: -0.02em; line-height: 1.15; color: #0F172A; }
    .hero-brand { background: linear-gradient(90deg, #1D4ED8, #0891B2);
                  -webkit-background-clip: text; background-clip: text;
                  -webkit-text-fill-color: transparent; color: #1D4ED8; }
    .hero-sep { color: #94A3B8; font-weight: 400; }
    .intro-card { background: #FFFFFF; border: 1px solid #E2E8F0; border-left: 4px solid #2563EB;
                  border-radius: 12px; padding: 1.25rem 1.5rem; margin: 0.75rem 0 1rem 0;
                  color: #334155; font-size: 1rem; line-height: 1.7; }
    .stat-strip { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                  gap: 1rem; margin-bottom: 0.5rem; }
    .stat-card { background: #FFFFFF; border: 1px solid #E2E8F0; border-top: 3px solid #2563EB;
                 border-radius: 12px; padding: 1rem 1.25rem; }
    .stat-title { font-size: 1.15rem; font-weight: 700; color: #0F172A; white-space: nowrap; }
    .stat-num { font-size: 2rem; font-weight: 800; color: #1D4ED8; letter-spacing: -0.02em; }
    .stat-sub { font-size: 0.9rem; color: #64748B; margin-top: 0.15rem; }
    [data-testid="stMetricValue"] { font-size: clamp(1.1rem, 1.9vw, 1.5rem); }
    [data-testid="stMetricValue"] * { overflow: visible !important; text-overflow: clip !important; }
    [data-testid="stMetricLabel"] * { overflow: visible !important; text-overflow: clip !important;
                                      white-space: normal !important; }
    .band-card { border-radius: 12px; padding: 1.25rem 1.5rem; border: 1px solid; }
    .band-card .band-label { font-size: 0.85rem; font-weight: 600; opacity: 0.8;
                             text-transform: uppercase; letter-spacing: 0.04em; }
    .band-card .band-value { font-size: 2.1rem; font-weight: 700; line-height: 1.25; }
    .band-card .band-meta { font-size: 0.95rem; opacity: 0.85; margin-top: 0.25rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


def band_card(band, meta):
    """Risk bandının rengine göre arka planı değişen kart."""
    style = next((s for name, s in BAND_STYLES.items() if name in band), NEUTRAL_STYLE)
    st.markdown(
        f"""
        <div class="band-card" style="background:{style['bg']}; color:{style['fg']};
                                      border-color:{style['border']};">
            <div class="band-label">Risk durumu</div>
            <div class="band-value">{band}</div>
            <div class="band-meta">{meta}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def forecast_chart(df, height=380, monthly_ticks=False):
    """q05-q95 bandı, q50 (kesikli) ve gerçekleşen (siyah) çizgili tahmin grafiği.

    monthly_ticks=True: x ekseninde her veri noktası (ay) için tam bir etiket gösterir.
    """
    if monthly_ticks:
        x_axis = alt.Axis(format='%Y-%m', labelColor='#475569', labelAngle=-45,
                          values=[alt.DateTime(year=d.year, month=d.month, date=d.day) for d in df['date']])
    else:
        x_axis = alt.Axis(format='%Y-%m', labelColor='#475569',
                          tickCount={'interval': 'month', 'step': 6})
    base = alt.Chart(df).encode(x=alt.X('date:T', title=None, axis=x_axis))

    band = base.mark_area(color=COLOR_BAND, opacity=0.18).encode(
        y=alt.Y('q05:Q', title='Su seviyesi (m)', scale=alt.Scale(zero=False)),
        y2='q95:Q',
    )

    lines_df = df.melt(id_vars='date', value_vars=['target', 'q50'],
                       var_name='key', value_name='value')
    lines_df['Seri'] = lines_df['key'].map({'target': 'Gerçekleşen', 'q50': 'Tahmin (q50)'})
    lines = alt.Chart(lines_df).mark_line(strokeWidth=2).encode(
        x='date:T',
        y=alt.Y('value:Q', scale=alt.Scale(zero=False)),
        color=alt.Color(
            'Seri:N', title=None,
            scale=alt.Scale(domain=['Gerçekleşen', 'Tahmin (q50)'],
                            range=[COLOR_ACTUAL, COLOR_FORECAST]),
            legend=alt.Legend(orient='top', symbolType='stroke'),
        ),
        strokeDash=alt.StrokeDash(
            'Seri:N',
            scale=alt.Scale(domain=['Gerçekleşen', 'Tahmin (q50)'], range=[[1, 0], [6, 4]]),
            legend=None,
        ),
    )

    thresholds = pd.DataFrame({
        'label': [f"{k.upper()} · {v:.2f} m" for k, v in percentiles.items()],
        'value': [float(v) for v in percentiles.values()],
    })
    rules = alt.Chart(thresholds).mark_rule(
        color=COLOR_THRESHOLD, strokeDash=[2, 3], opacity=0.7
    ).encode(y=alt.Y('value:Q', scale=alt.Scale(zero=False)))
    rule_labels = alt.Chart(thresholds).mark_text(
        align='left', baseline='bottom', dx=4, dy=-2, fontSize=11, color=COLOR_THRESHOLD
    ).encode(x=alt.value(0), y='value:Q', text='label:N')

    # Üzerine gelinen aya ait değerleri gösteren tooltip
    hover = alt.selection_point(nearest=True, on='pointerover', fields=['date'], empty=False)
    tip = alt.Chart(df).mark_rule(color='#94A3B8').encode(
        x='date:T',
        opacity=alt.condition(hover, alt.value(0.6), alt.value(0)),
        tooltip=[
            alt.Tooltip('date:T', title='Tarih', format='%Y-%m'),
            alt.Tooltip('target:Q', title='Gerçekleşen (m)', format='.2f'),
            alt.Tooltip('q50:Q', title='q50 (m)', format='.2f'),
            alt.Tooltip('q05:Q', title='q05 (m)', format='.2f'),
            alt.Tooltip('q95:Q', title='q95 (m)', format='.2f'),
            alt.Tooltip('risk_band_clean:N', title='Risk'),
        ],
    ).add_params(hover)

    return (
        alt.layer(band, rules, rule_labels, lines, tip)
        .properties(height=height)
        .configure_view(strokeWidth=0)
        .configure_axis(grid=True, gridColor='#E2E8F0', domainColor='#CBD5E1', titleColor='#475569')
        .configure_legend(labelColor='#334155')
    )


st.markdown(
    '<div class="hero"><span class="hero-icon">🌊</span>'
    '<h1 class="hero-title"><span class="hero-brand">SuGözü</span>'
    '<span class="hero-sep"> — </span>Atatürk Barajı Erken Uyarı Sistemi</h1></div>',
    unsafe_allow_html=True,
)
st.caption("Fırat havzası pilot uygulaması · Hidrolojik veri + yapay zeka ile 3 aylık su seviyesi tahmini")

st.markdown(
    '<div class="intro-card">'
    "Türkiye’de kuraklık kaynaklı hidroelektrik açığı, ancak gerçekleştiğinde fark ediliyor ve bu yüzden "
    "en pahalı yoldan (son dakika doğalgaz alımı) kapatılıyor — bu da yılda ortalama 1,8 milyar dolarlık, "
    "büyük ölçüde önlenebilir bir ek maliyete yol açıyor. Bu prototip, Fırat havzasındaki Atatürk Barajı’nı "
    "pilot alarak, uydu altimetrisi (DAHITI) ve iklim verisiyle (NASA POWER) eğitilmiş bir makine öğrenmesi "
    "modelinin, 3 ay sonraki su seviyesini olasılıksal olarak tahmin edip bunu basit bir erken uyarı "
    "göstergesine (yeşil/sarı/turuncu/kırmızı) bağladığı çalışan bir sistemi gösteriyor. 2020-2026 arası "
    "geçmişe dönük testte model, “değişmeyecek” varsayan basit bir referans yönteme göre tahmin hatasını "
    "%23 azalttı; ayrıca 2021 kuraklığını, gerçekleşmeden 9 ay önce, aşamalı ve tutarlı bir şekilde doğru "
    "yönde işaret ettiği somut bir vaka analiziyle gösterildi. Bu bir kavram kanıtıdır — tek baraj, bilinen "
    "sınırlamalarla (dar güven aralığı, sınırlı test dönemi) birlikte sunulmaktadır."
    "</div>",
    unsafe_allow_html=True,
)

STATS = [
    ("1,8", "Milyar $/yıl", "Önlenebilir maliyet potansiyeli"),
    ("%23", "Daha İsabetli", "Basit referans yönteme göre"),
    ("9", "Ay Önceden", "2021 kuraklığının erken tespiti"),
]
st.markdown(
    '<div class="stat-strip">'
    + "".join(
        f'<div class="stat-card"><div class="stat-title"><span class="stat-num">{num}</span> {unit}</div>'
        f'<div class="stat-sub">{sub}</div></div>'
        for num, unit, sub in STATS
    )
    + "</div>",
    unsafe_allow_html=True,
)

# --- Güncel durum ---
st.subheader("Güncel Durum")
latest = all_results.sort_values('date').iloc[-1]

col_card, col1, col2, col3 = st.columns([2, 1, 1.2, 1.5])
with col_card:
    band_card(latest['risk_band_clean'], f"Son tahmin tarihi: {latest['date'].strftime('%Y-%m')}")
with col1:
    with st.container(border=True):
        st.metric("Son tahmin tarihi", latest['date'].strftime('%Y-%m'))
with col2:
    with st.container(border=True):
        st.metric("En olası tahmin (q50)", f"{latest['q50']:.2f} m")
with col3:
    with st.container(border=True):
        st.metric("Tahmin aralığı (q05–q95)", f"{latest['q05']:.1f}–{latest['q95']:.1f} m")

st.divider()

# --- Tahmin grafiği ---
st.subheader("Tahmin ve Gerçekleşen Değerler (2020-2026)")
with st.container(border=True):
    st.altair_chart(forecast_chart(all_results))
    st.caption("Gölgeli alan q05–q95 tahmin aralığını gösterir. "
               "Kesikli yatay çizgiler tarihsel yüzdelik dilim eşikleridir.")

st.divider()

# --- Vaka analizi ---
st.subheader("Vaka Analizi: 2021 Kuraklığı")
case_df = all_results[(all_results['date'] >= '2021-06-01') & (all_results['date'] <= '2022-02-01')]
with st.container(border=True):
    st.altair_chart(forecast_chart(case_df, height=320, monthly_ticks=True))
    st.markdown("Model, 2021 kuraklığını 9 ay boyunca aşamalı olarak doğru şekilde takip etti.")

st.divider()

# --- Tarihe göre inceleme ---
st.subheader("Tarihe Göre İncele")
st.caption("Yalnızca veri setinde bulunan tarihler seçilebilir; değerler önceden hesaplanmış satırlardan okunur.")
available_dates = sorted(all_results['date'].unique())
selected_date = st.selectbox(
    "Tarih seçin",
    available_dates,
    index=len(available_dates) - 1,
    format_func=lambda d: pd.Timestamp(d).strftime('%Y-%m'),
)
row = all_results[all_results['date'] == selected_date].iloc[0]

sel_card, s1, s2, s3, s4 = st.columns([2, 1.5, 1.2, 1.2, 1.2])
with sel_card:
    band_card(row['risk_band_clean'], f"Tarih: {row['date'].strftime('%Y-%m')}")
for col, label, key in [(s1, "Gerçekleşen (target)", 'target'), (s2, "q05", 'q05'),
                        (s3, "q50", 'q50'), (s4, "q95", 'q95')]:
    with col:
        with st.container(border=True):
            st.metric(label, f"{row[key]:.2f} m")

st.divider()

# --- Tüm sonuçlar tablosu ---
st.subheader("Tüm Test Sonuçları")
st.dataframe(all_results[['date', 'target', 'q05', 'q50', 'q95', 'risk_band_clean']])

st.divider()

# --- Proje hakkında ---
st.subheader("Proje Hakkında")
st.markdown(
    "Pilot baraj Atatürk Barajı'dır; veriler DAHITI (uydu altimetri) ve NASA POWER kaynaklarından alınmıştır. "
)

st.markdown("**Geliştirme Altyapısı**")
st.markdown(
    "- **Veri:** DAHITI uydu altimetrisi (Atatürk Barajı su seviyesi, 2002–2026) ve NASA POWER "
    "(yağış, sıcaklık, kar derinliği, toprak nemi).\n"
    "- **İşleme:** Python / pandas; temizleme, aylık yeniden örnekleme, kısa boşluklarda doğrusal enterpolasyon.\n"
    "- **Modelleme:** LightGBM kuantil regresyon (q05/q50/q95); geçmiş 3 ayın seviyesi ve o ayın iklim "
    "verisiyle 3 ay sonrasını tahmin eder.\n"
    "- **Doğrulama:** Walk-forward backtesting, 2020–2026 arası 7 katlı geriye dönük test.\n"
    "- **Karar katmanı:** 2020 öncesi veriden hesaplanan tarihsel yüzdelik dilimlere dayalı, kural tabanlı "
    "risk bandı (veri sızıntısını önlemek için).\n"
    "- **Arayüz:** Streamlit; önceden hesaplanmış sonuçları okur, canlı yeniden eğitim yapmaz."
)

st.markdown("**Bilinen Sınırlamalar**")
st.markdown(
    "- Tahmin aralığı (q05–q95), hedeflenen %90 kapsama yerine şu an ~%72–80 arası gerçekleşiyor; "
    "model belirsizliği olması gerekenden biraz dar tahmin ediyor.\n"
    "- Geçmişe dönük doğrulama 2002–2026 arası veriyle yapıldı, ancak 2020 sonrası yalnızca 7 yıllık "
    "test dönemi var; istatistiksel güç sınırlı.\n"
    "- Bu prototip yalnızca Atatürk Barajı için kuruldu; Karakaya, Keban ve çok havzalı genişletme "
    "sonraki aşamadır."
)
