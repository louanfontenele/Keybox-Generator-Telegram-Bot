# Keybox Generator Telegram Bot 🚀🔑

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Telegram bot that generates Android `keybox.xml` files for device attestation. Built with `python-telegram-bot` and OpenSSL. Easy to deploy and use, featuring a clean and interactive interface with inline keyboards.

## ✨ Features

*   **⚡️ Instant Keybox Generation:** Create `keybox.xml` files effortlessly using the `/generate` command or a simple button tap.
*   **🤖 Interactive & Intuitive:**  Leverages Telegram's inline keyboards for a streamlined and user-friendly experience.
*   **📦 File & Text Output:** Receive the generated keybox as a convenient file attachment or view the XML directly within the chat – the choice is yours!
*   **🧐 Clear Error Handling:**  Provides informative error messages should any issues arise during key generation.
*   **❓ Help & Source Code Access:**  Utilize the `/help` command to access the GitHub repository containing comprehensive documentation and the source code.
*   **🔒 Secure Configuration:**  Employs a `.env` file to securely store your bot token, ensuring its confidentiality.
*   **⚙️ Effortless Setup:**  Includes a `requirements.txt` file to facilitate easy installation of all required dependencies.

## 📝 Requirements

*   Python 3.7+
*   `python-telegram-bot[all]` (Install using: `pip install -r requirements.txt`)
*   `python-dotenv` (Install using: `pip install -r requirements.txt`)
*   OpenSSL (typically pre-installed on Linux/macOS; see installation instructions below if needed).

## ⬇️ Installation and Usage

1.  **Clone the Repository:**

    ```bash
    git clone https://github.com/CRZX1337/Keybox-Generator-Telegram-Bot.git
    cd Keybox-Generator-Telegram-Bot
    ```

2.  **Set Up a Virtual Environment (Strongly Recommended):**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # For Linux/macOS
    venv\Scripts\activate      # For Windows
    ```

3.  **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Create a `.env` File (and Keep It Secret!):**

    ```
    TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN_HERE  # Replace with your actual bot token!
    ```

    **CRITICAL:** Ensure your `.env` file is listed in your `.gitignore` file to prevent accidental exposure of your bot token.

5.  **Run the Bot:**

    ```bash
    python main.py
    ```

6.  **Interact with the Bot in Telegram:**

    *   Use `/start` to initiate a conversation.
    *   Use `/generate` (or the inline keyboard button) to generate a keybox.
    *   Use `/help` for assistance and to access the source code link.

## Obtaining a Telegram Bot Token

1.  Open Telegram and search for the **@BotFather** bot.
2.  Start a chat with BotFather and send the `/newbot` command.
3.  Follow the prompts to give your bot a name and a username.
4.  BotFather will provide you with a bot token.  Copy this token and paste it into your `.env` file (as shown above).

## OpenSSL Installation (If Necessary)

*   **Debian/Ubuntu:**

    ```bash
    sudo apt-get update && sudo apt-get install openssl
    ```

*   **Fedora/CentOS/RHEL:**

    ```bash
    sudo yum install openssl
    ```

*   **macOS:**

    ```bash
    brew install openssl
    ```
    (If you use Homebrew)

*   **Windows:**  Download and install a suitable OpenSSL binary distribution (e.g., from [https://slproweb.com/products/Win32OpenSSL.html](https://slproweb.com/products/Win32OpenSSL.html)). Ensure the `openssl` executable is included in your system's PATH environment variable.

## 🤝 Contributing

Contributions, bug reports, and feature requests are welcome!  Feel free to open issues or submit pull requests on GitHub.

## 📜 License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.
