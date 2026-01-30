import hu_core_news_lg
import pandas as pd
import spacy
import os
from tqdm import tqdm
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.model_selection import StratifiedKFold

try:
    nlp = spacy.load("hu_core_news_lg")
except:
    print("Can't found the big modell. Using the medium sized...")
    nlp = spacy.load("hu_core_news_md")
nlp = hu_core_news_lg.load()
RAW_CSV = r"../../data/articles_example.csv"
PROCESSED_CSV = r"../../data/preprocessed_articles_example.csv"
csv_file = r"../../data/articles.csv"

def spacy_preprocess_pipe(texts, batch_size=50):
    cleaned_texts = []

    for doc in tqdm(nlp.pipe(texts, batch_size=batch_size, disable=["ner", "parser"]),
                    total=len(texts),
                    desc="Preprocessing the text"):

        tokens = []
        for token in doc:
            if token.is_stop or token.is_punct:
                continue
            if token.like_num:
                tokens.append("NUM")
            else:
                tokens.append(token.lemma_)

        cleaned_texts.append(" ".join(tokens))

    return cleaned_texts


def get_training_data():
    # 1. Loading the raw data
    if not os.path.exists(RAW_CSV):
        raise FileNotFoundError(f"No sourcefile: {RAW_CSV}")

    df_raw = pd.read_csv(RAW_CSV, encoding="utf-8-sig")
    df_raw = df_raw.dropna(subset=['title', 'text', 'url'])

    # 2. Check if there's a saved file
    if os.path.exists(PROCESSED_CSV):
        df_processed = pd.read_csv(PROCESSED_CSV, encoding="utf-8-sig")
        processed_urls = set(df_processed['url'])
        print(f"Loaded {len(df_processed)} preprocessed articles.")
    else:
        df_processed = pd.DataFrame(columns=['url', 'cleaned_text', 'label'])
        processed_urls = set()
        print("There's no preprocessed articles.")

    # 3. Filter out
    df_new = df_raw[~df_raw['url'].isin(processed_urls)].copy()

    if df_new.empty:
        print("There's no preprocessed articles. Working from the cache")
    else:
        print(f"Under preprocessing: {len(df_new)} new articles...")

        df_new['full_text'] = df_new['title'] + ": " + df_new['text']

        df_new['cleaned_text'] = spacy_preprocess_pipe(df_new['full_text'].tolist())

        # 4. Save
        df_to_save = df_new[['url', 'cleaned_text', 'label']]
        header_needed = not os.path.exists(PROCESSED_CSV)

        df_to_save.to_csv(PROCESSED_CSV, mode='a', index=False, header=header_needed, encoding='utf-8-sig')

        df_processed = pd.concat([df_processed, df_to_save], ignore_index=True)
        print("New datas saved.")

    return df_processed['cleaned_text'], df_processed['label']


