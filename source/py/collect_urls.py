import feedparser
import os

# --- CONFIGURATION ---

# List of independent news sources
FEEDS_INDEPENDENT = [
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
    "https://rtl.hu/rss/huszonegy-perc",
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

# List of pro-government/other sources
FEEDS_GOV = [
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


# --- FUNCTIONS ---

def fetch_urls_from_feed(feed_url: str, keywords: list = None, limit: int = None) -> set:
    """Parses a single feed and returns a set of matching URLs."""
    urls = set()
    try:
        feed = feedparser.parse(feed_url)
    except Exception as e:
        print(f"Error reading feed ({feed_url}): {e}")
        return urls

    count = 0
    for entry in feed.entries:
        # Check if we reached the limit for this specific feed
        if limit is not None and count >= limit:
            break

        url = entry.get('link')
        if not url:
            continue

        # If keywords are provided, filter the entries
        if keywords:
            text = (entry.get('title', '') + " " + entry.get('summary', '')).lower()
            if not any(k.lower() in text for k in keywords):
                continue  # Skip if no keyword match

        urls.add(url)
        count += 1

    return urls


def load_existing_urls(filepath: str) -> set:
    """Reads existing URLs from the file to prevent duplicates."""
    existing = set()
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    existing.add(line.strip())
    return existing


def collect_news(category_id: int, output_file: str, keywords: list = None, max_items: int = None):
    """
    Main logic controller.
    category_id: 0 for Independent, 1 for Government
    """

    # 1. Select Source List
    if category_id == 0:
        feed_list = FEEDS_INDEPENDENT
        print(f"--- Collecting INDEPENDENT news (Target: {max_items if max_items else 'Unlimited'}) ---")
    else:
        feed_list = FEEDS_GOV
        print(f"--- Collecting PRO-GOVERNMENT news (Target: {max_items if max_items else 'Unlimited'}) ---")

    # 2. Load already saved URLs to avoid duplicates
    saved_urls = load_existing_urls(output_file)
    initial_count = len(saved_urls)
    new_items_count = 0

    # 3. Iterate through feeds
    with open(output_file, 'a', encoding='utf-8') as f:
        for feed_url in feed_list:
            # Global limit check
            if max_items is not None and new_items_count >= max_items:
                break

            # Fetch URLs from current feed
            fetched_urls = fetch_urls_from_feed(feed_url, keywords)

            current_feed_new = 0
            for url in fetched_urls:
                if url not in saved_urls:
                    f.write(url + "\n")
                    saved_urls.add(url)  # Add to set
                    new_items_count += 1
                    current_feed_new += 1

                    # Stop if we hit the global limit mid-feed
                    if max_items is not None and new_items_count >= max_items:
                        break

            if current_feed_new > 0:
                print(f"Saved {current_feed_new} new articles from: {feed_url}")

    print("-" * 50)
    print(f"Finished. Total new items saved: {new_items_count}")
    print(f"File '{output_file}' now contains {len(saved_urls)} unique URLs.")
    print("-" * 50)


# --- EXECUTION ---

if __name__ == "__main__":
    # Example usage:
    # 0 = Independent, 1 = Gov

    # Collect 200 independent articles
    collect_news(category_id=0, output_file='../../data/0urls.txt', keywords=KEYWORDS, max_items=200)

    # Collect 200 pro-gov articles
    collect_news(category_id=1, output_file='../../data/1urls.txt', keywords=KEYWORDS, max_items=200)