## Bug 1: HTML scrapper false positive
Here's html block from https://nextmove.de/ueberfuehrungsfahrten/:
```html
<div class="elementor-element elementor-element-7084c8a elementor-widget elementor-widget-theme-post-content"
    data-id="7084c8a" data-element_type="widget" data-e-type="widget" data-widget_type="theme-post-content.default">
    <h1 class="wp-block-heading">Kostenlose Überführungsfahrten (Testdrives)</h1>
    <p><span class="font-555555" style="color: #000000;">Hier finden Sie kostenlose* One-Way-Mieten von nextmove für
            verschiedenste Fahrzeugmodelle. </span></p>
    <p><strong><span class="font-555555" style="color: #000000;">Bei Interesse senden Sie einfach eine </span><span
                class="font-555555" style="color: #3366ff;"><a style="color: #3366ff;" href="/anfrage/?reason=219740009"
                    target="_blank" rel="noopener">Anfrage</a></span><span class="font-555555" style="color: #000000;">
                über unser Formular.</span></strong></p>
    <ul>
        <li>
            <h3><span style="color: #99cc00;">Arnstadt</span></h3>
            <ul>
                <li><b>keine</b></li>
            </ul>
        </li>
        <li>
            <h3><span style="color: #99cc00;">Berlin</span></h3>
            <ul>
                <li><strong>VW. ID4 (503) nach Arnstadt, ab dem 27.04., 2 Tage 500 km frei</strong></li>
                <li><strong>VW. ID4 (507) nach Arnstadt, ab dem 24.04., 2 Tage 500 km frei</strong></li>
                <li><strong>Maxus eDeliver9 (187) 72kWh nach Leipzig, ab sofort, 2 Tage 400 km frei</strong></li>
            </ul>
        </li>
        <li>
            <h3><span style="color: #99cc00;">Düsseldorf</span></h3>
            <ul>
                <li><b>keine</b></li>
            </ul>
        </li>
        <li>
            <h3><span style="color: #99cc00;">Leipzig</span></h3>
            <ul>
                <li><strong>VW. ID4 (508) nach Arnstadt, ab dem 04.05., 2 Tage 400 km frei</strong></li>
            </ul>
        </li>
        <li>
            <h3><span style="color: #99cc00;">München</span></h3>
            <ul>
                <li><strong>VW. ID4 (504) nach Arnstadt, ab dem 21.04., 2 Tage 700 km frei</strong></li>
            </ul>
        </li>
        <li>
            <h3><span style="color: #99cc00;">Hamburg</span></h3>
            <ul>
                <li><span style="color: #000000;"><strong>Ford eTransit (105, 177) nach Leipzig, ab sofort, 3 Tage 700
                            km frei,&nbsp;Ladepauschale entfällt</strong></span></li>
                <li><strong>Tesla Model Y (453) nach Leipzig, ab sofort, 2 Tage 700 km frei</strong></li>
            </ul>
        </li>
        <li>
            <h3><span style="color: #99cc00;">Frankfurt am Main</span><strong
                    style="color: #000000; font-size: 16px;">&nbsp;</strong></h3>
            <ul>
                <li><strong>VW. ID4 (506) nach Arnstadt, ab dem 22.04., 2 Tage 500 km frei</strong></li>
                <li><strong>VW. ID7 Tourer 79 kWh (638) nach Stuttgart, 18.05. -21.05., 2 Tage 400 km frei</strong></li>
                <li><span style="color: #000000;"><strong>Mercedes EQE 300, nach Leipzig, 17.04. -23.04., 2 Tage 600 km
                            frei</strong></span></li>
            </ul>
        </li>
        <li>
            <h3><span style="color: #99cc00;">Nürnberg</span></h3>
            <ul>
                <li><span style="color: #000000;"><b>keine</b></span></li>
            </ul>
        </li>
    </ul>
    <ul>
        <li>
            <h3><span style="color: #99cc00;">Sinsheim</span></h3>
            <ul>
                <li><strong>VW. ID4 (509) nach Arnstadt, ab dem 22.04., 2 Tage 600 km frei</strong></li>
            </ul>
        </li>
        <li>
            <h3><span style="color: #99cc00;">Solingen</span></h3>
        </li>
    </ul>
    <ul>
        <li style="list-style-type: none;">
            <ul>
                <li><span style="color: #000000;"><strong>Maxus eDeliver3 (13, 53, 54) nach Leipzig, ab sofort, 3 Tage
                            700 km frei, Ladepauschale entfällt</strong></span></li>
            </ul>
        </li>
    </ul>
    <ul>
        <li>
            <h3><span style="color: #99cc00;">Stuttgart</span></h3>
            <ul>
                <li><span style="color: #000000;"><b>Maxus eDeliver3 (24), ab sofort, nach Leipzig, 3 Tage 700 km
                            frei</b></span></li>
            </ul>
        </li>
    </ul>
    <p><span style="color: #000000;"><strong>Die allgemeinen Test Drives im Detail:</strong></span></p>
    <ul>
        <li><span style="color: #000000;">Angegebener Mietzeitraum und Kilometeranzahl kostenfrei.</span></li>
        <li><span style="color: #000000;">Die Preise für gefahrene Mehrkilometer sind den individuellen Fahrzeugseiten
                zu entnehmen.</span></li>
        <li><span style="color: #000000;">Wenn kein genaues Datum ausgeschrieben wurde, muss der Test Drive innerhalb
                von einer Woche wahrgenommen werden.</span></li>
        <li><span style="color: #000000;">Jeder Test Drive beinhaltet eine Selbstbeteiligung (Kaution) des Anmietenden
                im Falle eines Schadens. Diese sind den individuellen Fahrzeugseiten zu entnehmen.</span></li>
        <li><span style="color: #000000;">alle Test Drives zzgl. einer einmaligen Ladepauschale. Ladepauschale &amp;
            </span><span style="color: #000000;">Zusatzleistungen sind dem <a style="color: #000000;"
                    href="https://nextmove.de/preis-und-leistungsverzeichnis/" target="_blank"
                    rel="noopener">Preis-/Leistungsverzeichnis</a> zu entnehmen.</span></li>
        <li><span style="color: #000000;">Social Media Posts bei kostenlosen Test Drives auf Facebook, Twitter,
                Instagram oder YouTube mit nextmove-Tag sind willkommen.</span></li>
        <li><span style="color: #000000;">Die Fahrzeuge beinhalten zum Teil einen weiteren Satz Räder, die
                mitzutransportieren sind.</span></li>
        <li><span style="color: #000000;">Es gelten die nextmove <a style="color: #000000;"
                    href="https://nextmove.de/agb/" target="_blank" rel="noopener">AGB</a>.</span></li>
    </ul>
</div>
```

