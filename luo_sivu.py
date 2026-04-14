import feedparser
import requests
import os
from datetime import datetime
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
                        "content": "Olet rakennusalan uutistoimittaja. Tee lyhyt ja selkeä 2-3 lauseen yhteenveto suomeksi annetusta uutisesta rakennustuotetoimittajan näkökulmasta. Korosta erityisesti hankkeiden kokoluokkaa, sijaintia ja aikataulua jos ne mainitaan. Älä lisää omia mielipiteitä."
                    },
                    {
                        "role": "user",
                        "content": f"Otsikko: {otsikko}\n\nSisältö: {teksti}"
                    }
                ],
                "max_tokens": 150
            }
        )
        vastaus.raise_for_status()
        return vastaus.json()["choices"][0]["message"]["content"]
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
    return kaikki_uutiset

def luo_html(uutiset):
    paivitysaika = datetime.now().strftime("%d.%m.%Y %H:%M")
    kortit = ""

    for u in uutiset:
        print(f"Tarkistetaan relevanssi: {u['otsikko'][:50]}...")

        if not on_relevantti(u["otsikko"], u["yhteenveto"]):
            print(f"  → Hylätty")
            continue

        print(f"  → Relevantti! Tehdään yhteenveto...")
        yhteenveto = tee_yhteenveto(u["otsikko"], u["yhteenveto"])

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
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; }}
    header {{ background-color: #1a1a2e; color: white; padding: 24px 20px; text-align: center; }}
    header h1 {{ font-size: 26px; margin-bottom: 6px; }}
    header p {{ font-size: 14px; color: #aaa; }}
    main {{ padding: 20px; }}
    .uutiskortti {{ background-color: white; border-radius: 8px; padding: 20px; margin: 16px auto; max-width: 700px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); }}
    .uutiskortti h2 {{ color: #1a1a2e; font-size: 18px; margin-bottom: 8px; }}
    .uutiskortti p {{ color: #555; line-height: 1.6; margin-bottom: 12px; }}
    .lahde-rivi {{ display: flex; align-items: center; gap: 12px; padding-top: 12px; border-top: 1px solid #eee; flex-wrap: wrap; }}
    .lahde-teksti {{ font-size: 13px; color: #888; }}
    .lue-lisaa {{ display: inline-block; color: #0066cc; text-decoration: none; font-size: 14px; font-weight: bold; padding: 4px 10px; border: 1px solid #0066cc; border-radius: 4px; }}
    .lue-lisaa:hover {{ background-color: #0066cc; color: white; }}
    footer {{ background-color: #1a1a2e; color: #aaa; text-align: center; padding: 20px; font-size: 13px; margin-top: 40px; }}
  </style>
</head>
<body>

  <header>
    <h1>Rakennusmarkkinan uutiset</h1>
    <p>Automaattisesti kerätyt uutiset rakennusalalta — päivitetty päivittäin</p>
  </header>

  <main>
{kortit}
  </main>

  <footer>
    <p>Uutiset kerätty automaattisesti julkisista lähteistä. Kaikki oikeudet alkuperäisille julkaisijoille.</p>
    <p style="margin-top: 6px;">Viimeksi päivitetty: {paivitysaika}</p>
  </footer>

</body>
</html>"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\nValmis! {len(uutiset)} uutista käyty läpi.")
    print(f"Päivitetty: {paivitysaika}")

if __name__ == "__main__":
    uutiset = hae_uutiset()
    luo_html(uutiset)