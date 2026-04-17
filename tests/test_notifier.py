"""Tests for nextmove-notifier — written BEFORE implementation (TDD)."""

import json
import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from datetime import date

# We'll import from our module once it exists
from nextmove_notifier import (
    fetch_session_token,
    fetch_rent_gaps,
    fetch_master_data,
    parse_testdrives_html,
    build_rent_gap_message,
    build_testdrive_message,
    load_state,
    save_state,
    find_new_rent_gaps,
    find_new_testdrives,
    send_telegram_message,
    rent_gap_key,
    testdrive_key,
)


# ---------------------------------------------------------------------------
# Sample data fixtures
# ---------------------------------------------------------------------------

SAMPLE_SESSION_RESPONSE = {"token": "abc123tokenxyz"}

SAMPLE_RENT_GAPS = {
    "rentGaps": [
        {
            "startDate": "2026-04-21",
            "endDate": "2026-04-30",
            "bookingDays": 10,
            "siteId": "site-solingen",
            "siteName": "Solingen",
            "vehicleId": "vehicle-1",
            "modelId": "model-born",
            "belongsTo": 0,
            "modelVariantId": "variant-77kwh",
            "rentPrice": 236.51,
            "includedKms": 1300,
            "pickupTimes": {},
            "discountPercentage": 40,
        },
        {
            "startDate": "2026-04-23",
            "endDate": "2026-05-15",
            "bookingDays": 23,
            "siteId": "site-berlin",
            "siteName": "Berlin",
            "vehicleId": "vehicle-2",
            "modelId": "model-born",
            "belongsTo": 0,
            "modelVariantId": "variant-58kwh",
            "rentPrice": 550.09,
            "includedKms": 2600,
            "pickupTimes": {},
            "discountPercentage": 50,
        },
    ]
}

SAMPLE_MASTER_DATA = {
    "models": [
        {
            "modelId": "model-born",
            "name": "Cupra Born",
            "pricePerDay": 38.70,
            "keyImageURL": "https://example.com/born.png",
            "modelVariants": [
                {"name": "58 kWh", "modelVariantId": "variant-58kwh", "isSelectable": True},
                {"name": "77 kWh", "modelVariantId": "variant-77kwh", "isSelectable": True},
            ],
        },
        {
            "modelId": "model-fiat",
            "name": "Fiat 500e",
            "pricePerDay": 30.54,
            "keyImageURL": "",
            "modelVariants": [
                {"name": "42 kWh", "modelVariantId": "variant-fiat42", "isSelectable": True},
            ],
        },
    ],
    "sites": [
        {"name": "Berlin", "siteId": "site-berlin"},
        {"name": "Solingen", "siteId": "site-solingen"},
    ],
}

SAMPLE_TESTDRIVES_HTML = """
<div class="elementor-widget-theme-post-content">
<h1 class="wp-block-heading">Kostenlose Überführungsfahrten (Testdrives)</h1>
<ul>
<li>
<h3><span style="color: #99cc00;">Berlin</span></h3>
<ul>
<li><strong>VW. ID4 (503) nach Arnstadt, ab dem 27.04., 2 Tage 500 km frei</strong></li>
<li><strong>Tesla Model 3 (100) nach Hamburg, ab sofort, 3 Tage 700 km frei</strong></li>
</ul>
</li>
<li>
<h3><span style="color: #99cc00;">München</span></h3>
<ul>
<li><b>keine</b></li>
</ul>
</li>
<li>
<h3><span style="color: #99cc00;">Hamburg</span></h3>
<ul>
<li><strong>Ford eTransit (105, 177) nach Leipzig, ab sofort, 3 Tage 700 km frei</strong></li>
</ul>
</li>
</ul>
</div>
"""

SAMPLE_TESTDRIVES_EMPTY_HTML = """
<div class="elementor-widget-theme-post-content">
<h1>Kostenlose Überführungsfahrten</h1>
<ul>
<li>
<h3><span style="color: #99cc00;">Berlin</span></h3>
<ul>
<li><b>keine</b></li>
</ul>
</li>
</ul>
</div>
"""


# ---------------------------------------------------------------------------
# Tests: HTML parsing (Testdrives)
# ---------------------------------------------------------------------------

