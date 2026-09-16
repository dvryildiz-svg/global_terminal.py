from feedparser import parse
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
    " indikatörleri, trend analizi, hisse bazlı yönetici özetleri ve haber"
    " akışı."
)

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

        delta = df["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        son_rsi = float(rsi.iloc[-1])

        sma50 = float(df["Close"].rolling(window=50).mean().iloc[-1])
        trend = (
            "📈 Yükseliş (SMA50 Üstü)"
            if son_fiyat > sma50
            else "📉 Baskı (SMA50 Altı)"
        )

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


@st.cache_data(ttl=1800)
def kuresel_haberleri_getir(hisse_kodu):
  try:
    url = f"https://news.google.com/rss/search?q={hisse_kodu}+stock+news&hl=EN&gl=US&ceid=US:en"
    feed = parse(url)
    haberler = [
        {
            "baslik": entry.title,
            "link": entry.link,
            "zaman": getattr(entry, "published", "Güncel"),
        }
        for entry in feed.entries[:5]
    ]
    return haberler
  except:
    return []


tab_matris, tab_detay = st.tabs(
    ["🌐 Küresel Sinyal Matrisi", "📊 Hisse Bazlı Yönetici Özeti ve Haberler"]
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

        st.markdown("### 📊 Genel Yönetici Özeti")
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
      "Detaylı İncelemek İstediğiniz Küresel Hisseyi Seçin:",
      tum_hisseler,
      key="detay_secim",
  )

  if st.button("🔍 Hisse Raporunu ve Haberleri Getir", key="btn_detay"):
    with st.spinner(f"{secilen_kuresel} detayları ve haberleri yükleniyor..."):
      df_detay = yf.download(
          secilen_kuresel, period="1y", interval="1d", progress=False
      )
      haberler = kuresel_haberleri_getir(secilen_kuresel)

      if df_detay is not None and not df_detay.empty:
        if isinstance(df_detay.columns, pd.MultiIndex):
          df_detay.columns = df_detay.columns.get_level_values(0)

        son_fiyat = float(df_detay["Close"].iloc[-1])
        onceki_fiyat = float(df_detay["Close"].iloc[-2])
        degisim = ((son_fiyat - onceki_fiyat) / onceki_fiyat) * 100

        delta = df_detay["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        son_rsi = float(rsi.iloc[-1])

        sma50 = float(df_detay["Close"].rolling(window=50).mean().iloc[-1])
        sma200 = float(df_detay["Close"].rolling(window=200).mean().iloc[-1])

        # 📋 Hisse Bazlı Yönetici Özeti Kutuları
        st.markdown(f"### 🎯 {secilen_kuresel} - Hisse Bazlı Yönetici Özeti")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Son Kapanış", f"{son_fiyat:.2f} $", f"{degisim:.2f}%")
        c2.metric("RSI (14)", f"{son_rsi:.1f}")
        c3.metric("İdeal Alım (Destek)", f"{son_fiyat * 0.97:.2f} $")
        c4.metric("Hedef Satış (Direnç)", f"{son_fiyat * 1.05:.2f} $")

        # Kısa Karar Yorumu
        if son_rsi < 35:
          st.success(
              f"**Akıllı Sinyal:** 🟢 **AL / FIRSAT** — {secilen_kuresel} aşırı"
              " satım bölgesinde. Kademeli alım fırsatları değerlendirilebilir."
          )
        elif son_rsi > 65:
          st.warning(
              f"**Akıllı Sinyal:** 🔴 **DİKKAT / SAT** — {secilen_kuresel} aşırı"
              " alım bölgesinde, kısa vadeli kar satışlarına karşı temkinli"
              " olunmalı."
          )
        else:
          st.info(
              f"**Akıllı Sinyal:** 🟡 **TUT / NÖTR** — Fiyat hareketleri dengeli"
              " seyrediyor."
          )

        st.markdown("---")

        # Fiyat Grafiği
        st.subheader(
            f"{secilen_kuresel} Fiyat ve Hareketli Ortalamalar (SMA50 / SMA200)"
        )
        df_detay["SMA50"] = df_detay["Close"].rolling(window=50).mean()
        df_detay["SMA200"] = df_detay["Close"].rolling(window=200).mean()
        st.line_chart(df_detay[["Close", "SMA50", "SMA200"]])

        st.markdown("---")

        # 📰 Şirket ve Piyasa Haberleri Sekmesi
        st.subheader(f"📰 {secilen_kuresel} Son Küresel Basın ve Haber Akışı")
        if haberler:
          for h in haberler:
            st.markdown(f"- **[{h['zaman']}]** [{h['baslik']}]({h['link']})")
        else:
          st.info("Bu hisse için güncel haber akışı bulunamadı.")
      else:
        st.warning("Hisse verisi alınamadı.")
