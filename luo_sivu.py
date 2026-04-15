import feedparser
import requests
import os
import re
import json
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
    # Yritysten omat syötteet
    {"nimi": "Lehto Group", "url": "https://www.lehto.fi/feed/"},
    {"nimi": "Lapti", "url": "https://www.lapti.fi/feed/"},
    {"nimi": "Luja", "url": "https://www.luja.fi/feed/"},
    {"nimi": "Jatke", "url": "https://www.jatke.fi/feed/"},
    {"nimi": "Fira", "url": "https://www.fira.fi/feed/"},
    {"nimi": "Kreate", "url": "https://www.kreate.fi/feed/"},
]

ALUEET = [
    "Pääkaupunkiseutu",
    "Tampere / Pirkanmaa",
    "Turku / Varsinais-Suomi",
    "Oulu / Pohjois-Suomi",
    "Jyväskylä / Keski-Suomi",
    "Kuopio / Itä-Suomi",
    "Koko Suomi",
]

AIHEPIIRIT = [
    "Uudet hankkeet",
    "Suhdanteet",
    "Toimitilat & kiinteistöt",
    "Infrastruktuuri",
    "Alan yritykset",
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
                        "content": (
                            "Olet rakennustuotetoimittajan assistentti. Tehtäväsi on arvioida onko uutinen "
                            "relevantti rakennustuotetoimittajalle. Relevantteja aiheita ovat: uudet "
                            "rakennushankkeet, rakentamisen suhdanteet, toimitilat, infrastruktuuri, "
                            "kaavoitus, rakennusluvat, kiinteistömarkkina, rakennusmateriaalit ja -tuotteet, "
                            "alan yritykset. Erityisen relevantteja ovat uutiset jotka koskevat seuraavia "
                            "rakennusalan yrityksiä: YIT, SRV, Skanska, NCC, Peab, Hartela, Lehto Group, "
                            "Lapti, Are, Luja, Jatke, Fira, Consti, Bonava, Destia, Kreate, Caverion. "
                            "Vastaa AINOASTAAN sanalla KYLLÄ tai EI."
                        )
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


def analysoi_uutinen(otsikko, teksti):
    """Palauttaa yhteenvedon + alueen + aihepiirin yhdessä API-kutsussa."""
    alueet_str = " / ".join(ALUEET)
    aihepiirit_str = " / ".join(AIHEPIIRIT)
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
                        "content": (
                            "Olet rakennusalan uutistoimittaja. Analysoi uutinen ja palauta AINOASTAAN "
                            "JSON-objekti ilman muuta tekstiä, muodossa:\n"
                            '{"yhteenveto": "...", "alue": "...", "aihepiiri": "..."}\n\n'
                            "Ohjeet:\n"
                            "- yhteenveto: 2-3 lausetta suomeksi rakennustuotetoimittajan näkökulmasta. "
                            "Korosta hankkeiden kokoluokkaa, sijaintia ja aikataulua. Älä käytä viittausnumeroita.\n"
                            f"- alue: valitse YKSI seuraavista: {alueet_str}\n"
                            f"- aihepiiri: valitse YKSI seuraavista: {aihepiirit_str}"
                        )
                    },
                    {
                        "role": "user",
                        "content": f"Otsikko: {otsikko}\n\nSisältö: {teksti[:500]}"
                    }
                ],
                "max_tokens": 350
            }
        )
        vastaus.raise_for_status()
        sisalto = vastaus.json()["choices"][0]["message"]["content"].strip()

        # Poistetaan mahdolliset markdown-koodiblokki-tagit
        sisalto = re.sub(r"^```json\s*", "", sisalto)
        sisalto = re.sub(r"\s*```$", "", sisalto)
        # Poistetaan viittausnumerot
        sisalto = re.sub(r'\[\d+\]', '', sisalto)

        tulos = json.loads(sisalto)

        # Varmistetaan että arvot ovat sallituista listoista
        if tulos.get("alue") not in ALUEET:
            tulos["alue"] = "Koko Suomi"
        if tulos.get("aihepiiri") not in AIHEPIIRIT:
            tulos["aihepiiri"] = "Alan yritykset"

        return tulos

    except Exception as e:
        print(f"Analyysivirhe: {e}")
        return {
            "yhteenveto": (teksti[:200] + "...") if len(teksti) > 200 else teksti,
            "alue": "Koko Suomi",
            "aihepiiri": "Alan yritykset"
        }


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

    with open("uutiset_cache.json", "w", encoding="utf-8") as f:
        json.dump(kaikki_uutiset, f, ensure_ascii=False, indent=2)

    return kaikki_uutiset


