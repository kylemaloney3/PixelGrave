import os
from flask import Flask, render_template
import feedparser
from bs4 import BeautifulSoup
import googleapiclient.discovery

app = Flask(__name__)

# RSS feeds
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
        content = content.replace('</p> <p dir="ltr">', '</p> <p dir="ltr">')
    return content

def clean_html(content):
    soup = BeautifulSoup(content, 'html.parser')
    return str(soup)

# Fetch articles
def fetch_articles(rss_urls, include_video=False):
    articles = []
    for url in rss_urls:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            summary = entry.summary
            formatted_summary = add_paragraphs(summary)
            cleaned_summary = clean_html(formatted_summary)
            article = {
                'title': entry.title,
                'link': entry.link,
                'summary': cleaned_summary,
                'published': entry.published_parsed,
                'thumbnail': None,
                'video': None
            }
            # Handle media content for higher quality thumbnails
            if 'media_thumbnail' in entry and entry.media_thumbnail:
                thumbnails = entry.media_thumbnail
                highest_quality_thumbnail = max(thumbnails, key=lambda t: t.get('width', 0))
                article['thumbnail'] = highest_quality_thumbnail.get('url', None)
            elif 'media_content' in entry:
                thumbnails = [media for media in entry.media_content if media.get('type') in ['image/png', 'image/jpeg']]
                if thumbnails:
                    highest_quality_thumbnail = max(thumbnails, key=lambda t: t.get('width', 0))
                    article['thumbnail'] = highest_quality_thumbnail.get('url', None)
            articles.append(article)
    return sorted(articles, key=lambda x: x['published'], reverse=True)


# YouTube API Functions
YOUTUBE_API_KEY = 'AIzaSyAHBNGwssv5AAQZCRsY7vqCkeu60DqBxi4'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

def get_youtube_service():
    return googleapiclient.discovery.build(
        YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=YOUTUBE_API_KEY)

def fetch_top_videos(youtube, max_results=35):
    request = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        chart="mostPopular",
        regionCode="US",
        videoCategoryId="20",  # Gaming category
        maxResults=max_results
    )
    response = request.execute()
    return response['items']

# Routing pages
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

@app.route('/youtube-top-videos')
def youtube_top_videos():
    youtube_service = get_youtube_service()
    videos = fetch_top_videos(youtube_service)
    return render_template('youtube_top_videos.html', videos=videos)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
    app.run(debug=True)
