# ⚡ ronymx

A powerful, lightweight, and fast Python-based network utility tool designed for DNS analysis, WHOIS information gathering, and system diagnostics. Fully optimized to run smoothly on **Termux (Android)** and **Linux** environments.

---

## 🚀 Features
* 🔍 **DNS Querying:** Quick and reliable DNS lookups using `dnspython`.
* 🌐 **WHOIS Lookup:** Fetch domain registration details and host information instantly with `python-whois`.
* ⚡ **Smart Termux Setup:** Fully optimized for Termux, handles existing directories automatically without throwing errors.
* 🎨 **Interactive Terminal UI:** User-friendly CLI experience.

---

## 🛠️ Quick Installation & Run (Single Command)

Copy and paste this smart command into your Termux app. It will automatically detect if you already have the folder, install dependencies, and run the tool instantly:

```bash
pkg update && pkg upgrade -y && pkg install git python -y && pip install requests dnspython python-whois && ([ -d "ronymx" ] && cd ronymx || git clone [https://github.com/ronymollik32/ronymx.git](https://github.com/ronymollik32/ronymx.git) && cd ronymx) && python ronymx.py
```

---

## 📖 Manual Installation

If you prefer to set it up step-by-step:

### 1. Install Requirements & Dependencies
```bash
pkg update && pkg upgrade -y
pkg install git python -y
pip install requests dnspython python-whois
```

### 2. Clone the Repository
```bash
git clone https://github.com/ronymollik32/ronymx.git
```

### 3. Navigate & Run
```bash
cd ronymx
python ronymx.py
```

---

## 📞 Connect With Me

For support, queries, or collaboration, feel free to reach out:

* 💬 **Telegram:** [rxrony_xy](https://telegram.me/rxrony_xy)
* 👤 **Facebook:** [Rony Mollik](https://www.facebook.com/share/1GmfgKzNrY/)

---
> ⚠️ **Disclaimer:** This tool is developed for educational and security auditing purposes only. The developer is not responsible for any misuse.
