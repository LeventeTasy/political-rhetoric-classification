# Project Documentation

## 1. Data Collection
The data was collected between *December 2025* and *January 2026*. The model uses approximately **1,700 articles**, half of which are propaganda rhetoric articles and half of which are independent rhetoric articles. Since the data was collected only in the last month, it can only produce reliable results in *current politics*. Labels reflect source affiliation and rhetorical style, *not factual correctness*. Also, it can only be used with Hungarian-language texts/articles.

The data collection process consisted of two main phases, ensuring relevance and a balanced data set.

### a) URL Discovery via RSS Feeds 
I classified the news sources into two categories: *Independent* and *Pro-Government*. For data collection, I used the `feedparser` library to monitor RSS feeds.
- **Keyword filtering:** I only collected articles whose title or summary contained specific *political keywords* (e.g., Brussels, war, EU, Orban, Peter Magyar). This ensured that the model learned political rhetoric rather than sports news or tabloid gossip.
- **Duplication filtering:** Before each save, the system checked for existing URLs, thus avoiding distortion of the data set with duplicate content.

### b) Article Scraping
Based on the collected URLs, I downloaded the full text of the articles using the `newspaper3k` library. I recorded the data in CSV format (`url`, `title`, `text`, `label`), where the `label` (0 or 1) indicates the category of the news source.

### Usage
Let's look at an example code of how can we expand the CSV file with independent articles:
```python
from collect_urls import collect_news
from process_articles import process_articles

# Collecting new URLs using RSS feeds
KEYWORDS = [...]
collect_news(category_id=0, output_file='../../data/0urls.txt', keywords=KEYWORDS, max_items=200) # It is not necessary to specify the max_items or keywords from the outset.

# Downloading the articles, and attach them to the CSV file
process_articles(source_file="../../data/0urls.txt", label=0) # 0 = Independent, 1 = Pro-Government
```
## 2. Preprocessing
When preparing the data, the goal was to reduce the noise level of the text and standardize the encoding of the content. To do this, I used the SpaCy (Hungarian language model) library through an optimized nlp.pipe process.
### a) The Cleaning Workflow
The `spacy_preprocess_pipe` function performs the following steps: 
- **Tokenization and Filtering:** I removed stop words (conjunctions, articles) and punctuation marks, as these do not carry political meaning in terms of rhetorical analysis. 
-  **Lemmatization:** I reduced every word to its root form. This is a critical step in Hungarian due to the high variability of inflection, as it allows the TF-IDF model to combine words with the same meaning. 
- **Numerical Standardization:** I replaced numbers with a uniform `NUM` token. This helps the model recognize statistical-based reasoning without treating each unique year or amount as a separate feature. 
- **Title and Content Merging:** I treated the article title and body text as a single unit, as titles often contain the strongest rhetorical markers.
### b) Efficiency and Incremental Loading
- **Batch Processing:** Using SpaCy `nlp.pipe` allows for batch processing of texts, which is significantly faster than calling the model line by line.
- **Persistent Caching:** I introduced an incremental processing logic. The program checks the URLs already processed in `processed_articles.csv` and only runs new articles through the NLP pipeline. This saves significant computing capacity when expanding the database.

## 3. Feature Engineering
I used a two-step process for the mathematical representation of the texts: *CountVectorizer* to measure frequencies and *TfidfTransformer* for weighting.
### a) CountVectorizer:
When configuring CountVectorizer, I made several critical decisions to improve the accuracy of the model:
- **N-gram Range (1, 2):** I examined not only individual words (unigrams) but also word combinations (bigrams). This is essential in political rhetoric, where expressions such as "Peter Magyar" or "European Union" have a much stronger meaning than their individual words.
- **Max Features (2000):** I limited the vocabulary to the 2000 most important elements. This helps prevent overfitting and ensures that the model focuses only on the most statistically relevant rhetorical elements.
- **Min_df / Max_df:** I excluded words that appear in more than 90% of the documents (too common, no distinguishing power), thus refining the model's focus.
### b) TfidfTransformer
I weighted the raw frequency data using TfidfTransformer to give more weight to less frequent but more informative words. I used the *sublinear_tf=True* setting, which uses logarithmic scaling (1 + log(TF)). This prevents a word from becoming overly dominant simply because it is repeated many times in an article (for example, in a long list).
## 
<!--stackedit_data:
eyJoaXN0b3J5IjpbLTI5MzMzNjk5MSwtODYwMjE5OTQ1LC0xMT
A4MTkxMzUsLTczMjEzMTQ2NywtNjk1Nzg3OTEzLC04OTIxNzYz
ODksLTY1NDQ5MDIyNF19
-->