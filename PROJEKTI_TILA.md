# Rakennusuutiset — projektin tila ja jatkokehitys

## Projektin kuvaus

Automaattinen uutissivusto rakennusalalle. Sivusto hakee uutiset RSS-syötteistä, tekoäly suodattaa epäolennaiset pois ja kirjoittaa relevanteista uutisista suomenkieliset yhteenvedot. Sivusto päivittyy automaattisesti joka aamu klo 7:00 Suomen aikaa.

**Käyttäjä:** Markus Suominen, työskentelee rakennustuotetoimittajalla.
**Live-osoite:** https://marksuom.github.io/Rakennusuutiset
**GitHub-repo:** https://github.com/marksuom/Rakennusuutiset

---

## Teknologiat

- **HTML & CSS** — sivuston rakenne ja ulkoasu
- **Python** — uutistenhaku ja HTML:n generointi
- **Perplexity API** — uutisten relevanssiarviointi ja yhteenvedot
- **Git & GitHub** — versionhallinta ja julkaisu
- **GitHub Actions** — automaattinen päivitys pilvessä
- **GitHub Pages** — ilmainen hosting

---

## Tiedostorakenne

```
Rakennusuutiset/
├── .env                          # Perplexity API-avain — EI GitHubissa
├── .gitignore                    # Suojaa arkaluonteiset tiedostot
├── .github/
│   └── workflows/
│       └── paivita.yml           # GitHub Actions automaatio
├── hae_uutiset.py                # Testiskripti uutisten hakuun
├── esikatselu.py                 # Nopea ulkoasun esikatselu ilman tekoälyä
├── index.html                    # Valmis sivusto — Python päivittää tämän
├── luo_sivu.py                   # Pääskripti — hakee + suodattaa + luo HTML
├── tyyli.css                     # Erillinen CSS-tiedosto
├── README.md                     # Projektin dokumentaatio
├── requirements.txt              # Python-kirjastot
├── uutiset_cache.json            # Välimuisti esikatselua varten (ei GitHubissa)
└── venv/                         # Virtuaaliympäristö (ei GitHubissa)
```

---

## Uutislähteet (luo_sivu.py — SYOTTEET-lista)

```python
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
```

---

## Tekoälyn toiminta (Perplexity API)

Malli: `sonar`
API endpoint: `https://api.perplexity.ai/chat/completions`
API-avain: tallennettu `.env`-tiedostoon muuttujana `PERPLEXITY_API_KEY`
GitHubissa: tallennettu GitHub Secrets -palveluun nimellä `PERPLEXITY_API_KEY`

**Kaksi vaihetta per uutinen:**

1. `on_relevantti()` — tarkistaa onko uutinen relevantti rakennustuotetoimittajalle (max_tokens: 5, vastaa KYLLÄ/EI)
2. `tee_yhteenveto()` — kirjoittaa 2-3 lauseen yhteenvedon suomeksi (max_tokens: 250)

**Tärkeää:** Viittausnumerot `[1][2][3]` poistetaan yhteenvedoista regex-siivouksella.

---

## GitHub Actions (paivita.yml)

- Ajastus: joka päivä klo 04:00 UTC = 07:00 Suomen aikaa
- Voidaan ajaa myös manuaalisesti GitHubissa: Actions → Run workflow
- Permissions: contents: write (tarvitaan index.html:n päivittämiseen)
- Python-versio: 3.14

---

## Ulkoasu (tyyli.css)

CSS-muuttujat joita muuttamalla vaihdetaan värimaailma:

```css
:root {
  --paavari: #1a1a2e;       /* tumma sininen — ylätunniste */
  --paavari-tumma: #111122; /* ylätunnisteen alapalkki */
  --korostus: #0066cc;      /* sininen — korttiviiva ja napit */
  --tausta: #f4f4f4;        /* sivun taustaväri */
}
```

---

## Seuraavat kehityskohteet — TÄSTÄ JATKETAAN