What I see with my eyes:
- Arnstadt
    - keine
- Berlin
    - VW. ID4 (503) nach Arnstadt, ab dem 27.04., 2 Tage 500 km frei
    - VW. ID4 (507) nach Arnstadt, ab dem 24.04., 2 Tage 500 km frei
    - Maxus eDeliver9 (187) 72kWh nach Leipzig, ab sofort, 2 Tage 400 km frei
- Düsseldorf
    - keine
- Leipzig
    - VW. ID4 (508) nach Arnstadt, ab dem 04.05., 2 Tage 400 km frei
- München
    - VW. ID4 (504) nach Arnstadt, ab dem 21.04., 2 Tage 700 km frei
- Hamburg
    - Ford eTransit (105, 177) nach Leipzig, ab sofort, 3 Tage 700 km frei, Ladepauschale entfällt
    - Tesla Model Y (453) nach Leipzig, ab sofort, 2 Tage 700 km frei
- Frankfurt am Main 
    - VW. ID4 (506) nach Arnstadt, ab dem 22.04., 2 Tage 500 km frei
    - VW. ID7 Tourer 79 kWh (638) nach Stuttgart, 18.05. -21.05., 2 Tage 400 km frei
    - Mercedes EQE 300, nach Leipzig, 17.04. -23.04., 2 Tage 600 km frei
- Nürnberg
    - keine
- Sinsheim
    - VW. ID4 (509) nach Arnstadt, ab dem 22.04., 2 Tage 600 km frei
- Solingen
    - Maxus eDeliver3 (13, 53, 54) nach Leipzig, ab sofort, 3 Tage 700 km frei, Ladepauschale entfällt
- Stuttgart
    - Maxus eDeliver3 (24), ab sofort, nach Leipzig, 3 Tage 700 km frei

What I got on first app run
 from telegram bot:

