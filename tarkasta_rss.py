"""
Testaa yritysten RSS-syötteet. Aja: python tarkasta_rss.py
"""
import feedparser

yritykset = [
    # Oma syöte (WordPress /feed/ tai vastaava)          Kauppalehti yrityssivu
    ("YIT",         "https://www.yit.fi/uutiset/feed/",          "https://feeds.kauppalehti.fi/rss/company/yit"),
    ("SRV",         "https://www.srv.fi/uutiset/feed/",          "https://feeds.kauppalehti.fi/rss/company/srv-group"),
    ("Skanska",     "https://www.skanska.fi/om-skanska/nyheter/feed/", "https://feeds.kauppalehti.fi/rss/company/skanska"),
    ("NCC",         "https://www.ncc.fi/tietoa-ncc/uutiset/feed/","https://feeds.kauppalehti.fi/rss/company/ncc"),
    ("Peab",        "https://www.peab.fi/feed/",                 "https://feeds.kauppalehti.fi/rss/company/peab"),
    ("Hartela",     "https://www.hartela.fi/feed/",              "https://feeds.kauppalehti.fi/rss/company/hartela"),
    ("Lehto Group", "https://www.lehto.fi/feed/",               "https://feeds.kauppalehti.fi/rss/company/lehto-group"),
    ("Lapti",       "https://www.lapti.fi/feed/",               "https://feeds.kauppalehti.fi/rss/company/lapti"),
    ("Are",         "https://www.are.fi/feed/",                 "https://feeds.kauppalehti.fi/rss/company/are"),
    ("Luja",        "https://www.luja.fi/feed/",               "https://feeds.kauppalehti.fi/rss/company/luja"),
    ("Jatke",       "https://www.jatke.fi/feed/",              "https://feeds.kauppalehti.fi/rss/company/jatke"),
    ("Fira",        "https://www.fira.fi/feed/",               "https://feeds.kauppalehti.fi/rss/company/fira"),
    ("Consti",      "https://www.consti.fi/feed/",             "https://feeds.kauppalehti.fi/rss/company/consti"),
    ("Bonava",      "https://www.bonava.fi/feed/",             "https://feeds.kauppalehti.fi/rss/company/bonava"),
    ("Destia",      "https://www.destia.fi/feed/",             "https://feeds.kauppalehti.fi/rss/company/destia"),
    ("Kreate",      "https://www.kreate.fi/feed/",             "https://feeds.kauppalehti.fi/rss/company/kreate"),
    ("Caverion",    "https://www.caverion.fi/feed/",           "https://feeds.kauppalehti.fi/rss/company/caverion"),
]

def tarkasta(url):
    feed = feedparser.parse(url)
    n = len(feed.entries)
    if n > 0:
        esimerkki = feed.entries[0].get("title", "")[:60]
        return f"✅ {n} art.  → \"{esimerkki}\""
    return "❌ tyhjä tai ei löydy"

print(f"\n{'Yritys':<14} {'Oma syöte':<55} {'Kauppalehti'}")
print("─" * 120)
for nimi, oma_url, kl_url in yritykset:
    oma = tarkasta(oma_url)
    kl  = tarkasta(kl_url)
    print(f"{nimi:<14} {oma:<55} {kl}")
print()
