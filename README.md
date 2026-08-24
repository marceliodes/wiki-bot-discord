# Wikipedia Discord Bot

A Python Discord bot for searching, summarizing, and exploring Wikipedia through
public slash-command responses.

## Features

- Search Wikipedia for up to 20 matching article titles.
- Read five-sentence article summaries with source links and thumbnails.
- Discover random Wikipedia articles.
- Use a discoverable `/wiki` slash-command group instead of message prefixes.
- Show the command, requester, and input at the beginning of every response so
  everyone in the channel understands its context.

## Requirements

- Python 3.8 or newer (Python 3.10+ recommended)
- A Discord application and bot token

Install the pinned dependencies with:

```bash
pip install -r requirements.txt
```

## Discord Application Setup

1. Open the [Discord Developer Portal](https://discord.com/developers/applications)
   and create or select an application.
2. On the **Bot** page, create the bot and copy its token. The Message Content
   privileged intent is not required and can remain disabled.
3. In **OAuth2 > URL Generator**, select the `bot` and `applications.commands`
   scopes, select the permissions needed to view and send messages in the target
   channels, and use the generated URL to install the bot.
4. If the bot was installed previously without application commands, reinstall it
   using a URL containing both scopes.

## Installation

1. Clone the repository and enter it:

   ```bash
   git clone https://github.com/your-username/your-repo-name.git
   cd your-repo-name
   ```

2. Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

   On Windows PowerShell, activate it with `.venv\Scripts\Activate.ps1`.

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and replace the placeholder with the bot token:

   ```dotenv
   DISCORD_TOKEN=your_actual_bot_token_here
   ```

## Running the Bot

```bash
python3 main.py
```

At startup, the bot globally synchronizes its `/wiki` command group with Discord.
Global command changes may take some time to appear in every server. The terminal
logs the synchronization count and connection status. Stopping the process takes
the bot offline.

## Commands

| Command | Description |
|---|---|
| `/wiki search query:<text>` | Display up to 20 matching Wikipedia article titles. |
| `/wiki article title:<text>` | Display a five-sentence article summary, image, and source link. |
| `/wiki random` | Display a random Wikipedia article. |
| `/wiki about` | Display bot information and licensing credits. |
| `/wiki help` | Display the command list. |

All replies are public. A response starts with context similar to:

```text
Command used: /wiki search • Requested by: @member • Query: “Ada Lovelace”
```

The requester is displayed without generating a new mention notification.

## Project Structure

- `main.py` configures and starts the Discord client and synchronizes commands.
- `wiki_bot/commands.py` defines the `/wiki` command group and interaction flow.
- `wiki_bot/service.py` runs the synchronous Wikipedia client away from Discord's
  event loop.
- `wiki_bot/responses.py` creates consistent context lines and embeds.
- `tests/` contains network-free unit tests.

## Testing

```bash
python3 -m unittest discover -s tests -v
```

## License

This project is licensed under the **GNU General Public License v3.0 (GPLv3)**.
See the [GNU GPL v3](https://www.gnu.org/licenses/gpl-3.0.html) for details.
