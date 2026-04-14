import feedparser
import json
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
        print(f"Haetaan uutisia: {syote['nimi']}...")

        feed = feedparser.parse(syote["url"])

        for artikkeli in feed.entries[:5]:
            uutinen = {
                "otsikko": artikkeli.get("title", "Ei otsikkoa"),
                "linkki": artikkeli.get("link", "#"),
                "yhteenveto": artikkeli.get("summary", ""),
                "lahde": syote["nimi"],
                "haettu": datetime.now().strftime("%d.%m.%Y %H:%M")
            }
            kaikki_uutiset.append(uutinen)

    return kaikki_uutiset

if __name__ == "__main__":
    uutiset = hae_uutiset()
    print(f"\nLöydettiin {len(uutiset)} uutista:")
    for u in uutiset:
        print(f"\n--- {u['lahde']} ---")
        print(f"Otsikko: {u['otsikko']}")
        print(f"Linkki:  {u['linkki']}")