```telegram
Jetzt buchen → (https://nextmove.de/aktionen/)
[17.04.2026 17:30] Nextmove Notifier: 🆓 Neue Überführungsfahrt!
📍 Arnstadt
SinsheimVW. ID4 (509) nach Arnstadt, ab dem 22.04., 2 Tage 600 km frei
Anfrage senden → (https://nextmove.de/anfrage/?reason=219740009)
[17.04.2026 17:30] Nextmove Notifier: 🆓 Neue Überführungsfahrt!
📍 Arnstadt
VW. ID4 (509) nach Arnstadt, ab dem 22.04., 2 Tage 600 km frei
Anfrage senden → (https://nextmove.de/anfrage/?reason=219740009)
[17.04.2026 17:30] Nextmove Notifier: 🆓 Neue Überführungsfahrt!
📍 Arnstadt
Solingen
Anfrage senden → (https://nextmove.de/anfrage/?reason=219740009)
[17.04.2026 17:30] Nextmove Notifier: 🆓 Neue Überführungsfahrt!
📍 Berlin
VW. ID4 (503) nach Arnstadt, ab dem 27.04., 2 Tage 500 km frei
Anfrage senden → (https://nextmove.de/anfrage/?reason=219740009)
[17.04.2026 17:30] Nextmove Notifier: 🆓 Neue Überführungsfahrt!
📍 Berlin
VW. ID4 (507) nach Arnstadt, ab dem 24.04., 2 Tage 500 km frei
Anfrage senden → (https://nextmove.de/anfrage/?reason=219740009)
[17.04.2026 17:30] Nextmove Notifier: 🆓 Neue Überführungsfahrt!
📍 Berlin
Maxus eDeliver9 (187) 72kWh nach Leipzig, ab sofort, 2 Tage 400 km frei
Anfrage senden → (https://nextmove.de/anfrage/?reason=219740009)
[17.04.2026 17:30] Nextmove Notifier: 🆓 Neue Überführungsfahrt!
📍 Düsseldorf
SinsheimVW. ID4 (509) nach Arnstadt, ab dem 22.04., 2 Tage 600 km frei
Anfrage senden → (https://nextmove.de/anfrage/?reason=219740009)
[17.04.2026 17:30] Nextmove Notifier: 🆓 Neue Überführungsfahrt!
📍 Düsseldorf
VW. ID4 (509) nach Arnstadt, ab dem 22.04., 2 Tage 600 km frei
Anfrage senden → (https://nextmove.de/anfrage/?reason=219740009)
[17.04.2026 17:30] Nextmove Notifier: 🆓 Neue Überführungsfahrt!
📍 Düsseldorf
Solingen
Anfrage senden → (https://nextmove.de/anfrage/?reason=219740009)
[17.04.2026 17:30] Nextmove Notifier: 🆓 Neue Überführungsfahrt!
📍 Leipzig
VW. ID4 (508) nach Arnstadt, ab dem 04.05., 2 Tage 400 km frei
Anfrage senden → (https://nextmove.de/anfrage/?reason=219740009)
[17.04.2026 17:30] Nextmove Notifier: 🆓 Neue Überführungsfahrt!
📍 München
VW. ID4 (504) nach Arnstadt, ab dem 21.04., 2 Tage 700 km frei
Anfrage senden → (https://nextmove.de/anfrage/?reason=219740009)
[17.04.2026 17:30] Nextmove Notifier: 🆓 Neue Überführungsfahrt!
📍 Hamburg
Ford eTransit (105, 177) nach Leipzig, ab sofort, 3 Tage 700 km frei, Ladepauschale entfällt
Anfrage senden → (https://nextmove.de/anfrage/?reason=219740009)
[17.04.2026 17:30] Nextmove Notifier: 🆓 Neue Überführungsfahrt!
📍 Hamburg
Tesla Model Y (453) nach Leipzig, ab sofort, 2 Tage 700 km frei
Anfrage senden → (https://nextmove.de/anfrage/?reason=219740009)
[17.04.2026 17:30] Nextmove Notifier: 🆓 Neue Überführungsfahrt!
📍 Frankfurt am Main
VW. ID4 (506) nach Arnstadt, ab dem 22.04., 2 Tage 500 km frei
Anfrage senden → (https://nextmove.de/anfrage/?reason=219740009)
[17.04.2026 17:30] Nextmove Notifier: 🆓 Neue Überführungsfahrt!
📍 Frankfurt am Main
VW. ID7 Tourer 79 kWh (638) nach Stuttgart, 18.05. -21.05., 2 Tage 400 km frei
Anfrage senden → (https://nextmove.de/anfrage/?reason=219740009)
[17.04.2026 17:30] Nextmove Notifier: 🆓 Neue Überführungsfahrt!
📍 Frankfurt am Main
Mercedes EQE 300, nach Leipzig, 17.04. -23.04., 2 Tage 600 km frei
Anfrage senden → (https://nextmove.de/anfrage/?reason=219740009)
[17.04.2026 17:30] Nextmove Notifier: 🆓 Neue Überführungsfahrt!
📍 Nürnberg
SinsheimVW. ID4 (509) nach Arnstadt, ab dem 22.04., 2 Tage 600 km frei
Anfrage senden → (https://nextmove.de/anfrage/?reason=219740009)
[17.04.2026 17:30] Nextmove Notifier: 🆓 Neue Überführungsfahrt!
📍 Nürnberg
VW. ID4 (509) nach Arnstadt, ab dem 22.04., 2 Tage 600 km frei
Anfrage senden → (https://nextmove.de/anfrage/?reason=219740009)
[17.04.2026 17:30] Nextmove Notifier: 🆓 Neue Überführungsfahrt!
📍 Nürnberg
Solingen
Anfrage senden → (https://nextmove.de/anfrage/?reason=219740009)
[17.04.2026 17:30] Nextmove Notifier: 🆓 Neue Überführungsfahrt!
📍 Sinsheim
VW. ID4 (509) nach Arnstadt, ab dem 22.04., 2 Tage 600 km frei
Anfrage senden → (https://nextmove.de/anfrage/?reason=219740009)
[17.04.2026 17:30] Nextmove Notifier: 🆓 Neue Überführungsfahrt!
📍 Solingen
Maxus eDeliver3 (13, 53, 54) nach Leipzig, ab sofort, 3 Tage 700 km frei, Ladepauschale entfällt
Anfrage senden → (https://nextmove.de/anfrage/?reason=219740009)
[17.04.2026 17:30] Nextmove Notifier: 🆓 Neue Überführungsfahrt!
📍 Solingen
Maxus eDeliver3 (13, 53, 54) nach Leipzig, ab sofort, 3 Tage 700 km frei, Ladepauschale entfällt
Anfrage senden → (https://nextmove.de/anfrage/?reason=219740009)
[17.04.2026 17:30] Nextmove Notifier: 🆓 Neue Überführungsfahrt!
📍 Stuttgart
Maxus eDeliver3 (24), ab sofort, nach Leipzig, 3 Tage 700 km frei
Anfrage senden → (https://nextmove.de/anfrage/?reason=219740009)
```

