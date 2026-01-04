import os
import pandas as pd
import nltk
from newspaper import Article
from url_mentes import gyujtes, KEYWORDS


# Csak egyszer kell futtatni, ha még nincs letöltve
# nltk.download('punkt')

def saveCsv(url_file: str, tipus: int, csv_file: str = r"../../data/propaganda_articles.csv"):
    print(f"\n--- FELDOLGOZÁS INDÍTÁSA: {url_file} ---")

    # 1. LÉPÉS: Megnézzük, mi van már meg a CSV-ben
    kesz_urls = set()
    if os.path.exists(csv_file) and os.path.getsize(csv_file) > 0:
        try:
            # Csak az 'url' oszlopot olvassuk be a gyorsaság érdekében
            df_letezo = pd.read_csv(csv_file, usecols=['url'])
            kesz_urls = set(df_letezo['url'].tolist())
            print(f"Meglévő adatbázis betöltve: {len(kesz_urls)} cikk már mentve.")
        except Exception as e:
            print(f"Hiba a meglévő CSV olvasásakor: {e}")
    else:
        print("Még nem létezik a CSV, vagy üres. Minden URL új lesz.")

    # 2. LÉPÉS: Beolvassuk az új listát a TXT fájlból
    try:
        with open(url_file, "r", encoding="utf-8") as f:
            file_urls = set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        print(f"A forrásfájl nem található: {url_file}")
        return

    # 3. LÉPÉS: A szűrés (Ami a fájlban van MINUSZ ami már a CSV-ben van)
    feldolgozando_urls = list(file_urls - kesz_urls)

    print(f"Forrásfájlban összesen: {len(file_urls)} db URL.")
    print(f"Ebből már megvolt: {len(file_urls) - len(feldolgozando_urls)} db.")
    print(f"Ténylegesen letöltendő: {len(feldolgozando_urls)} db.")
    print("-" * 30)

    if not feldolgozando_urls:
        print("Nincs új cikk, minden URL szerepel már a CSV-ben.")
        return

    # 4. LÉPÉS: Letöltés és mentés
    data = []
    torlendo_urls = []  # Ide gyűjtjük a 403-as hibákat
    hiba = 0
    sikeres = 0

    for url in feldolgozando_urls:
        try:
            article = Article(url)
            article.download()
            article.parse()

            # Ellenőrzés: ha nincs szöveg, az is gyanús lehet, de most hagyjuk
            if not article.text:
                print(f"Figyelem: Üres szöveg letöltve innen: {url}")

            data.append({
                "url": url,
                "title": article.title,
                "text": article.text,
                "label": tipus
            })

            print(f"Siker: {url}")
            sikeres += 1

        except Exception as e:
            msg = str(e)
            print(f"Hiba ({url}): {msg}")

            # Itt figyeljük a 403-as kódot
            if "403" in msg:
                print(f"--> 403 FORBIDDEN észlelve! Ez az URL törlésre kerül a forrásfájlból.")
                torlendo_urls.append(url)

            hiba += 1

    # 5. LÉPÉS: Sikeres cikkek írása a CSV-be
    if data:
        new_df = pd.DataFrame(data)
        kell_fejlec = not os.path.exists(csv_file)
        # Append mode ('a')
        new_df.to_csv(csv_file, mode='a', index=False, header=kell_fejlec, encoding='utf-8')
        print(f"\n{len(data)} új cikk hozzáfűzve a(z) {csv_file} fájlhoz.")

    # 6. LÉPÉS: A 403-as URL-ek törlése a forrásfájlból (url_file)
    if torlendo_urls:
        print(f"\n{len(torlendo_urls)} db hibás (403) URL eltávolítása a forrásfájlból ({url_file})...")

        # Beolvassuk az eredeti fájl sorait
        with open(url_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Visszaírjuk csak azokat, amik NINCSENEK a törlendő listában
        # A strip() azért kell, hogy az összehasonlítás pontos legyen
        torlendo_set = set(torlendo_urls)

        with open(url_file, "w", encoding="utf-8") as f:
            for line in lines:
                if line.strip() not in torlendo_set:
                    f.write(line)

        print("A forrásfájl frissítve lett.")

    print(f"Összesítés: {sikeres} sikeres, {hiba} sikertelen (ebből {len(torlendo_urls)} végleg törölve).")


# Futtatás
print("Start")
#gyujtes(0, 700, keywords=KEYWORDS)
#gyujtes(0, 200, keywords=None)
#gyujtes(1, 700, keywords=KEYWORDS)
saveCsv("../../data/0urls.txt", 0)
saveCsv("../../data/1urls.txt", 1)