import pandas as pd
import yfinance as yf

# Seçtiğimiz Küresel Portföy Sepeti
tech_devleri = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA"]
enerji_devleri = ["XOM", "CVX", "SHEL", "TTE", "BP"]
tum_hisseler = tech_devleri + enerji_devleri


def kuresel_piyasayi_tara():
  print("🌐 ABD ve Dünya Enerji Piyasaları Taranıyor...\n")
  rapor_listesi = []

  for hisse in tum_hisseler:
    try:
      # yfinance ile son 6 aylık günlük veriyi çek
      df = yf.download(hisse, period="6mo", interval="1d", progress=False)
      if df is not None and not df.empty:
        # Sütun başlıklarını sadeleştir
        if isinstance(df.columns, pd.MultiIndex):
          df.columns = df.columns.get_level_values(0)

        son_fiyat = float(df["Close"].iloc[-1])

        # Teknik İndikatör: RSI (14) Hesaplama
        delta = df["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        son_rsi = float(rsi.iloc[-1])

        # Basit Alarm / Durum Kontrol Örneği
        durum = "NÖTR"
        if son_rsi < 35:
          durum = "🟢 AŞIRI SATIM (Fırsat Olabilir)"
        elif son_rsi > 65:
          durum = "🔴 AŞIRI ALIM (Dikkat)"

        rapor_listesi.append({
            "Hisse": hisse,
            "Sektör": (
                "Teknoloji" if hisse in tech_devleri else "Enerji / Emtia"
            ),
            "Fiyat ($)": round(son_fiyat, 2),
            "RSI (14)": round(son_rsi, 1),
            "Durum Sinyali": durum,
        })
    except Exception as e:
      print(f"{hisse} verisi alınırken hata oluştu: {e}")

  return pd.DataFrame(rapor_listesi)


if __name__ == "__main__":
  df_matris = kuresel_piyasayi_tara()
  if not df_matris.empty:
    print(df_matris.to_string(index=False))