As we can see: many false alarms!

## Bug 2: cronjob don't work!
On my linux server I executed `bash install.sh `:
```console
=== nextmove-notifier installer ===
[sudo] password for mike: 
Defaulting to user installation because normal site-packages is not writeable
Requirement already satisfied: requests>=2.28 in /usr/lib/python3/dist-packages (from -r /opt/nextmove-notifier/requirements.txt (line 1)) (2.28.1)
Collecting beautifulsoup4>=4.12
  Downloading beautifulsoup4-4.14.3-py3-none-any.whl (107 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 107.7/107.7 kB 2.6 MB/s eta 0:00:00
Collecting soupsieve>=1.6.1
  Downloading soupsieve-2.8.3-py3-none-any.whl (37 kB)
Requirement already satisfied: typing-extensions>=4.0.0 in /usr/lib/python3/dist-packages (from beautifulsoup4>=4.12->-r /opt/nextmove-notifier/requirements.txt (line 2)) (4.4.0)
Installing collected packages: soupsieve, beautifulsoup4
Successfully installed beautifulsoup4-4.14.3 soupsieve-2.8.3

⚠️  Edit /opt/nextmove-notifier/.env with your Telegram credentials!
   nano /opt/nextmove-notifier/.env

✅ Installed to /opt/nextmove-notifier
✅ Cron job set: every 15 minutes

Next steps:
  1. Edit /opt/nextmove-notifier/.env with your Telegram bot token and chat ID
  2. Test manually: /opt/nextmove-notifier/run.sh
  3. Check logs: tail -f /var/log/nextmove-notifier.log

To get your Telegram chat ID:
  1. Message your bot on Telegram
  2. Visit: https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
  3. Find your chat ID in the response
```

Then I've edited **/opt/nextmove-notifier/.env** with my Telegram credentials!
I tested **/opt/nextmove-notifier/run.sh** manually and it worked, I got messages from telegram.
But when I've executed `tail -f /var/log/nextmove-notifier.log` after an hour I got ... nothing!
```console
tail: cannot open '/var/log/nextmove-notifier.log' for reading: No such file or directory
tail: no files remaining
```

And `crontab -l` also returns nothing! Why?