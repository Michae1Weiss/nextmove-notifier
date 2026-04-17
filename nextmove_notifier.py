"""
nextmove-notifier: Monitor nextmove.de for new Last-Minute-Angebote and Überführungsfahrten.
Sends Telegram notifications for new offers.
"""

import json
import logging
import os
import re
import ssl
import sys
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

BASE_URL = "https://nextmove-booking.azurewebsites.net/api/v1"
TESTDRIVES_URL = "https://nextmove.de/ueberfuehrungsfahrten/"
AKTIONEN_URL = "https://nextmove.de/aktionen/"
ANFRAGE_URL = "https://nextmove.de/anfrage/?reason=219740009"

DEFAULT_STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state.json")

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "de",
    "content-type": "application/json",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "user-agent": USER_AGENT,
}

BROWSER_HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "accept-language": "de-DE,de;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "user-agent": USER_AGENT,
}


# ---------------------------------------------------------------------------
# SSL adapter — fixes SSLv3 handshake failures with some servers
# ---------------------------------------------------------------------------

class TLSAdapter(HTTPAdapter):
    """Force TLS 1.2+ and use a broader cipher set for compatibility."""
    def init_poolmanager(self, *args, **kwargs):
        ctx = ssl.create_default_context()
        ctx.set_ciphers("DEFAULT:@SECLEVEL=1")
        ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        kwargs["ssl_context"] = ctx
        return super().init_poolmanager(*args, **kwargs)


def _session() -> requests.Session:
    """Create a requests session with TLS adapter mounted."""
    s = requests.Session()
    s.mount("https://", TLSAdapter())
    return s

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# API client
# ---------------------------------------------------------------------------