class TestParseTestdrivesHTML(unittest.TestCase):
    def test_parses_offers_grouped_by_city(self):
        result = parse_testdrives_html(SAMPLE_TESTDRIVES_HTML)
        # Should return list of dicts with 'city' and 'text'
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)  # 3 real offers (keine excluded)

    def test_excludes_keine(self):
        result = parse_testdrives_html(SAMPLE_TESTDRIVES_HTML)
        texts = [r["text"] for r in result]
        for t in texts:
            self.assertNotIn("keine", t.lower())

    def test_city_is_extracted(self):
        result = parse_testdrives_html(SAMPLE_TESTDRIVES_HTML)
        cities = [r["city"] for r in result]
        self.assertIn("Berlin", cities)
        self.assertIn("Hamburg", cities)

    def test_text_contains_vehicle_info(self):
        result = parse_testdrives_html(SAMPLE_TESTDRIVES_HTML)
        berlin_offers = [r for r in result if r["city"] == "Berlin"]
        self.assertEqual(len(berlin_offers), 2)
        texts = [r["text"] for r in berlin_offers]
        self.assertTrue(any("ID4" in t for t in texts))
        self.assertTrue(any("Tesla" in t for t in texts))

    def test_empty_page_returns_empty_list(self):
        result = parse_testdrives_html(SAMPLE_TESTDRIVES_EMPTY_HTML)
        self.assertEqual(result, [])

    def test_completely_empty_html(self):
        result = parse_testdrives_html("")
        self.assertEqual(result, [])


# ---------------------------------------------------------------------------
# Tests: Rent gap key generation (for deduplication)
# ---------------------------------------------------------------------------

class TestRentGapKey(unittest.TestCase):
    def test_key_contains_essential_fields(self):
        gap = SAMPLE_RENT_GAPS["rentGaps"][0]
        key = rent_gap_key(gap)
        self.assertIn("vehicle-1", key)
        self.assertIn("2026-04-21", key)
        self.assertIn("2026-04-30", key)

    def test_different_gaps_different_keys(self):
        gaps = SAMPLE_RENT_GAPS["rentGaps"]
        k1 = rent_gap_key(gaps[0])
        k2 = rent_gap_key(gaps[1])
        self.assertNotEqual(k1, k2)


class TestTestdriveKey(unittest.TestCase):
    def test_key_is_based_on_city_and_text(self):
        entry = {"city": "Berlin", "text": "VW ID4 (503) nach Arnstadt"}
        key = testdrive_key(entry)
        self.assertIn("Berlin", key)
        self.assertIn("VW ID4 (503) nach Arnstadt", key)

    def test_different_entries_different_keys(self):
        e1 = {"city": "Berlin", "text": "VW ID4 (503)"}
        e2 = {"city": "Berlin", "text": "Tesla Model 3 (100)"}
        self.assertNotEqual(testdrive_key(e1), testdrive_key(e2))


# ---------------------------------------------------------------------------
# Tests: State management (load / save / diff)
# ---------------------------------------------------------------------------