def preprocess():
    x, y = get_training_data()
    y = y.astype(int)
    x.sample()

    hu_stop_words = [
        "2010", "2020", "a", "abban", "ad", "adatvédelmi", "ahhoz", "ahogy",
        "ahol", "ahogy", "aki", "akik", "akit", "akár", "akkor", "alá", "alatt", "által",
        "általában", "amely", "amelyek", "amelyekben", "amelyeket", "amelyet", "amelynek",
        "ami", "amíg", "amikor", "amit", "amolyan", "amúgy", "annak", "arra", "arról",
        "át", "az", "azért", "azok", "azoknak", "azon", "azonban", "azt", "aztán",
        "azután", "azzal", "ászf", "bár", "be", "bele", "belül", "benne", "cikk",
        "cikkek", "cikkeket", "com", "copyright", "csak", "de", "e", "ebben", "eddig",
        "egész", "egy", "egyéb", "egyes", "egyetlen", "egyik", "egyre", "ehhez", "ekkor",
        "el", "elég", "ellen", "elő", "először", "előtt", "első", "ember", "emilyen",
        "én", "ennek", "éppen", "erre", "es", "esetleg", "és", "evvel", "ez", "ezek",
        "ezen", "ezért", "ezt", "ezzel", "fel", "feladva", "felé", "felett", "fel",
        "főleg", "ha", "hanem", "hát", "hello", "helló", "helyett", "hirtelen",
        "hiszen", "hogy", "hogyan", "hol", "hozzászólás", "hozzászólások", "http",
        "ide", "igen", "így", "igy", "ill", "ill.", "illetve", "ilyen", "ilyenkor",
        "impresszum", "is", "ismét", "ison", "itt", "jó", "jobban", "jog fenntartva",
        "jogi nyilatkozat", "jól", "kategória", "kell", "kellett", "keressünk",
        "keresztül", "ki", "kis", "kívül", "komment", "köszönöm", "köszönjük", "köszi",
        "közepette", "között", "közül", "külön", "le", "legalább", "legyen", "lehet",
        "lehetett", "lenne", "lenni", "lesz", "lett", "maga", "magam", "magatokat",
        "magát", "magunk", "magunkat", "magunkkal", "magunkra", "majd", "már", "más",
        "másik", "meg", "még", "mellett", "mely", "melyek", "mert", "mi", "miért",
        "míg", "mikor", "milyen", "mind", "minden", "mindenki", "mindenkinek",
        "mindenkit", "mindent", "mindig", "mindneki", "mint", "mintha", "mit",
        "mivel", "most", "nagy", "nagyobb", "nagyon", "ne", "néha", "néhány",
        "nekem", "neki", "nélkül", "nem", "nincs", "ő", "oda", "ők", "õk", "őket",
        "oka", "olyan", "ön", "os", "össze", "ott", "pedig", "persze", "pici",
        "picivel", "pont", "rá", "rám", "rajtam", "ripost", "rólam", "rólunk", "rss",
        "s", "saját", "sajnos", "sem", "semmi", "soha", "sok", "sokat", "sokkal",
        "száma", "számára", "szemben", "szerint", "szerintem", "szeretettel",
        "szerző", "szét", "szia", "sziasztok", "szinte", "szó", "talán", "te",
        "tehát", "teljes", "ti", "több", "tőle", "tőlem", "tőletek", "tőlük",
        "tőlünk", "tovább", "továbbá", "üdv", "úgy", "ugyanis", "új", "újabb",
        "újra", "után", "utána", "utolsó", "vagy", "vagyis", "vagyok", "valaki",
        "valami", "valamint", "valamit", "valaminek", "valamiért", "való", "van",
        "vannak", "vele", "velem", "veletek", "velük", "vissza", "viszont", "volna",
        "volt", "voltak", "voltam", "voltunk", "www"
    ]

    vectorizer = CountVectorizer(ngram_range=(1,2), token_pattern=r'\b\w+\b', min_df=1, max_df=0.9, max_features=2000, stop_words=hu_stop_words)
    x_counts = vectorizer.fit_transform(x)

    tfidf = TfidfTransformer(sublinear_tf=True)
    x_tfidf = tfidf.fit_transform(x_counts)

    # Train, valid, test

    from sklearn.model_selection import train_test_split

    x_train_full, x_test, y_train_full, y_test = train_test_split(
        x_tfidf, y,
        test_size=0.15,
        random_state=42,
        stratify=y
    )
    print(f"Learning+Validating dataset size: {x_train_full.shape[0]}")
    print(f"Test dataset size: {x_test.shape[0]}")

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    fold = 1
    for train_index, val_index in skf.split(x_train_full, y_train_full):
        x_train, x_valid = x_train_full[train_index], x_train_full[val_index]
        y_train, y_valid = y_train_full.iloc[train_index], y_train_full.iloc[val_index]

        print(f"\n--- {fold}. FOLD ---")
        print(f"Learning (x_train): {x_train.shape[0]} db")
        print(f"Validation (x_valid): {x_valid.shape[0]} db")
        print(f"Test (x_test): {x_test.shape[0]} db (fix)")

        fold += 1

    return x_train, x_valid, x_test, y_train, y_valid, y_test


