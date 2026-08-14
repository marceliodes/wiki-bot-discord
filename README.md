# Wikipedia Discord Bot

A Discord bot built with Python that allows users to search, summarize, and explore Wikipedia articles directly within Discord channels using rich embeds.

## Features

- Search Wikipedia articles for top matching terms.
- Fetch concise 5-sentence summaries with direct source links and images.
- Discover random Wikipedia topics on demand.
- Simple command interface using the `>w` prefix.
- Secure configuration using environment variables for tokens.

## Prerequisites

To run this bot, ensure your system meets the following minimum requirements:

- **Python:** Version 3.8 or higher (3.10+ recommended)
- **Libraries:**
  - discord.py >= 2.0.0
  - wikipedia >= 1.4.0
  - python-dotenv >= 1.0.0

## Discord Developer Portal Configuration

Before starting the bot, configure your Discord Application:

1. Open the [Discord Developer Portal](https://discord.com/developers/applications).
2. Create a new Application (or select your existing application).
3. Go to the **Bot** tab on the left-hand menu.
4. Copy or reset your **Bot Token** (store this securely).
5. Scroll down to **Privileged Gateway Intents**.
6. Enable **MESSAGE CONTENT INTENT** (toggle to ON).
7. Save your changes.

## Installation and Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-username/your-repo-name.git
   cd your-repo-name
   ```

2. **Create a virtual environment:**

   ```bash
   python3 -m venv .venv
   ```

3. **Activate the virtual environment:**

   - **Linux / macOS:**

     ```bash
     source .venv/bin/activate
     ```

   - **Windows (Command Prompt):**

     ```cmd
     .venv\Scripts\activate.bat
     ```

   - **Windows (PowerShell):**

     ```powershell
     .venv\Scripts\Activate.ps1
     ```

4. **Install required packages:**

   ```bash
   pip install discord.py wikipedia python-dotenv
   ```

5. **Configure environment variables:**

   Create a `.env` file in the root directory (alongside `main.py`):

   ```
   DISCORD_TOKEN=your_actual_bot_token_here
   ```

## Running the Bot

Start the bot by running `main.py` inside your active virtual environment:

```bash
python3 main.py
```

### Local Hosting Behavior

Running the script hosts the bot directly on your local machine. Terminating the terminal session or shutting down the computer will stop the process and take the bot offline.

## Available Commands

| Command | Syntax | Description |
|---|---|---|
| **Search** | `>w search <term>` | Displays up to 20 matching Wikipedia article titles. |
| **Wiki** | `>w wiki <term>` | Displays a 5-sentence summary and image from the requested page. |
| **Random** | `>w random` | Fetches a summary and image for a random Wikipedia page. |
| **About** | `>w about` | Displays bot information and licensing credits. |
| **Help** | `>w help` | Shows a list of commands and usage syntax. |

## License

This project is licensed under the **GNU General Public License v3.0 (GPLv3)**.

Permissions of this strong copyleft license are conditioned on making available complete source code of licensed works and modifications under the same license. Copyright and license notices must be preserved.

See the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.html) for full details.
