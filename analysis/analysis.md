# Analysis

## 1. Data Collection
The data was collected between *December 2025* and *January 2026*. The model uses approximately **1,700 articles**, half of which are propaganda rhetoric articles and half of which are independent rhetoric articles. Since the data was collected only in the last month, it can only produce reliable results in *current politics*.

The data collection process consisted of two main phases, ensuring relevance and a balanced data set.

### a) URL Discovery via RSS Feeds 
I classified the news sources into two categories: *Independent* and *Pro-Government*. For data collection, I used the `feedparser` library to monitor RSS feeds.
- **Keyword filtering:** I only collected articles whose title or summary contained specific *political keywords* (e.g., Brussels, war, EU, Orban, Peter Magyar). This ensured that the model learned political rhetoric rather than sports news or tabloid gossip.
- **Duplication filtering:** Before each save, the system checked for existing URLs, thus avoiding distortion of the data set with duplicate content.

### b) Article Scraping
Based on the collected URLs, I downloaded the full text of the articles using the `newspaper3k` library. I recorded the data in CSV format (`url`, `title`, `text`, `label`), where the `label` (0 or 1) indicates the category of the news source.

### Usage
In the `collect_urls.py` file, we can easily save the URLs from the RSS feeds, using this code:
```python
# Collect 200 independent articles  
collect_news(category_id=0, output_file='../../data/0urls_example.txt', keywords=KEYWORDS, max_items=200)  
  
# Collect 200 pro-gov articles  
collect_news(category_id=1, output_file='../../data/1urls_example.txt', keywords=KEYWORDS, max_items=200)
```
In the `process_articles.py` file, we are able to 
Let's look at an example code of how we can expand the CSV file with independent articles:
```python
from collect_urls import collect_news
from process_articles import process_articles

# Collecting new URLs using RSS feeds
KEYWORDS = [...]
collect_news(category_id=0, output_file='../../data/0urls.txt', keywords=KEYWORDS, max_items=200) # It is not necessary to specify the max_items or keywords from the outset.

# Downloading the articles, and attach them to the CSV file
process_articles(source_file="../../data/0urls.txt", label=0) # 0 = Independent, 1 = Pro-go
```

<!--stackedit_data:
eyJoaXN0b3J5IjpbLTc0MTU3MDgxOCwtNjk1Nzg3OTEzLC04OT
IxNzYzODksLTY1NDQ5MDIyNF19
-->