# GCE Altra Guide

Sistem panduan **Salin & Tampal** untuk GCE Exam Labs (Google Certified Educator).
Semua teks kritikal (nama kelas, tajuk tugasan, soalan, mesej) menjadi **butang salin 📋** —
klik kiri untuk salin ejaan 100% tepat, kemudian klik kanan → Paste di destinasi.

## Fail

| Fail | Fungsi |
|---|---|
| `index.html` | **Mod Admin** — buka untuk sunting/tambah panduan. Data disimpan automatik dalam browser (localStorage). |
| `GCE-Altra-Guide-SAMPLE.html` | Contoh fail kongsi (baca-sahaja) yang dijana oleh butang 📤 Kongsi. |
| `AltraPaste.pyw` | **Pembantu salin & tampal pantas** (Windows, perlu Python). Pilih teks = salin terus · klik KANAN = tampal terus. |
| `PDF Guider/` | PDF asal (sumber kandungan 6 lab). |

## AltraPaste v2 — salin dengan pilih, tampal dengan klik kanan

Dwiklik `AltraPaste.pyw` — tetingkap kecil muncul di penjuru kanan atas dengan
dua suis dan pratonton clipboard terkini. Kedua-dua mod mula dalam keadaan **ON**.

| Mod | Fungsi | Hotkey |
|---|---|---|
| **AUTO-COPY** | **Pilih/highlight teks** (seret tetikus) di mana-mana app = teks terus disalin. Setiap pilihan baru **menggantikan** salinan lama secara automatik. | F7 |
| **PASTE** | **Klik KANAN** di mana-mana medan teks = tampal terus, tiada menu. | F8 |

Aliran kerja penuh tanpa papan kekunci: *pilih teks → klik kanan di destinasi → siap.*

- Tahan **Shift** sambil klik kanan untuk menu klik-kanan biasa.
- Pratonton "CLIPBOARD TERKINI" dalam tetingkap menunjukkan apa yang akan ditampal.
- Kedua-dua mod **dilangkau secara automatik dalam terminal** (cmd, PowerShell, Windows
  Terminal, Git Bash) — Ctrl+C di situ membatalkan arahan, jadi AltraPaste tidak masuk campur.
- Tutup tetingkap AltraPaste untuk berhenti sepenuhnya.

> Nota: komputer penerima perlu Python untuk AltraPaste. Tanpa Python, mereka masih boleh guna Ctrl+V seperti biasa — fail HTML panduan berfungsi sendiri.

## Cara guna (Admin — anda)

1. Buka `index.html` (dwiklik sahaja — tiada server diperlukan).
2. 6 panduan GCE telah dimuatkan siap sedia (L1: Classroom, Docs, Forms · L2: Calendar, Classroom, Slides).
3. **Sunting**: klik mana-mana blok → ✎. Highlight teks dalam editor → klik butang
   `📋 [[ ]] Tanda Teks` untuk menjadikannya butang salin. Format: `Taip nama: [[Geography]]`
4. **Import dokumen**: butang `📄 Import Dokumen` menerima **.docx / .pptx / .xlsx / .xls / .pdf / .txt** —
   teks diekstrak menjadi blok panduan (boleh jadi panduan baru atau ditambah pada panduan semasa),
   kemudian tanda `[[ ]]` pada teks penting. Import memerlukan internet (perpustakaan penghurai
   dimuat dari CDN); fail .doc / .ppt lama perlu di-Save As ke format baru dahulu.
5. **Kongsi**: klik `📤 Kongsi (Eksport HTML)` → pilih panduan → muat turun satu fail HTML →
   hantar melalui WhatsApp/Telegram/Drive/email. Penerima buka fail itu — baca sahaja, tak boleh sunting.
6. **PDF**: klik `🖨️ Cetak / Simpan PDF` (butang salin dicetak sebagai teks bertanda ✂).
7. **Backup**: `💾 Backup Data (JSON)` — simpan fail JSON; boleh import semula di komputer lain.

## Cara guna (Penerima)

1. Buka fail HTML yang dikongsi.
2. **Klik KIRI** pada kotak biru 📋 → teks disalin (kotak bertukar hijau ✅).
3. Pergi ke Google Classroom/Forms/dll → **klik KANAN → Paste** (atau Ctrl+V).
4. Ada kawasan latihan tampal di bahagian bawah setiap panduan — klik kanan di dalamnya untuk tampal.
