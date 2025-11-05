# Pharos Asseto Auto Bot

🤖 Bot otomatis untuk subscribe di Asseto platform menggunakan USDT di Atlantic Chain

## 📋 Fitur

- ✅ Multi-wallet support (multiple private keys)
- ✅ Auto approval USDT token
- ✅ Batch subscribe dengan jumlah custom (1-1000)
- ✅ Retry mechanism untuk failed transactions
- ✅ Colored console output untuk monitoring
- ✅ Nonce management otomatis
- ✅ Gas price optimization

## 🔧 Requirement

- Python 3.7+
- pip (Python package manager)

## 📦 Installation

1. Clone repository ini:
```bash
git clone https://github.com/febriyan9346/Pharos-Asseto-Auto-Bot.git
cd Pharos-Asseto-Auto-Bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy dan edit file `.env`:
```bash
cp .env.example .env
```

4. Edit file `.env` dan masukkan private key wallet Anda:
```
PRIVATEKEY_1=0xYOUR_PRIVATE_KEY_HERE
PRIVATEKEY_2=0xYOUR_SECOND_PRIVATE_KEY_HERE
# Tambahkan lebih banyak dengan format PRIVATEKEY_3, PRIVATEKEY_4, dst
```

## 🚀 Cara Menggunakan

1. Pastikan wallet Anda memiliki:
   - USDT di Atlantic Chain
   - Native token untuk gas fee

2. Jalankan bot:
```bash
python bot.py
```

3. Masukkan jumlah subscribe yang diinginkan (1-1000)

4. Bot akan otomatis:
   - Approve USDT token
   - Melakukan subscribe sejumlah yang diminta
   - Menampilkan status setiap transaksi

## ⚙️ Konfigurasi

Bot menggunakan konfigurasi berikut:

- **RPC URL**: https://atlantic.dplabs-internal.com
- **Chain ID**: 688689
- **USDT Address**: 0xe7e84b8b4f39c507499c40b4ac199b050e2882d5
- **Subscribe Contract**: 0x56f4add11d723412d27a9e9433315401b351d6e3
- **Subscribe Amount**: 0.0001 USDT per subscribe
- **Gas Limit**: 200,000

## 📝 Format Private Key

Anda bisa memasukkan private key dengan berbagai format:
- `0x1234...` (dengan prefix 0x)
- `1234...` (tanpa prefix)

Bot akan otomatis menormalkan format.

## 🔐 Keamanan

⚠️ **PENTING**: 
- Jangan pernah share file `.env` Anda
- Jangan commit private key ke repository
- Gunakan wallet testing untuk percobaan awal
- File `.env` sudah ada di `.gitignore` untuk keamanan

## 📊 Output

Bot akan menampilkan:
- ✅ Status koneksi RPC
- ✅ Jumlah wallet yang terdeteksi
- ✅ Balance USDT setiap wallet
- ✅ Status approval token
- ✅ Progress setiap transaksi subscribe
- ✅ Summary success/failed transactions

## 🐛 Troubleshooting

### RPC Connection Failed
- Periksa koneksi internet Anda
- Pastikan RPC URL masih aktif

### Insufficient Balance
- Pastikan wallet memiliki cukup USDT
- Pastikan ada native token untuk gas fee

### Transaction Failed
- Bot akan otomatis retry dengan nonce yang benar
- Periksa gas price jika sering gagal

## 🤝 Contributing

Pull requests are welcome! Untuk perubahan besar, silakan buka issue terlebih dahulu.

## 📄 License

MIT License - lihat file [LICENSE](LICENSE) untuk detail

## ⚠️ Disclaimer

Bot ini dibuat untuk tujuan edukasi. Gunakan dengan risiko Anda sendiri. Developer tidak bertanggung jawab atas kehilangan dana atau masalah lainnya yang mungkin timbul dari penggunaan bot ini.

## 📞 Support

Jika ada pertanyaan atau masalah, silakan buka issue di repository ini.

---

**Happy Subscribing! 🚀**
