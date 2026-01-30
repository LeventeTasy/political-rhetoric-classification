import pandas as pd
from joblib import load
import csv

try:
    MODEL_PATH = '../../models/ensemble_pipeline_id1_0_89.joblib'
    model = load(MODEL_PATH)
    domains = set()
    data = []
    osszesito = {}

    df = pd.read_csv('../../data/preprocessed_articles.csv')

    with open('../../data/new_articles.csv', mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)

        # 1. Fejléc megírása
        writer.writerow(['url', 'label', 'predicted label'])

        # 2. Adatok írása sorról sorra
        for index, row in df.iterrows():
            # Itt a row már egy olyan objektum, amit oszlopnévvel indexelhetsz
            if 'www.' in row['url']:
                domain = row['url'].split('www.')[1].split('/')[0]
            elif 'http://' in row['url']:
                domain = row['url'].split('http://')[1].split('/')[0]
            else:
                domain = row['url'].split('https://')[1].split('/')[0]
            label = row['label']
            prediction = int(model.predict([row['cleaned_text']])[0])

            sor = [domain, label, prediction]
            domains.add(domain)
            data.append(sor)
            print(sor)
            writer.writerow(sor)

    for domain in domains:
        osszesito[domain] = [0, 0]

    for i in data:
        if i[1] != i[2]:
            osszesito[i[0]][1] += 1
        else:
            osszesito[i[0]][0] += 1

    print('Domanin\tTalálat\tHiba')
    for k, i in osszesito.items():
        print(f'{k}\t{i[0]}\t{i[1]}')
except FileNotFoundError:
    print("Hiba: A fájl nem található. Ellenőrizd az elérési utat!")