### 1. Historiallisten uutisten tallennus

**Tavoite:** Tallentaa päivittäiset uutiset historiaan niin että viikon uutiset ovat selattavissa.

**Suunnitelma:**
- Luodaan `historia/`-kansio projektiin
- Joka päivä uutiset tallennetaan tiedostoon `historia/YYYY-MM-DD.json`
- JSON sisältää: otsikko, yhteenveto, linkki, lähde, alue, aihepiiri
- Vanhemmat kuin 7 päivää poistetaan automaattisesti
- **Tärkeää:** Tekoäly arvioi uutiset vain kerran — ei uudelleenarvioida vanhoja

**JSON-rakenne per uutinen:**
```json
{
  "otsikko": "Destia peruskorjaa kahdeksan siltaa",
  "yhteenveto": "Tekoälyn kirjoittama yhteenveto...",
  "linkki": "https://...",
  "lahde": "Rakennuslehti",
  "alue": "Uusimaa",
  "aihepiiri": "Infrastruktuuri",
  "paiva": "2026-04-15"
}
```

### 2. Päivänavigaatio yläpalkkiin

**Tavoite:** Yläpalkissa painikkeet jokaiselle päivälle jonka uutiset on tallennettu.

**Toiminta:**
- JavaScript lataa `historia/`-kansion JSON-tiedostot
- Yläpalkissa näkyy: `15.4 | 14.4 | 13.4 | 12.4 | 11.4 | 10.4 | 9.4`
- Aktiivinen päivä korostettuna
- Klikkauksella vaihdetaan näkyvät uutiset

### 3. Filtterit

**Maantieteellinen filtteri:**
- Koko Suomi
- Pääkaupunkiseutu
- Tampere / Pirkanmaa
- Turku / Varsinais-Suomi
- Oulu / Pohjois-Suomi
- Jyväskylä / Keski-Suomi
- Kuopio / Itä-Suomi

**Aihepiiri-filtteri:**
- Kaikki
- Uudet hankkeet
- Suhdanteet
- Toimitilat & kiinteistöt
- Infrastruktuuri
- Alan yritykset

**Avainsanahaku:**
- Vapaa tekstihaku otsikoista ja yhteenvedoista

**Toteutus:** JavaScript-filtterit — uutiset ladataan kaikki kerralla, filtteröinti tapahtuu selaimessa. Tekoäly luokittelee alueen ja aihepiirin automaattisesti JSON:iin tallennuksen yhteydessä.

---

## Tietoturva-asiat

- `.env` ei ole GitHubissa — suojattu `.gitignore`:lla
- API-avain GitHubissa: Settings → Secrets → PERPLEXITY_API_KEY
- Git-sähköposti: `265981152+marksuom@users.noreply.github.com`
- Linkeissä aina `target="_blank" rel="noopener noreferrer"`
- Uutiset vain julkisista RSS-lähteistä
- Tekijänoikeus: näytetään vain otsikko + tekoälyn kirjoittama yhteenveto + linkki alkuperäiseen

---

## Hyödylliset komennot

```bash
# Aktivoi virtuaaliympäristö (aina kun aloitat)
source venv/Scripts/activate

# Päivitä uutiset ja luo uusi index.html
python luo_sivu.py

# Nopea ulkoasun esikatselu ilman tekoälyä
python esikatselu.py

# Git — tallenna muutokset
git add .
git commit -m "viesti"
git pull
git push
```

---

## Git-historia tiivistetysti

- Vaihe 1: HTML-rakenne, ulkoasu, ylä- ja alatunniste
- Vaihe 2: Python RSS-haku, virtuaaliympäristö, .gitignore
- Vaihe 3: Perplexity API, relevanssifilttteri, yhteenvedot
- Vaihe 4: GitHub Pages julkaisu, GitHub Actions automaatio
- Viimeisin: Aikavyöhyke korjattu Suomen aikaan, token-raja nostettu 250:een

