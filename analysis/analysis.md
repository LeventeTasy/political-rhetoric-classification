# Analysis

## 1. Data Collection
The data was collected between *December 2025* and *January 2026*. The model uses approximately **1,700 articles**, half of which are propaganda rhetoric articles and half of which are independent rhetoric articles. Since the data was collected only in the last month, it can only produce reliable results in *current politics*.

The data collection process consisted of two main phases, ensuring relevance and a balanced data set.

### a) URL Discovery via RSS Feeds 
I classified the news sources into two categories: *Independent* and *Pro-Government*. For data collection, I used the `feedparser` library to monitor RSS feeds.
- **Keyword filtering:** I only collected articles whose title or summary contained specific *political keywords* (e.g., Brussels, war, EU, Orban, Peter Magyar). This ensured that the model learned political rhetoric rather than sports news or tabloid gossip.
- **Duplication filtering:** Before each save, the system checked for existing URLs, thus avoiding distortion of the data set with duplicate content.

### b) Article Scraping
Based on the collected URLs, I downloaded the full text of the articles using the `newspaper3k` library. I recorded the data in CSV format (url, title, text, label), where the label (0 or 1) indicates the category of the news source.

<!--stackedit_data:
eyJoaXN0b3J5IjpbMTQ3NjcxODgzMCwtNjk1Nzg3OTEzLC04OT
IxNzYzODksLTY1NDQ5MDIyNF19
-->