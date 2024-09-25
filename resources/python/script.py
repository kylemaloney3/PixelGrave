import feedparser

rss_url = 'https://feeds.feedburner.com/ign/video-reviews'
feed = feedparser.parse(rss_url)

articles = []
for entry in feed.entries:
    articles.append({
        'title': entry.title,
        'link': entry.link,
        'summary': entry.summary
    })

for article in articles:
    print(f"Title: {article['title']}")
    print(f"Link: {article['link']}")
    print(f"Summary: {article['summary']}\n")
