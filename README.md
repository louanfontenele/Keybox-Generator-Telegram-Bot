# Keybox Generator Telegram Bot 🚀🔑

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Telegram bot that generates Android `keybox.xml` files for device attestation. Built with `python-telegram-bot` and OpenSSL.  Features user limits, a VIP system, and an admin panel for managing users.

## ✨ Features

*   **⚡️ Instant Keybox Generation:** Create `keybox.xml` files with `/generate` or a button tap.
*   **🤖 Interactive Interface:**  Uses Telegram's inline keyboards.
*   **📦 File & Text Output:** Receive the keybox as a file or as text in the chat.
*   **🧐 Clear Error Handling:** Informative error messages.
*   **❓ Help & Source Code:**  `/help` command links to the GitHub repo.
*   **🔒 Secure Configuration:**  Uses a `.env` file for the bot token.
*   **⚙️ Easy Setup:** `requirements.txt` for easy dependency installation.
*   **👤 User Limits:**  Regular users have a daily limit (default: 5 keyboxes).
*   **👑 VIP Status:**  Admin can grant VIP status to remove limits.
*   **🛡️ Admin Panel:** `/admin` command (for admin user) to manage users and view data.
*   **💾 Data Persistence:**  User data is saved to `user_data.json`.

## 📝 Requirements

*   Python 3.7+
*   `python-telegram-bot[all]` (Install: `pip install -r requirements.txt`)
*   `python-dotenv` (Install: `pip install -r requirements.txt`)
*   OpenSSL (usually pre-installed; see below)

## ⬇️ Installation and Usage

1.  **Clone:**
    ```bash
    git clone https://github.com/CRZX1337/Keybox-Generator-Telegram-Bot.git
    cd Keybox-Generator-Telegram-Bot
    ```

2.  **Virtual Environment (Recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # Linux/macOS
    venv\Scripts\activate      # Windows
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **`.env` File (Secret!):**
    ```
    TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN_HERE
    ```
    **Important:** `.env` file MUST be in your `.gitignore`.

5. **Set Admin User ID:**
  Open `main.py` and change the value of `ADMIN_USER_ID` to *your* Telegram user ID.

6.  **Run:**
    ```bash
    python main.py
    ```

7.  **Telegram:**
    *   `/start`:  Welcome message.
    *   `/generate`: Create a keybox (or use the button).
    *   `/help`: Get help.
    *   `/admin`: Access the admin panel (if you're the admin).

## Obtaining a Telegram Bot Token

1.  Open Telegram, search for **@BotFather**.
2.  Send `/newbot`.
3.  Follow prompts, and paste the given Token in the `.env` file.

## OpenSSL Installation (if needed)

*   **Debian/Ubuntu:** `sudo apt-get update && sudo apt-get install openssl`
*   **Fedora/CentOS/RHEL:** `sudo yum install openssl`
*   **macOS:** `brew install openssl` (with Homebrew)
*   **Windows:**  Download OpenSSL (e.g., [https://slproweb.com/products/Win32OpenSSL.html](https://slproweb.com/products/Win32OpenSSL.html)).  Ensure `openssl` is in your PATH.

## 🤝 Contributing

Contributions welcome!

## 📜 License

MIT License (see the [LICENSE](LICENSE) file).
