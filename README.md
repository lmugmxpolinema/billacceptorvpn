# 📡 VPN PPTP Auto Setup Script

Script ini digunakan untuk **menginstal dan mengonfigurasi VPN PPTP secara otomatis** di sistem berbasis Debian/Ubuntu. Script akan:

- Menginstal semua dependensi (pptp-linux, ufw)
- Membuat dan mengedit konfigurasi VPN
- Mengatur `rc.local` dan `crontab` agar VPN otomatis aktif saat boot
- Menyimpan log koneksi ke direktori yang ditentukan

---

## 🚀 Cara Clone Repositori

```bash
git clone https://github.com/blablabla/vpn.git
cd vpn
```

> Ganti `https://github.com/blablabla/vpn.git` dengan URL GitHub kamu yang sebenarnya.

---

## ⚙️ Cara Penggunaan

1. Jalankan script dengan `sudo`:
   
   ```bash
   sudo python3 setup_vpn.py
   ```

2. Ikuti instruksi yang muncul:
   - Masukkan **IP Gateway VPN**
   - Masukkan **Username VPN**
   - Masukkan **Password VPN**
   - Masukkan **path folder untuk log** (misalnya: `/var/log/vpnlog`)

3. Setelah selesai:
   - File konfigurasi VPN akan dibuat di `/etc/ppp/peers/vpn`
   - VPN akan otomatis aktif saat sistem boot
   - Log koneksi disimpan ke `logvpn.txt` di folder log

---

## 🛠 Struktur Proyek

```
vpn/
├── setup_vpn.py       # Script utama untuk konfigurasi VPN
├── README.md          # Panduan penggunaan
```

---

## 🔒 Catatan Penting

- Script ini akan **mengganti isi dari `/etc/rc.local`** — pastikan tidak ada konfigurasi penting lain di file tersebut sebelum menjalankan.
- UFW akan diatur untuk mengizinkan semua koneksi masuk (`allow from 0.0.0.0/0`) — sesuaikan dengan kebijakan keamanan jaringan Anda.
- Script ini hanya bekerja untuk **sistem berbasis Debian/Ubuntu**.

---

## 📬 Kontribusi

Pull request dan issue sangat terbuka jika kamu ingin membantu pengembangan script ini lebih lanjut 🚀

---

## 🧾 Lisensi

Script ini berlisensi **MIT License** — bebas digunakan, disalin, dimodifikasi, bahkan untuk tujuan komersial.

---

## 🙏 Terima Kasih

Dibuat dengan ❤️ untuk kebutuhan automasi VPN PPTP.