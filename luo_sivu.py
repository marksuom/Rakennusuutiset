import feedparser
from datetime import datetime

# Rakennusalan RSS-syötteet
SYOTTEET = [
    {
        "nimi": "Rakennuslehti",
        "url": "https://www.rakennuslehti.fi/feed/"
    },
    {
        "nimi": "Yle Uutiset - Talous",
        "url": "https://feeds.yle.fi/uutiset/v1/recent.rss?publisherIds=YLE_UUTISET&concepts=18-34837"
    }
]

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
        kortit += f"""
    <div class="uutiskortti">
      <h2>{u['otsikko']}</h2>
      <p>{u['yhteenveto'][:200] + '...' if len(u['yhteenveto']) > 200 else u['yhteenveto']}</p>
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

    print(f"Valmis! Löydettiin {len(uutiset)} uutista.")
    print(f"Päivitetty: {paivitysaika}")

if __name__ == "__main__":
    uutiset = hae_uutiset()
    luo_html(uutiset)