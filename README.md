# nextmove-notifier 🚗⚡

Monitors [nextmove.de](https://nextmove.de) for new EV rental deals and sends Telegram notifications.

## What it monitors

- **Last-Minute-Angebote** — discounted rent gap offers (via API)
- **Kostenlose Überführungsfahrten** — free one-way test drives (via HTML scraping)

## Setup

### 1. Create a Telegram Bot

1. Open Telegram, search for **@BotFather**
2. Send `/newbot`, follow the prompts
3. Copy the bot token

### 2. Get your Chat ID

1. Send any message to your new bot
2. Visit `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
3. Find `"chat":{"id": 123456789}` in the response

### 3. Install

```bash
git clone <this-repo> && cd nextmove-notifier
bash install.sh
nano /opt/nextmove-notifier/.env   # paste your token + chat ID
```

### 4. Test

```bash
/opt/nextmove-notifier/run.sh
```

You should see log output and (on first run) Telegram messages for all current offers.

## How it works

Every 15 minutes (via cron):

1. Fetches current rent gap offers from nextmove booking API
2. Scrapes the Überführungsfahrten page
3. Compares against previously seen offers (`state.json`)
4. Sends Telegram messages for anything new
5. Updates `state.json`

## Files

```
nextmove_notifier.py   # Main script (~200 lines)
requirements.txt       # Python dependencies
.env.example           # Config template
install.sh             # One-command installer
tests/                 # Test suite (44 tests)
state.json             # Auto-created: tracks seen offers
```

## Running tests

```bash
cd nextmove-notifier
python3 -m unittest discover -s tests -v
```

## Uninstall

```bash
crontab -e   # remove the nextmove line
sudo rm -rf /opt/nextmove-notifier
```
