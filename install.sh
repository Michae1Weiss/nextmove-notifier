#!/bin/bash
set -e

echo "=== nextmove-notifier installer ==="

INSTALL_DIR="/opt/nextmove-notifier"

# Create directory
sudo mkdir -p "$INSTALL_DIR"
sudo cp nextmove_notifier.py requirements.txt "$INSTALL_DIR/"
sudo chown -R "$USER:$USER" "$INSTALL_DIR"

# Install Python deps
pip3 install -r "$INSTALL_DIR/requirements.txt" --break-system-packages 2>/dev/null || \
pip3 install -r "$INSTALL_DIR/requirements.txt"

# Create .env if it doesn't exist
if [ ! -f "$INSTALL_DIR/.env" ]; then
    sudo cp .env.example "$INSTALL_DIR/.env"
    sudo chown "$USER:$USER" "$INSTALL_DIR/.env"
    echo ""
    echo "⚠️  Edit $INSTALL_DIR/.env with your Telegram credentials!"
    echo "   nano $INSTALL_DIR/.env"
    echo ""
fi

# Create wrapper script that loads .env
cat > /tmp/nextmove-check.sh << 'WRAPPER'
#!/bin/bash
set -a
source /opt/nextmove-notifier/.env
set +a
cd /opt/nextmove-notifier
/usr/bin/python3 nextmove_notifier.py
WRAPPER
sudo mv /tmp/nextmove-check.sh "$INSTALL_DIR/run.sh"
sudo chmod +x "$INSTALL_DIR/run.sh"

# Install crontab entry (every 15 minutes)
CRON_LINE="*/15 * * * * $INSTALL_DIR/run.sh >> /var/log/nextmove-notifier.log 2>&1"
(crontab -l 2>/dev/null | grep -v "nextmove"; echo "$CRON_LINE") | crontab -

echo "✅ Installed to $INSTALL_DIR"
echo "✅ Cron job set: every 15 minutes"
echo ""
echo "Next steps:"
echo "  1. Edit $INSTALL_DIR/.env with your Telegram bot token and chat ID"
echo "  2. Test manually: $INSTALL_DIR/run.sh"
echo "  3. Check logs: tail -f /var/log/nextmove-notifier.log"
echo ""
echo "To get your Telegram chat ID:"
echo "  1. Message your bot on Telegram"
echo "  2. Visit: https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates"
echo "  3. Find your chat ID in the response"
