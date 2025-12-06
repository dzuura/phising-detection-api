# Direktori Models

Direktori ini berisi model machine learning terlatih yang digunakan oleh API.

## File yang Diperlukan

- `model.pkl` - Model Random Forest terlatih untuk deteksi phishing

## Informasi Model

- **Tipe**: RandomForestClassifier
- **Fitur yang Diharapkan**: 716
  - 22 fitur dasar
  - 694 fitur TLD one-hot encoded
- **Classes**: [0, 1]
  - 0 = Phishing
  - 1 = Legitimate
- **Versi Training**: scikit-learn 1.6.1
- **Runtime yang Kompatibel**: scikit-learn 1.3.2+

## Setup

1. Letakkan file model terlatih Anda di direktori ini
2. Pastikan nama file sesuai dengan `MODEL_PATH` di file `.env` Anda
3. Path default: `./models/model.pkl`

## Training

Jika Anda perlu melatih ulang model:

1. Siapkan dataset training dengan format yang sesuai
2. Train model Random Forest dengan 716 fitur yang sama:
   - 22 fitur dasar dari analisis URL dan konten
   - 694 fitur TLD dari one-hot encoding (drop_first=True)
3. Save model menggunakan joblib ke file `model.pkl`
4. Letakkan file model di direktori ini
