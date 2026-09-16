import pandas as pd
import streamlit as st
import yfinance as yf

st.set_page_config(
    page_title="Küresel Teknoloji & Enerji Terminali",
    page_icon="🌍",
    layout="wide",
)

st.title("🌍 Küresel Piyasalar: Teknoloji & Enerji Devleri Terminali")
st.markdown(
    "ABD teknoloji ve dünya enerji devleri için anlık fiyat taraması, RSI"
    " indikatörleri, trend analizi ve otomatik hedef fiyat matrisi."
)

# Sektörel Sembol Grupları
tech_devleri = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA"]
enerji_devleri = ["XOM", "CVX", "SHEL", "TTE", "BP"]
tum_hisseler = tech_devleri + enerji_devleri


@st.cache_data(ttl=1800)
def kuresel_piyasayi_tara():
  rapor_listesi = []
  asiri_alim_sayisi = 0
  firsat_sayisi = 0

  for hisse in tum_hisseler:
    try:
      df = yf.download(hisse, period="6mo", interval="1d", progress=False)
      if df is not None and not df.empty:
        if isinstance(df.columns, pd.MultiIndex):
          df.columns = df.columns.get_level_values(0)

        son_fiyat = float(df["Close"].iloc[-1])
        onceki_fiyat = float(df["Close"].iloc[-2])
        gunluk_degisim_yuzde = (
            (son_fiyat - onceki_fiyat) / onceki_fiyat
        ) * 100

        # RSI Hesaplama (14)
        delta = df["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        son_rsi = float(rsi.iloc[-1])

        # 50 Günlük Hareketli Ortalama (Trend)
        sma50 = float(df["Close"].rolling(window=50).mean().iloc[-1])
        trend = (
            "📈 Yükseliş (SMA50 Üstü)"
            if son_fiyat > sma50
            else "📉 Baskı (SMA50 Altı)"
        )

        # Otomatik Hedef Seviyeler
        ideal_alim = son_fiyat * 0.97
        hedef_satim = son_fiyat * 1.05

        durum = "🟡 NÖTR"
        if son_rsi < 35:
          durum = "🟢 AŞIRI SATIM (Fırsat)"
          firsat_sayisi += 1
        elif son_rsi > 65:
          durum = "🔴 AŞIRI ALIM (Dikkat)"
          asiri_alim_sayisi += 1

        rapor_listesi.append({
            "Hisse": hisse,
            "Sektör": (
                "Teknoloji" if hisse in tech_devleri else "Enerji / Emtia"
            ),
            "Fiyat ($)": round(son_fiyat, 2),
            "Günlük Değişim (%)": round(gunluk_degisim_yuzde, 2),
            "RSI (14)": round(son_rsi, 1),
            "Trend Durumu": trend,
            "Sinyal": durum,
            "İdeal Alım ($)": round(ideal_alim, 2),
            "Hedef Satış ($)": round(hedef_satim, 2),
        })
    except:
      pass

  return (
      pd.DataFrame(rapor_listesi),
      asiri_alim_sayisi,
      firsat_sayisi,
  )


# Arayüz Sekmeleri
tab_matris, tab_detay = st.tabs(
    ["🌐 Küresel Sinyal Matrisi", "📊 Tekli Hisse & Grafik İnceleme"]
)

with tab_matris:
  st.subheader("Büyük Oyuncular Fırsat ve Durum Matrisi")
  if st.button("🚀 Küresel Piyasaları Şimdi Tara"):
    with st.spinner(
        "ABD ve Avrupa enerji/teknoloji devleri analiz ediliyor..."
    ):
      df_sonuc, alim_cnt, firsat_cnt = kuresel_piyasayi_tara()
      if not df_sonuc.empty:
        st.success("Tarama başarıyla tamamlandı!")

        # 📋 Yönetici Özeti Paneli (Executive Summary)
        st.markdown("### 📊 Yönetici Özeti")
        col_o1, col_o2, col_o3 = st.columns(3)
        col_o1.metric("Taranan Toplam Varlık", len(df_sonuc))
        col_o2.metric(
            "Aşırı Alım Bölgesindeki Hisseler (Dikkat)",
            alim_cnt,
            delta_color="inverse",
        )
        col_o3.metric(
            "Aşırı Satım / Fırsat Adayları",
            firsat_cnt,
            delta_color="normal",
        )
        st.markdown("---")

        st.dataframe(df_sonuc, use_container_width=True)
      else:
        st.warning("Veriler alınamadı, lütfen tekrar deneyin.")

with tab_detay:
  secilen_kuresel = st.selectbox(
      "Detaylı İncelemek İstediğiniz Küresel Hisseyi Seçin:", tum_hisseler
  )

  if st.button("📈 Grafiği ve Verileri Getir"):
    with st.spinner(f"{secilen_kuresel} verileri yükleniyor..."):
      df_detay = yf.download(
          secilen_kuresel, period="1y", interval="1d", progress=False
      )
      if df_detay is not None and not df_detay.empty:
        if isinstance(df_detay.columns, pd.MultiIndex):
          df_detay.columns = df_detay.columns.get_level_values(0)

        df_detay["SMA50"] = df_detay["Close"].rolling(window=50).mean()
        df_detay["SMA200"] = df_detay["Close"].rolling(window=200).mean()

        son_fiyat_d = float(df_detay["Close"].iloc[-1])
        st.metric(
            label=f"{secilen_kuresel} Son Kapanış",
            value=f"{son_fiyat_d:.2f} $",
        )

        st.subheader(
            f"{secilen_kuresel} Fiyat ve Hareketli Ortalamalar (SMA50 / SMA200)"
        )
        st.line_chart(df_detay[["Close", "SMA50", "SMA200"]])
      else:
        st.warning("Hisse grafik verisi alınamadı.")
