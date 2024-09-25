import os
from flask import Flask, render_template
import feedparser
from bs4 import BeautifulSoup


app = Flask(__name__)

# RSS feeds #

game_reviews_rss_urls = [
    'https://feeds.feedburner.com/ign/video-reviews',
    'https://www.gamespot.com/feeds/reviews'
]

main_articles_rss_urls = [
    'https://feeds.feedburner.com/ign/games-all'
]

tech_articles_rss_urls = [
    'https://feeds.feedburner.com/ign/tech-articles'
]

movie_reviews_rss_urls = [
    'https://www.gamespot.com/feeds/entertainment-reviews'
]

game_articles_rss_urls = [
    'https://www.gamespot.com/feeds/game-news'
]

# Function to add paragraph tags

def add_paragraphs(content):
    if '</p><p dir="ltr">' in content:
        content = content.replace('</p><p dir="ltr">', '</p> <p dir="ltr">')
    return content



# Fetch articles #

def fetch_articles(rss_urls, include_video=False):
    articles = []
    for url in rss_urls:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            summary = entry.summary
            formatted_summary = add_paragraphs(summary)  # Format the summary with paragraphs

            article = {
                'title': entry.title,
                'link': entry.link,
                'summary': formatted_summary,  # Use formatted summary here
                'thumbnail': None,
                'video': None
            }

            # Handle media content
            if 'media_thumbnail' in entry and entry.media_thumbnail:
                article['thumbnail'] = entry.media_thumbnail[0].get('url', None)
            elif 'media_content' in entry:
                for media in entry.media_content:
                    if media.get('type') == 'image/png' or media.get('type') == 'image/jpeg':
                        article['thumbnail'] = media.get('url')
                    elif include_video and media.get('type') == 'video/mp4':
                        article['video'] = media.get('url')

            articles.append(article)
    return articles

# Routing pages #

@app.route('/')
def home():
    articles = fetch_articles(main_articles_rss_urls)
    return render_template('index.html', articles=articles)

@app.route('/game-reviews')
def game_reviews():
    articles = fetch_articles(game_reviews_rss_urls, include_video=True)
    return render_template('game_reviews.html', articles=articles)

@app.route('/tech-news')
def tech_news():
    articles = fetch_articles(tech_articles_rss_urls)
    return render_template('tech_news.html', articles=articles)

@app.route('/movie-reviews')
def movie_reviews():
    articles = fetch_articles(movie_reviews_rss_urls, include_video=True)
    return render_template('movie_reviews.html', articles=articles)

@app.route('/game-articles')
def game_articles():
    articles = fetch_articles(game_articles_rss_urls)
    return render_template('game_articles.html', articles=articles)

if __name__ == '__main__':
    app.run(debug=True)
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))