class TestStateManagement(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.state_file = os.path.join(self.tmpdir, "state.json")

    def tearDown(self):
        if os.path.exists(self.state_file):
            os.remove(self.state_file)
        os.rmdir(self.tmpdir)

    def test_load_state_returns_empty_on_missing_file(self):
        state = load_state(self.state_file)
        self.assertEqual(state, {"rent_gaps": [], "testdrives": []})

    def test_save_and_load_roundtrip(self):
        data = {"rent_gaps": ["key1", "key2"], "testdrives": ["td1"]}
        save_state(self.state_file, data)
        loaded = load_state(self.state_file)
        self.assertEqual(loaded, data)

    def test_save_creates_file(self):
        save_state(self.state_file, {"rent_gaps": [], "testdrives": []})
        self.assertTrue(os.path.exists(self.state_file))

    def test_load_corrupt_file_returns_empty(self):
        with open(self.state_file, "w") as f:
            f.write("NOT JSON {{{{")
        state = load_state(self.state_file)
        self.assertEqual(state, {"rent_gaps": [], "testdrives": []})


# ---------------------------------------------------------------------------
# Tests: Finding new items (diff logic)
# ---------------------------------------------------------------------------

class TestFindNewRentGaps(unittest.TestCase):
    def test_all_new_when_state_empty(self):
        gaps = SAMPLE_RENT_GAPS["rentGaps"]
        new = find_new_rent_gaps(gaps, [])
        self.assertEqual(len(new), 2)

    def test_no_new_when_all_seen(self):
        gaps = SAMPLE_RENT_GAPS["rentGaps"]
        seen = [rent_gap_key(g) for g in gaps]
        new = find_new_rent_gaps(gaps, seen)
        self.assertEqual(len(new), 0)

    def test_only_unseen_returned(self):
        gaps = SAMPLE_RENT_GAPS["rentGaps"]
        seen = [rent_gap_key(gaps[0])]
        new = find_new_rent_gaps(gaps, seen)
        self.assertEqual(len(new), 1)
        self.assertEqual(new[0]["vehicleId"], "vehicle-2")


class TestFindNewTestdrives(unittest.TestCase):
    def test_all_new_when_state_empty(self):
        entries = parse_testdrives_html(SAMPLE_TESTDRIVES_HTML)
        new = find_new_testdrives(entries, [])
        self.assertEqual(len(new), 3)

    def test_no_new_when_all_seen(self):
        entries = parse_testdrives_html(SAMPLE_TESTDRIVES_HTML)
        seen = [testdrive_key(e) for e in entries]
        new = find_new_testdrives(entries, seen)
        self.assertEqual(len(new), 0)

    def test_only_unseen_returned(self):
        entries = parse_testdrives_html(SAMPLE_TESTDRIVES_HTML)
        seen = [testdrive_key(entries[0])]
        new = find_new_testdrives(entries, seen)
        self.assertEqual(len(new), 2)


# ---------------------------------------------------------------------------
# Tests: Message formatting
# ---------------------------------------------------------------------------

class TestBuildRentGapMessage(unittest.TestCase):
    def test_contains_model_name(self):
        gap = SAMPLE_RENT_GAPS["rentGaps"][0]
        msg = build_rent_gap_message(gap, SAMPLE_MASTER_DATA)
        self.assertIn("Cupra Born", msg)

    def test_contains_variant_name(self):
        gap = SAMPLE_RENT_GAPS["rentGaps"][0]
        msg = build_rent_gap_message(gap, SAMPLE_MASTER_DATA)
        self.assertIn("77 kWh", msg)

    def test_contains_site_name(self):
        gap = SAMPLE_RENT_GAPS["rentGaps"][0]
        msg = build_rent_gap_message(gap, SAMPLE_MASTER_DATA)
        self.assertIn("Solingen", msg)

    def test_contains_price(self):
        gap = SAMPLE_RENT_GAPS["rentGaps"][0]
        msg = build_rent_gap_message(gap, SAMPLE_MASTER_DATA)
        self.assertIn("236", msg)

    def test_contains_discount(self):
        gap = SAMPLE_RENT_GAPS["rentGaps"][0]
        msg = build_rent_gap_message(gap, SAMPLE_MASTER_DATA)
        self.assertIn("40%", msg)

    def test_contains_dates(self):
        gap = SAMPLE_RENT_GAPS["rentGaps"][0]
        msg = build_rent_gap_message(gap, SAMPLE_MASTER_DATA)
        self.assertIn("21.04.", msg)
        self.assertIn("30.04.", msg)

    def test_contains_included_kms(self):
        gap = SAMPLE_RENT_GAPS["rentGaps"][0]
        msg = build_rent_gap_message(gap, SAMPLE_MASTER_DATA)
        self.assertTrue("1.300" in msg or "1300" in msg)

    def test_contains_booking_link(self):
        gap = SAMPLE_RENT_GAPS["rentGaps"][0]
        msg = build_rent_gap_message(gap, SAMPLE_MASTER_DATA)
        self.assertIn("nextmove.de", msg)

    def test_unknown_model_shows_fallback(self):
        gap = SAMPLE_RENT_GAPS["rentGaps"][0].copy()
        gap["modelId"] = "unknown-model-id"
        gap["modelVariantId"] = "unknown-variant"
        msg = build_rent_gap_message(gap, SAMPLE_MASTER_DATA)
        # Should not crash, should show something reasonable
        self.assertIsInstance(msg, str)
        self.assertIn("Solingen", msg)


class TestBuildTestdriveMessage(unittest.TestCase):
    def test_contains_city(self):
        entry = {"city": "Berlin", "text": "VW. ID4 (503) nach Arnstadt, ab dem 27.04., 2 Tage 500 km frei"}
        msg = build_testdrive_message(entry)
        self.assertIn("Berlin", msg)

    def test_contains_vehicle_text(self):
        entry = {"city": "Berlin", "text": "VW. ID4 (503) nach Arnstadt, ab dem 27.04., 2 Tage 500 km frei"}
        msg = build_testdrive_message(entry)
        self.assertIn("VW. ID4 (503)", msg)

    def test_contains_link(self):
        entry = {"city": "Berlin", "text": "some text"}
        msg = build_testdrive_message(entry)
        self.assertIn("nextmove.de", msg)


# ---------------------------------------------------------------------------
# Tests: Telegram sending (mocked)
# ---------------------------------------------------------------------------

class TestSendTelegramMessage(unittest.TestCase):
    @patch("nextmove_notifier._session")
    def test_calls_telegram_api(self, mock_session):
        mock_resp = MagicMock(status_code=200, json=lambda: {"ok": True})
        mock_session.return_value.post.return_value = mock_resp
        send_telegram_message("Hello", bot_token="TOKEN", chat_id="12345")
        mock_session.return_value.post.assert_called_once()
        call_url = mock_session.return_value.post.call_args[0][0]
        self.assertIn("TOKEN", call_url)
        self.assertIn("sendMessage", call_url)

    @patch("nextmove_notifier._session")
    def test_sends_correct_payload(self, mock_session):
        mock_resp = MagicMock(status_code=200, json=lambda: {"ok": True})
        mock_session.return_value.post.return_value = mock_resp
        send_telegram_message("Test msg", bot_token="TOK", chat_id="999")
        payload = mock_session.return_value.post.call_args[1]["json"]
        self.assertEqual(payload["chat_id"], "999")
        self.assertEqual(payload["text"], "Test msg")

    @patch("nextmove_notifier._session")
    def test_handles_api_error_gracefully(self, mock_session):
        mock_resp = MagicMock(status_code=400, text="Bad Request")
        mock_session.return_value.post.return_value = mock_resp
        # Should not raise
        send_telegram_message("Test", bot_token="TOK", chat_id="999")


# ---------------------------------------------------------------------------
# Tests: API client (mocked HTTP)
# ---------------------------------------------------------------------------

class TestFetchSessionToken(unittest.TestCase):
    @patch("nextmove_notifier._session")
    def test_returns_token(self, mock_session):
        mock_resp = MagicMock(status_code=200)
        mock_resp.json.return_value = SAMPLE_SESSION_RESPONSE
        mock_resp.raise_for_status = MagicMock()
        mock_session.return_value.post.return_value = mock_resp
        token = fetch_session_token()
        self.assertEqual(token, "abc123tokenxyz")

    @patch("nextmove_notifier._session")
    def test_returns_none_on_error(self, mock_session):
        mock_session.return_value.post.side_effect = Exception("Connection error")
        token = fetch_session_token()
        self.assertIsNone(token)


class TestFetchRentGaps(unittest.TestCase):
    @patch("nextmove_notifier._session")
    def test_returns_gaps_list(self, mock_session):
        mock_resp = MagicMock(status_code=200)
        mock_resp.json.return_value = SAMPLE_RENT_GAPS
        mock_resp.raise_for_status = MagicMock()
        mock_session.return_value.get.return_value = mock_resp
        gaps = fetch_rent_gaps("sometoken")
        self.assertEqual(len(gaps), 2)

    @patch("nextmove_notifier._session")
    def test_returns_empty_on_error(self, mock_session):
        mock_session.return_value.get.side_effect = Exception("timeout")
        gaps = fetch_rent_gaps("sometoken")
        self.assertEqual(gaps, [])


class TestFetchMasterData(unittest.TestCase):
    @patch("nextmove_notifier._session")
    def test_returns_master_data(self, mock_session):
        mock_resp = MagicMock(status_code=200)
        mock_resp.json.return_value = SAMPLE_MASTER_DATA
        mock_resp.raise_for_status = MagicMock()
        mock_session.return_value.get.return_value = mock_resp
        data = fetch_master_data("sometoken")
        self.assertIn("models", data)
        self.assertIn("sites", data)

    @patch("nextmove_notifier._session")
    def test_returns_empty_on_error(self, mock_session):
        mock_session.return_value.get.side_effect = Exception("fail")
        data = fetch_master_data("sometoken")
        self.assertEqual(data, {})


# ---------------------------------------------------------------------------
# Tests: Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases(unittest.TestCase):
    def test_rent_gap_with_missing_fields(self):
        """Gaps with missing optional fields shouldn't crash."""
        gap = {
            "startDate": "2026-05-01",
            "endDate": "2026-05-05",
            "bookingDays": 5,
            "siteId": "unknown",
            "siteName": "Nowhere",
            "vehicleId": "v999",
            "modelId": "unknown",
            "modelVariantId": "unknown",
            "rentPrice": 100.0,
            "includedKms": 500,
            "discountPercentage": 20,
        }
        msg = build_rent_gap_message(gap, {"models": [], "sites": []})
        self.assertIsInstance(msg, str)
        self.assertIn("100", msg)

    def test_testdrive_html_with_nested_spans(self):
        """Real-world HTML has nested spans with styles."""
        html = """
        <ul><li>
        <h3><span style="color: #99cc00;">Stuttgart</span></h3>
        <ul>
        <li><span style="color: #000000;"><b>Maxus eDeliver3 (24), ab sofort, nach Leipzig, 3 Tage 700 km frei</b></span></li>
        </ul>
        </li></ul>
        """
        result = parse_testdrives_html(html)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["city"], "Stuttgart")
        self.assertIn("Maxus", result[0]["text"])

    def test_testdrive_html_with_solingen_structure(self):
        """Solingen has a weird nested structure in the real HTML."""
        html = """
        <ul>
        <li>
        <h3><span style="color: #99cc00;">Solingen</span></h3>
        </li>
        </ul>
        <ul>
        <li style="list-style-type: none;">
        <ul>
        <li><span style="color: #000000;"><strong>Maxus eDeliver3 (13) nach Leipzig, ab sofort</strong></span></li>
        </ul>
        </li>
        </ul>
        """
        result = parse_testdrives_html(html)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["city"], "Solingen")
        self.assertIn("Maxus", result[0]["text"])

    def test_keine_city_gets_no_false_positives(self):
        """A 'keine' city in one <ul> must not steal offers from a sibling <ul>."""
        html = """
        <ul>
        <li>
        <h3><span>Arnstadt</span></h3>
        <ul><li><b>keine</b></li></ul>
        </li>
        </ul>
        <ul>
        <li>
        <h3><span>Sinsheim</span></h3>
        <ul><li><strong>VW. ID4 (509) nach Arnstadt, ab dem 22.04., 2 Tage 600 km frei</strong></li></ul>
        </li>
        </ul>
        """
        result = parse_testdrives_html(html)
        cities = [r["city"] for r in result]
        self.assertNotIn("Arnstadt", cities)
        self.assertIn("Sinsheim", cities)
        self.assertEqual(len(result), 1)

    def test_solingen_no_duplicate(self):
        """Solingen's orphaned offer must appear exactly once, not twice."""
        html = """
        <ul>
        <li>
        <h3><span style="color: #99cc00;">Solingen</span></h3>
        </li>
        </ul>
        <ul>
        <li style="list-style-type: none;">
        <ul>
        <li><strong>Maxus eDeliver3 (13, 53, 54) nach Leipzig, ab sofort, 3 Tage 700 km frei</strong></li>
        </ul>
        </li>
        </ul>
        """
        result = parse_testdrives_html(html)
        solingen = [r for r in result if r["city"] == "Solingen"]
        self.assertEqual(len(solingen), 1)


if __name__ == "__main__":
    unittest.main()