import json
from datetime import datetime

def luo_esikatselu():
    try:
        with open("uutiset_cache.json", "r", encoding="utf-8") as f:
            uutiset = json.load(f)
        print(f"Ladattu {len(uutiset)} uutista välimuistista.")
    except FileNotFoundError:
        print("Ei löydy uutiset_cache.json — aja ensin: python luo_sivu.py")
        return

    paivitysaika = datetime.now().strftime("%d.%m.%Y %H:%M")
    kortit = ""

    for u in uutiset:
        kortit += f"""
    <div class="uutiskortti">
      <h2>{u['otsikko']}</h2>
      <p>{u['yhteenveto'][:200]}...</p>
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
  <title>Rakennusmarkkinan uutiset — esikatselu</title>
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
      Esikatselu — päivitetty: {paivitysaika}
    </div>
  </header>

  <main>
    <div class="uutismaara">{len(uutiset)} uutista (esikatselu — ei tekoälysuodatusta)</div>
{kortit}
  </main>

  <footer>
    <p>Uutiset kerätty automaattisesti julkisista lähteistä.</p>
    <p>Kaikki oikeudet alkuperäisille julkaisijoille.</p>
  </footer>

</body>
</html>"""

    with open("esikatselu.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("Esikatselu valmis — avaa esikatselu.html selaimessa!")

if __name__ == "__main__":
    luo_esikatselu()