# Direktori Scripts

Script utilitas untuk pemrosesan data dan persiapan model.

## Script yang Tersedia

### extract_tlds.py

Mengekstrak TLD unik dari dataset training dan menyimpannya ke `tld_list.json`.

**Penggunaan:**

```bash
cd phising-detection-api
python scripts/extract_tlds.py
```

**Requirements:**

- pandas
- Dataset training dalam format CSV dengan kolom TLD

**Output:**

- `tld_list.json` - List dari TLD unik dari data training

**Catatan:** Script ini hanya diperlukan jika Anda melatih ulang model dengan dataset yang berbeda. File `tld_list.json` yang ada saat ini sudah di-generate dan disertakan dalam repository.