def tallenna_historia(analysoidut, paiva_str):
    """Tallentaa analysoidut uutiset historia-kansioon ja siivoaa yli 7 vrk vanhat."""
    os.makedirs("historia", exist_ok=True)

    tiedosto = f"historia/{paiva_str}.json"
    with open(tiedosto, "w", encoding="utf-8") as f:
        json.dump(analysoidut, f, ensure_ascii=False, indent=2)
    print(f"Tallennettu {len(analysoidut)} uutista tiedostoon {tiedosto}")

    # Poistetaan yli 7 päivää vanhat tiedostot
    raja = datetime.now() - timedelta(days=7)
    for tiedostonimi in os.listdir("historia"):
        if not tiedostonimi.endswith(".json"):
            continue
        try:
            pvm = datetime.strptime(tiedostonimi.replace(".json", ""), "%Y-%m-%d")
            if pvm < raja:
                os.remove(f"historia/{tiedostonimi}")
                print(f"Poistettu vanha tiedosto: {tiedostonimi}")
        except ValueError:
            pass


def hae_saatavilla_olevat_paivat():
    """Palauttaa listan päivistä joilta historiaa löytyy (max 7, uusin ensin)."""
    if not os.path.exists("historia"):
        return []
    paivat = []
    for tiedostonimi in os.listdir("historia"):
        if tiedostonimi.endswith(".json"):
            try:
                pvm_str = tiedostonimi.replace(".json", "")
                datetime.strptime(pvm_str, "%Y-%m-%d")  # validointi
                paivat.append(pvm_str)
            except ValueError:
                pass
    return sorted(paivat, reverse=True)[:7]


def luo_html(analysoidut, paivat, paiva_str):
    suomi = timezone(timedelta(hours=3))
    paivitysaika = datetime.now(suomi).strftime("%d.%m.%Y %H:%M")
    relevantit = len(analysoidut)

    # --- Päivänavigaatio ---
    def muotoile_paivanappi(p):
        dt = datetime.strptime(p, "%Y-%m-%d")
        # Windows-yhteensopiva muoto (ei %-d)
        nayta = str(dt.day) + "." + str(dt.month) + "."
        aktiivinen = ' class="aktiivinen"' if p == paiva_str else ''
        return f'<button{aktiivinen} onclick="lataaPaiva(\'{p}\')">{nayta}</button>'

    paivanavigaatio = "\n        ".join(muotoile_paivanappi(p) for p in paivat)

    # --- Uutiskortit ---
    kortit = ""
    for u in analysoidut:
        kortit += f"""
    <div class="uutiskortti"
         data-alue="{u['alue']}"
         data-aihepiiri="{u['aihepiiri']}">
      <div class="kortti-aihepiiri">{u['aihepiiri']}</div>
      <h2>{u['otsikko']}</h2>
      <p>{u['yhteenveto']}</p>
      <div class="lahde-rivi">
        <span class="lahde-teksti">Lähde: {u['lahde']} · {u['alue']}</span>
        <a class="lue-lisaa"
           href="{u['linkki']}"
           target="_blank"
           rel="noopener noreferrer">
          Lue alkuperäinen →
        </a>
      </div>
    </div>
"""

    # --- Filtterivaihtoehdot ---
    alue_napit = '<button class="aktiivinen" onclick="asetaAlue(this, \'kaikki\')">Kaikki alueet</button>\n'
    for a in ALUEET:
        alue_napit += f'        <button onclick="asetaAlue(this, \'{a}\')">{a}</button>\n'

    aihe_napit = '<button class="aktiivinen" onclick="asetaAihe(this, \'kaikki\')">Kaikki aiheet</button>\n'
    for a in AIHEPIIRIT:
        aihe_napit += f'        <button onclick="asetaAihe(this, \'{a}\')">{a}</button>\n'

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
    <nav class="paivanavigaatio">
      <div class="kehys">
        {paivanavigaatio}
      </div>
    </nav>
  </header>

  <div class="filtterit">
    <div class="kehys">
      <div class="filtteri-rivi">
        <span class="filtteri-otsikko">Alue:</span>
        <div class="filtteri-napit" id="alue-napit">
          {alue_napit}
        </div>
      </div>
      <div class="filtteri-rivi">
        <span class="filtteri-otsikko">Aihe:</span>
        <div class="filtteri-napit" id="aihe-napit">
          {aihe_napit}
        </div>
      </div>
      <div class="filtteri-rivi">
        <span class="filtteri-otsikko">Haku:</span>
        <input type="text" id="hakukentta" placeholder="Hae otsikoista ja yhteenvedoista...">
      </div>
    </div>
  </div>

  <main id="uutislista">
    <div class="uutismaara" id="uutismaara">Tänään {relevantit} relevanttia uutista</div>
{kortit}
  </main>

  <footer>
    <p>Uutiset kerätty automaattisesti julkisista lähteistä.</p>
    <p>Kaikki oikeudet alkuperäisille julkaisijoille.</p>
  </footer>

  <script>
    // --- Tila ---
    let aktiivisetKortit = [];
    let valittuAlue = "kaikki";
    let valittuAihe = "kaikki";
    let hakusana = "";
    const ladattuPaiva = "{paiva_str}";

    // --- Alusta kortit sivun latautuessa ---
    document.addEventListener("DOMContentLoaded", () => {{
      aktiivisetKortit = Array.from(document.querySelectorAll(".uutiskortti"));
      document.getElementById("hakukentta").addEventListener("input", (e) => {{
        hakusana = e.target.value.toLowerCase();
        suodataUutiset();
      }});
    }});

    // --- Päivän vaihto ---
    async function lataaPaiva(paiva) {{
      // Päivitä napit
      document.querySelectorAll(".paivanavigaatio button").forEach(b => {{
        const paivaStr = b.getAttribute("onclick").match(/'([^']+)'/)[1];
        b.classList.toggle("aktiivinen", paivaStr === paiva);
      }});

      if (paiva === ladattuPaiva) {{
        // Palauta alkuperäiset kortit
        const lista = document.getElementById("uutislista");
        lista.innerHTML = document.getElementById("alkuperaiset-kortit").innerHTML;
        aktiivisetKortit = Array.from(lista.querySelectorAll(".uutiskortti"));
        suodataUutiset();
        return;
      }}

      try {{
        const vastaus = await fetch("historia/" + paiva + ".json");
        if (!vastaus.ok) throw new Error("Ei löydy");
        const uutiset = await vastaus.json();
        renderKortit(uutiset);
      }} catch (e) {{
        document.getElementById("uutislista").innerHTML =
          '<p class="virhe">Uutisia ei löydy tälle päivälle.</p>';
      }}
    }}

    function renderKortit(uutiset) {{
      const lista = document.getElementById("uutislista");
      let html = '<div class="uutismaara" id="uutismaara">' + uutiset.length + ' uutista</div>';
      uutiset.forEach(u => {{
        html += '<div class="uutiskortti" data-alue="' + u.alue + '" data-aihepiiri="' + u.aihepiiri + '">' +
          '<div class="kortti-aihepiiri">' + u.aihepiiri + '</div>' +
          '<h2>' + u.otsikko + '</h2>' +
          '<p>' + u.yhteenveto + '</p>' +
          '<div class="lahde-rivi">' +
            '<span class="lahde-teksti">Lähde: ' + u.lahde + ' · ' + u.alue + '</span>' +
            '<a class="lue-lisaa" href="' + u.linkki + '" target="_blank" rel="noopener noreferrer">Lue alkuperäinen →</a>' +
          '</div></div>';
      }});
      lista.innerHTML = html;
      aktiivisetKortit = Array.from(lista.querySelectorAll(".uutiskortti"));
      suodataUutiset();
    }}

    // --- Filtterit ---
    function asetaAlue(nappi, arvo) {{
      valittuAlue = arvo;
      document.querySelectorAll("#alue-napit button").forEach(b => b.classList.remove("aktiivinen"));
      nappi.classList.add("aktiivinen");
      suodataUutiset();
    }}

    function asetaAihe(nappi, arvo) {{
      valittuAihe = arvo;
      document.querySelectorAll("#aihe-napit button").forEach(b => b.classList.remove("aktiivinen"));
      nappi.classList.add("aktiivinen");
      suodataUutiset();
    }}

    function suodataUutiset() {{
      let nakyvia = 0;
      aktiivisetKortit.forEach(kortti => {{
        const alue = kortti.dataset.alue || "";
        const aihe = kortti.dataset.aihepiiri || "";
        const teksti = (kortti.querySelector("h2").textContent + " " +
                        (kortti.querySelector("p") ? kortti.querySelector("p").textContent : "")).toLowerCase();

        const alueOk = valittuAlue === "kaikki" || alue === valittuAlue;
        const aiheOk = valittuAihe === "kaikki" || aihe === valittuAihe;
        const hakuOk = hakusana === "" || teksti.includes(hakusana);

        kortti.style.display = (alueOk && aiheOk && hakuOk) ? "" : "none";
        if (alueOk && aiheOk && hakuOk) nakyvia++;
      }});

      const maara = document.getElementById("uutismaara");
      if (maara) maara.textContent = nakyvia + " uutista";
    }}
  </script>

