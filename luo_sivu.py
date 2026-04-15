import feedparser
import requests
import os
import re
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("PERPLEXITY_API_KEY")

SYOTTEET = [
    {"nimi": "Rakennuslehti", "url": "https://www.rakennuslehti.fi/feed/"},
    {"nimi": "Kauppalehti — Rakentaminen", "url": "https://feeds.kauppalehti.fi/rss/topic/rakentaminen"},
    {"nimi": "Kauppalehti — Suhdanteet", "url": "https://feeds.kauppalehti.fi/rss/topic/suhdanteet"},
    {"nimi": "Kauppalehti — Toimitilat", "url": "https://feeds.kauppalehti.fi/rss/topic/toimitilat"},
    {"nimi": "Yle — Tampere", "url": "https://feeds.yle.fi/uutiset/v1/recent.rss?publisherIds=YLE_TAMPERE"},
    {"nimi": "Yle — Turku", "url": "https://feeds.yle.fi/uutiset/v1/recent.rss?publisherIds=YLE_TURKU"},
    {"nimi": "Yle — Oulu", "url": "https://feeds.yle.fi/uutiset/v1/recent.rss?publisherIds=YLE_OULU"},
    {"nimi": "Yle — Jyväskylä", "url": "https://feeds.yle.fi/uutiset/v1/recent.rss?publisherIds=YLE_KESKI_SUOMI"},
    {"nimi": "Yle — Kuopio", "url": "https://feeds.yle.fi/uutiset/v1/recent.rss?publisherIds=YLE_KUOPIO"},
    {"nimi": "Yle Uutiset — Talous", "url": "https://feeds.yle.fi/uutiset/v1/recent.rss?publisherIds=YLE_UUTISET&concepts=18-34837"},
    {"nimi": "Keskisuomalainen", "url": "https://www.ksml.fi/feed/rss"},
    {"nimi": "Kaleva", "url": "https://www.kaleva.fi/rss/kaikki"},
]

def on_relevantti(otsikko, teksti):
    try:
        vastaus = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "sonar",
                "messages": [
                    {
                        "role": "system",
                        "content": "Olet rakennustuotetoimittajan assistentti. Tehtäväsi on arvioida onko uutinen relevantti rakennustuotetoimittajalle. Relevantteja aiheita ovat: uudet rakennushankkeet, rakentamisen suhdanteet, toimitilat, infrastruktuuri, kaavoitus, rakennusluvat, kiinteistömarkkina, rakennusmateriaalit ja -tuotteet, alan yritykset. Vastaa AINOASTAAN sanalla KYLLÄ tai EI."
                    },
                    {
                        "role": "user",
                        "content": f"Otsikko: {otsikko}\nSisältö: {teksti[:300]}"
                    }
                ],
                "max_tokens": 5
            }
        )
        vastaus.raise_for_status()
        tulos = vastaus.json()["choices"][0]["message"]["content"].strip().upper()
        return "KYLLÄ" in tulos
    except Exception as e:
        print(f"Relevanssivirhe: {e}")
        return True

def tee_yhteenveto(otsikko, teksti):
    try:
        vastaus = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "sonar",
                "messages": [
                    {
                        "role": "system",
                        "content": "Olet rakennusalan uutistoimittaja. Tee lyhyt ja selkeä 2-3 lauseen yhteenveto suomeksi annetusta uutisesta rakennustuotetoimittajan näkökulmasta. Korosta erityisesti hankkeiden kokoluokkaa, sijaintia ja aikataulua jos ne mainitaan. Älä lisää omia mielipiteitä. Älä käytä viittausnumeroita tai hakasulkuja tekstissä."
                    },
                    {
                        "role": "user",
                        "content": f"Otsikko: {otsikko}\n\nSisältö: {teksti}"
                    }
                ],
                "max_tokens": 250
            }
        )
        vastaus.raise_for_status()
        tulos = vastaus.json()["choices"][0]["message"]["content"]
        tulos = re.sub(r'\[\d+\]', '', tulos).strip()
        return tulos
    except Exception as e:
        print(f"API-virhe: {e}")
        return teksti[:200] + "..." if len(teksti) > 200 else teksti

def hae_uutiset():
    kaikki_uutiset = []
    for syote in SYOTTEET:
        print(f"Haetaan: {syote['nimi']}...")
        feed = feedparser.parse(syote["url"])
        for artikkeli in feed.entries[:5]:
            uutinen = {
                "otsikko": artikkeli.get("title", "Ei otsikkoa"),
                "linkki": artikkeli.get("link", "#"),
                "yhteenveto": artikkeli.get("summary", ""),
                "lahde": syote["nimi"]
            }
            kaikki_uutiset.append(uutinen)

    import json
    with open("uutiset_cache.json", "w", encoding="utf-8") as f:
        json.dump(kaikki_uutiset, f, ensure_ascii=False, indent=2)

    return kaikki_uutiset

def luo_html(uutiset):
    suomi = timezone(timedelta(hours=3))
    paivitysaika = datetime.now(suomi).strftime("%d.%m.%Y %H:%M")
    kortit = ""
    relevantit = 0

    for u in uutiset:
        print(f"Tarkistetaan relevanssi: {u['otsikko'][:50]}...")

        if not on_relevantti(u["otsikko"], u["yhteenveto"]):
            print(f"  → Hylätty")
            continue

        print(f"  → Relevantti! Tehdään yhteenveto...")
        yhteenveto = tee_yhteenveto(u["otsikko"], u["yhteenveto"])
        relevantit += 1

        kortit += f"""
    <div class="uutiskortti">
      <h2>{u['otsikko']}</h2>
      <p>{yhteenveto}</p>
      <div class="lahde-rivi">
        <span class="lahde-teksti">Lähde: {u['lahde']}</span>
        <a class="lue-lisaa"
           href="{u['linkki']}"
           target="_blank"
           rel="noopener noreferrer">
          Lue alkuperäinen uutinen →
        </a>
      </div>
    </div>
"""

    html = f"""<!DOCTYPE html>
<html lang="fi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Rakennusmarkkinan uutiset</title>
  <link rel="stylesheet" href="tyyli.css">
</head>
<body>

  <header>
    <div class="header-ylaosa">
      <div>
        <h1>Rakennusmarkkinan uutiset</h1>
        <div class="alaotsikko">Automaattisesti kerätyt uutiset rakennusalalta</div>
      </div>
    </div>
    <div class="header-alapalkki">
      Päivitetty: {paivitysaika}
    </div>
  </header>

  <main>
    <div class="uutismaara">Tänään {relevantit} relevanttia uutista</div>
{kortit}
  </main>

  <footer>
    <p>Uutiset kerätty automaattisesti julkisista lähteistä.</p>
    <p>Kaikki oikeudet alkuperäisille julkaisijoille.</p>
  </footer>

</body>
</html>"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\nValmis! {relevantit} relevanttia uutista {len(uutiset)}:sta.")
    print(f"Päivitetty: {paivitysaika}")

if __name__ == "__main__":
    uutiset = hae_uutiset()
    luo_html(uutiset)