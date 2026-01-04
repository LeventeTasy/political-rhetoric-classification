import feedparser
import os

# --- JAVÍTOTT LISTA (Vessző pótolva!) ---
feeds_0 = [
    "https://telex.hu/rss",
    "https://444.hu/feed",
    "http://hvg.hu/rss/rss.hvg/hirek",
    "http://hvg.hu/rss/rss.hvg/szemle",
    "https://24.hu/tag/rss/",
    "https://rss.feedspot.com/rss_feeds/nezszava-hu-news-feed.xml",
    "https://rss.hirkereso.hu/hirsiteok/atlatszo/",
    "https://magyarhang.org/feed",
    "https://szabadeuropa.hu/rss",
    "https://www.valaszonline.hu/feed/",
    "https://direkt36.hu/rss",
    "https://merce.hu/feed",
    "https://nepszava.hu/feed",
    "https://rtl.hu/rss/huszonegy-perc",  # Vessző pótolva
    "https://lakmusz.hu/feed",
    "https://g7.hu/feed",
    "https://forbes.hu/feed",
    "https://media1.hu/feed",
    "https://qubit.hu/feed",
    "https://hu.euronews.com/rss?level=vertical&name=news",
    "https://k-monitor.hu/feed",
    "https://debreciner.hu/feed",
    "https://szabadpecs.hu/feed"
]

feeds_1 = [
    "https://www.origo.hu/contentpartner/rss",
    "http://origo.hu/contentpartner/rss/itthon/origo.rss",
    "https://magyarnemzet.hu/rss",
    "https://mandiner.hu/rss",
    "https://888.hu/rss",
    "https://hirtv.hu/rss",
    "https://ripost.hu/feed",
    "https://metropol.hu/feed",
    "https://borsonline.hu/publicapi/hu/rss",
    "https://pestisracok.hu/feed",
    "https://vadhajtasok.hu/feed",
    "https://demokrata.hu/feed",
    "https://magyarhirlap.hu/rss",
    "https://vasarnap.hu/feed",
    "https://hirado.hu/feed",
    "https://index.hu/24ora/rss/",
    "https://infostart.hu/24ora/rss/",
    "https://www.blikk.hu/rss"
]

KEYWORDS = [
    "brüsszel", "nato", "europai unio", "szankció", "háború", "ukrajna", "oroszország", "kína", "usa", "amerika",
    "zelenszkij", "putyin", "trump", "izrael", "gáza", "európai parlament", "ep", "európai bizottság",
    "kormány", "orbán", "magyar péter", "gyurcsány", "karácsony", "soros", "fidesz", "tisza párt", "ellenzék",
    "dk", "momentum", "mi hazánk",
    "dollárbaloldal", "dollármédia", "békepárti", "háborúpárti", "háborús pszichózis", "szuverenitás",
    "migráns", "gender", "lmbtq", "brüsszeli bürokraták", "guruló dollárok", "szankciós infláció",
    "nemzeti konzultáció", "gyermekvédelem", "patrióták", "blokkosodás", "konnektivitás", "genderideológia",
    "genderlobbi", "melegpropaganda", "gyermekek átnevelése", "woke",
    "infláció", "rezsi", "adó", "korrupció", "pedagógus", "egészségügy", "kórház", "akkumulátorgyár",
    "közpénz", "jogállamiság", "átláthatóság", "közbeszerzés", "tüntetés", "nyugdíj", "minimálbér",
    "veszély", "fenyegetés", "támadás", "megvédeni", "rá akarják erőltetni", "el akarják venni", "brüsszel diktál",
    "nem hagyjuk", "magyar emberek", "családok védelme",
    "ideológia", "nyomásgyakorlás", "háttérhatalom", "félelem", "veszély", "veszélyes"
]


def getUrls(feed_url: str, keywords: list = None, limit: int = None):
    urls = set()
    try:
        feed = feedparser.parse(feed_url)
    except Exception as e:
        print(f"Hiba a feed olvasásakor ({feed_url}): {e}")
        return urls

    db = 0

    if keywords is None:
        for entry in feed.entries:
            if limit is None or db < limit:
                urls.add(entry.link)
                db += 1
            else:
                break
    else:
        for entry in feed.entries:
            if limit is None or db < limit:
                # Cím és összefoglaló összefűzése a jobb találatért
                text = (entry.title + " " + entry.get("summary", "")).lower()
                if any(k.lower() in text for k in keywords):
                    urls.add(entry.link)
                    db += 1
            else:
                break
    return urls