def fetch_session_token() -> str | None:
    """Start a session and return the API token."""
    try:
        resp = _session().post(
            f"{BASE_URL}/session/start",
            headers=HEADERS,
            json={"referral": None},
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json().get("token")
    except Exception as e:
        log.error("Failed to fetch session token: %s", e)
        return None


def fetch_rent_gaps(token: str) -> list:
    """Fetch current Last-Minute rent gap offers."""
    try:
        resp = _session().get(
            f"{BASE_URL}/booking/rentGaps",
            headers={**HEADERS, "x-api-token": token},
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json().get("rentGaps", [])
    except Exception as e:
        log.error("Failed to fetch rent gaps: %s", e)
        return []


def fetch_master_data(token: str) -> dict:
    """Fetch master data (models, sites) for resolving names."""
    try:
        resp = _session().get(
            f"{BASE_URL}/session/masterData",
            headers={**HEADERS, "x-api-token": token},
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        log.error("Failed to fetch master data: %s", e)
        return {}


def fetch_testdrives_html() -> str:
    """Fetch the Überführungsfahrten page HTML."""
    try:
        resp = _session().get(TESTDRIVES_URL, headers=BROWSER_HEADERS, timeout=15)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        log.error("Failed to fetch testdrives page: %s", e)
        return ""


# ---------------------------------------------------------------------------
# HTML parser (Testdrives)
# ---------------------------------------------------------------------------

def parse_testdrives_html(html: str) -> list[dict]:
    """
    Parse the Überführungsfahrten HTML page.
    Returns list of {"city": str, "text": str} for each real offer (excluding "keine").
    """
    if not html.strip():
        return []

    soup = BeautifulSoup(html, "html.parser")
    results = []

    # Find all h3 headers which contain city names
    h3s = soup.find_all("h3")

    for h3 in h3s:
        city = h3.get_text(strip=True)
        if not city:
            continue

        # Collect offers: look at subsequent <li> elements containing <strong> or <b>
        # The offers can be in sibling <ul> or parent's sibling <ul> (Solingen edge case)
        offers = []

        # Strategy 1: offers in a <ul> that is a sibling of the <h3> (inside same <li>)
        parent_li = h3.find_parent("li")
        if parent_li:
            for sub_li in parent_li.find_all("li"):
                text = sub_li.get_text(strip=True)
                if text and text.lower() != "keine":
                    # Don't re-add the parent or h3 text
                    if text != city:
                        offers.append(text)

        # Strategy 2: Solingen-style — h3 is in a <li> with no sub-<ul>,
        # and offers are in the NEXT <ul> block.
        # Only trigger when the parent <li> has no nested <ul> at all;
        # "keine" cities have a <ul> with filtered content and must not fall through here.
        if not offers and parent_li and not parent_li.find("ul"):
            parent_ul = parent_li.find_parent("ul")
            if parent_ul:
                next_ul = parent_ul.find_next_sibling("ul")
                if next_ul:
                    for li in next_ul.find_all("li"):
                        if li.find("li"):  # skip wrapper elements that contain nested lis
                            continue
                        text = li.get_text(strip=True)
                        if text and text.lower() != "keine":
                            offers.append(text)

        for text in offers:
            results.append({"city": city, "text": text})

    return results


# ---------------------------------------------------------------------------
# Key generation (for deduplication)
# ---------------------------------------------------------------------------

def rent_gap_key(gap: dict) -> str:
    """Generate a unique key for a rent gap offer."""
    return f"{gap['vehicleId']}|{gap['startDate']}|{gap['endDate']}"


def testdrive_key(entry: dict) -> str:
    """Generate a unique key for a testdrive offer."""
    return f"{entry['city']}|{entry['text']}"


# ---------------------------------------------------------------------------
# State management
# ---------------------------------------------------------------------------

def load_state(path: str) -> dict:
    """Load previously seen offer keys from JSON file."""
    if not os.path.exists(path):
        return {"rent_gaps": [], "testdrives": []}
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {"rent_gaps": [], "testdrives": []}


def save_state(path: str, state: dict) -> None:
    """Save seen offer keys to JSON file."""
    with open(path, "w") as f:
        json.dump(state, f, indent=2)


# ---------------------------------------------------------------------------
# Diff logic
# ---------------------------------------------------------------------------

def find_new_rent_gaps(gaps: list, seen_keys: list) -> list:
    """Return only rent gaps not in seen_keys."""
    seen = set(seen_keys)
    return [g for g in gaps if rent_gap_key(g) not in seen]


def find_new_testdrives(entries: list, seen_keys: list) -> list:
    """Return only testdrive entries not in seen_keys."""
    seen = set(seen_keys)
    return [e for e in entries if testdrive_key(e) not in seen]


# ---------------------------------------------------------------------------
# Message formatting
# ---------------------------------------------------------------------------

def _resolve_model(master_data: dict, model_id: str, variant_id: str) -> tuple[str, str]:
    """Resolve model and variant names from master data."""
    model_name = "Unbekanntes Modell"
    variant_name = ""
    for m in master_data.get("models", []):
        if m["modelId"] == model_id:
            model_name = m["name"]
            for v in m.get("modelVariants", []):
                if v["modelVariantId"] == variant_id:
                    variant_name = v["name"]
                    break
            break
    return model_name, variant_name


def _format_date(iso_date: str) -> str:
    """Convert 2026-04-21 → 21.04."""
    try:
        d = datetime.strptime(iso_date, "%Y-%m-%d")
        return d.strftime("%d.%m.")
    except ValueError:
        return iso_date


def _format_price(price: float) -> str:
    """Format price German-style: 1.234,56 €"""
    # Simple approach: format with 2 decimals, swap . and ,
    s = f"{price:,.2f}"  # e.g. "1,234.56"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{s} €"


def _format_kms(kms: int) -> str:
    """Format km German-style: 1.300"""
    return f"{kms:,}".replace(",", ".")


def build_rent_gap_message(gap: dict, master_data: dict) -> str:
    """Build a Telegram notification message for a rent gap offer."""
    model_name, variant_name = _resolve_model(
        master_data, gap.get("modelId", ""), gap.get("modelVariantId", "")
    )
    title = model_name
    if variant_name:
        title += f" {variant_name}"

    site = gap.get("siteName", "?")
    start = _format_date(gap["startDate"])
    end = _format_date(gap["endDate"])
    days = gap.get("bookingDays", "?")
    price = _format_price(gap["rentPrice"])
    discount = gap.get("discountPercentage", 0)
    kms = _format_kms(gap["includedKms"])

    lines = [
        f"🚗 *Neues Last-Minute-Angebot!*",
        f"*{title}* in {site}",
        f"📅 {start} – {end} ({days} Tage)",
        f"💰 {price} (-{discount}%)",
        f"📍 {kms} km inkl.",
        f"[Jetzt buchen →]({AKTIONEN_URL})",
    ]
    return "\n".join(lines)


def build_testdrive_message(entry: dict) -> str:
    """Build a Telegram notification message for a testdrive offer."""
    lines = [
        f"🆓 *Neue Überführungsfahrt!*",
        f"📍 *{entry['city']}*",
        f"{entry['text']}",
        f"[Anfrage senden →]({ANFRAGE_URL})",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Telegram
# ---------------------------------------------------------------------------

def send_telegram_message(text: str, bot_token: str, chat_id: str) -> None:
    """Send a message via Telegram Bot API."""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    try:
        resp = _session().post(url, json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True,
        }, timeout=10)
        if resp.status_code != 200:
            log.warning("Telegram API returned %s: %s", resp.status_code, resp.text)
    except Exception as e:
        log.error("Failed to send Telegram message: %s", e)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    state_file = os.environ.get("STATE_FILE", DEFAULT_STATE_FILE)

    if not bot_token or not chat_id:
        log.error("Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables!")
        sys.exit(1)

    state = load_state(state_file)

    # --- Rent Gaps (Last-Minute-Angebote) ---
    log.info("Checking Last-Minute-Angebote...")
    token = fetch_session_token()
    if token:
        gaps = fetch_rent_gaps(token)
        master_data = fetch_master_data(token)

        new_gaps = find_new_rent_gaps(gaps, state["rent_gaps"])
        log.info("Found %d rent gaps, %d new", len(gaps), len(new_gaps))

        for gap in new_gaps:
            msg = build_rent_gap_message(gap, master_data)
            send_telegram_message(msg, bot_token, chat_id)
            log.info("Notified: %s", rent_gap_key(gap))

        # Update state with ALL current keys (not just new ones)
        state["rent_gaps"] = [rent_gap_key(g) for g in gaps]
    else:
        log.warning("Skipping rent gaps — no session token")

    # --- Testdrives (Überführungsfahrten) ---
    log.info("Checking Überführungsfahrten...")
    html = fetch_testdrives_html()
    if html:
        entries = parse_testdrives_html(html)
        new_entries = find_new_testdrives(entries, state["testdrives"])
        log.info("Found %d testdrives, %d new", len(entries), len(new_entries))

        for entry in new_entries:
            msg = build_testdrive_message(entry)
            send_telegram_message(msg, bot_token, chat_id)
            log.info("Notified: %s", testdrive_key(entry))

        # Update state with ALL current keys
        state["testdrives"] = [testdrive_key(e) for e in entries]
    else:
        log.warning("Skipping testdrives — no HTML")

    save_state(state_file, state)
    log.info("Done.")


if __name__ == "__main__":
    main()