</body>
</html>"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\nValmis! {relevantit} relevanttia uutista.")
    print(f"Päivitetty: {paivitysaika}")


if __name__ == "__main__":
    suomi = timezone(timedelta(hours=3))
    paiva_str = datetime.now(suomi).strftime("%Y-%m-%d")

    # 1. Hae uutiset RSS-syötteistä
    uutiset = hae_uutiset()

    # 2. Suodata ja analysoi tekoälyllä
    analysoidut = []
    for u in uutiset:
        print(f"Tarkistetaan relevanssi: {u['otsikko'][:60]}...")
        if not on_relevantti(u["otsikko"], u["yhteenveto"]):
            print(f"  → Hylätty")
            continue
        print(f"  → Relevantti! Analysoidaan...")
        analyysi = analysoi_uutinen(u["otsikko"], u["yhteenveto"])
        analysoidut.append({
            "otsikko": u["otsikko"],
            "linkki": u["linkki"],
            "lahde": u["lahde"],
            "yhteenveto": analyysi["yhteenveto"],
            "alue": analyysi["alue"],
            "aihepiiri": analyysi["aihepiiri"],
            "paiva": paiva_str
        })

    # 3. Tallenna historiaan
    tallenna_historia(analysoidut, paiva_str)

    # 4. Hae saatavilla olevat päivät
    paivat = hae_saatavilla_olevat_paivat()

    # 5. Luo HTML
    luo_html(analysoidut, paivat, paiva_str)