# --- JAVÍTOTT FÜGGVÉNY: saveArticle ---
def saveArticle(filename: str, urls: set):
    eredeti = set()

    # Ha létezik a fájl, olvassuk be, hogy ne legyen duplikátum
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf8') as f:
            for line in f:
                eredeti.add(line.strip())

    mentett_darab = 0
    with open(filename, 'a', encoding='utf-8') as f:
        for url in urls:
            if url not in eredeti:
                f.write(url + "\n")
                mentett_darab += 1

    # A ténylegesen elmentett (új) sorok számát adjuk vissza!
    return mentett_darab


def mentes(output: str, ertek: int = 0, keywords: list = None, limit: int = None):
    if ertek == 0:
        listaja = feeds_0
        kiir = 'független forrás mentve'
    else:
        listaja = feeds_1
        kiir = 'propaganda forrás mentve'

    n_db = 0
    for f in listaja:
        # Ha elértük a limitet globálisan ebben a körben, álljunk meg
        if limit is not None and n_db >= limit:
            break

        # Mennyi kell még?
        aktualis_limit = limit - n_db if limit else None

        urls = getUrls(f, keywords, aktualis_limit)

        if urls:
            uj_mentes = saveArticle(output, urls)
            n_db += uj_mentes
            print(f'{f}: {len(urls)} talált, {uj_mentes} új mentve.')
        else:
            print(f'{f}: 0 talált')

    print("-------------------------------------------------")
    print(f"{n_db} {kiir} ebben a körben.")
    print("-------------------------------------------------")

    return n_db


def main(ertek: int = 0, output: str = '', keywords: list = None, limit: int = None, mennyit: int = None):
    # Itt egyszerűsítettem: a main csak egy wrapper, ami meghívja a mentést
    # A ciklust a gyujtes() intézi
    return mentes(ertek=ertek, output=output, keywords=keywords, limit=limit)


def osszefesul(mit: str, hova: str):
    urls = set()

    if not os.path.exists(mit):
        print(f"Hiba: A forrásfájl nem található: {mit}")
        return

    with open(mit, 'r', encoding='utf8') as f:
        for line in f:
            if line.strip():
                urls.add(line.strip())

    if os.path.exists(hova):
        with open(hova, 'r', encoding='utf8') as f:
            for line in f:
                if line.strip():
                    urls.add(line.strip())

    with open(hova, 'w', encoding='utf8') as f:
        for line in sorted(urls):
            f.write(f'{line}\n')

    print(f'{mit} tartalma összefésülve a {hova} fájllal ({len(urls)} db egyedi sor).')


# --- JAVÍTOTT CIKLUS: gyujtes ---
def gyujtes(ertek: int, osszeszedni: int, maximumszor: int = 1, limit_per_kor: int = None, keywords: list = None):
    osszeszedett = 0
    maximum = 0

    # Készítünk mappát, ha nincs
    os.makedirs('../../data', exist_ok=True)
    temp_file = f'../../data/{ertek}{ertek}urls.txt'
    final_file = f'../../data/{ertek}urls.txt'

    # JAVÍTÁS: 'and' feltétel, hogy bármelyik elérésekor megálljon
    while osszeszedett < osszeszedni and maximum < maximumszor:
        print(f"\n--- {maximum + 1}. KÖR (Eddig: {osszeszedett}/{osszeszedni}) ---")

        # Mennyi hiányzik még?
        hatralevo = osszeszedni - osszeszedett
        aktualis_limit = min(hatralevo, limit_per_kor) if limit_per_kor else hatralevo

        uj = main(ertek, temp_file, keywords, limit=aktualis_limit)

        osszeszedett += uj
        maximum += 1

        if uj == 0:
            print("Nem találtunk új cikket ebben a körben, kilépés.")
            break

    osszefesul(temp_file, final_file)


# Futtatás
#gyujtes(0, 300, keywords=KEYWORDS)
#gyujtes(1, 300, keywords=KEYWORDS)
mentes('0urls_test.txt', 0, KEYWORDS, 10)
mentes('1urls_test.txt', 1, KEYWORDS, 10)