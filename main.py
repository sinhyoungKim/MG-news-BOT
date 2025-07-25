from flask import Flask
from threading import Thread
import os
import requests
import time
import feedparser
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ 봇이 살아있어요!"

# ✅ 뉴스봇 설정
KEYWORD = "새마을금고"
BOT_TOKEN = "7154715773:AAGEHbCEtnvrZ5LNVZxUw3WiUiRINfO6iHU"
CHAT_ID = "-1002887632454"
INTERVAL = 600  # 10분
MAX_NEWS_COUNT = 10
TIME_LIMIT_MINUTES = 10
sent_titles = set()

def shorten_url(url):
    try:
        res = requests.get(f"https://tinyurl.com/api-create.php?url={url}", timeout=5)
        if res.status_code == 200:
            return res.text
    except Exception as e:
        print("❌ URL 축소 실패:", e)
    return url

def is_recent_news(published_time_str):
    try:
        published_time = datetime(*feedparser._parse_date(published_time_str)[:6])
        now = datetime.utcnow()
        return (now - published_time) <= timedelta(minutes=TIME_LIMIT_MINUTES)
    except:
        return False

def get_news():
    url = f"https://news.google.com/rss/search?q={KEYWORD}&hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(url)
    news_list = []

    for entry in feed.entries:
        if entry.title in sent_titles:
            continue
        if not is_recent_news(entry.published):
            continue

        short_link = shorten_url(entry.link)
        news_list.append((entry.title, short_link))
        sent_titles.add(entry.title)

        if len(news_list) >= MAX_NEWS_COUNT:
            break
    return news_list

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "disable_web_page_preview": False}
    try:
        requests.post(url, data=payload, timeout=5)
    except Exception as e:
        print("❌ 텔레그램 전송 실패:", e)

def news_loop():
    while True:
        print("🔎 뉴스 수집 중...")
        news = get_news()
        if news:
            for title, link in news:
                message = f"📰 {title}\n🔗 {link}"
                send_telegram_message(message)
                print("✅ 전송:", title)
        else:
            print("❌ 새로운 뉴스 없음")
        time.sleep(INTERVAL)

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    Thread(target=run).start()        # Flask 서버
    Thread(target=news_loop).start()  # 뉴스 루프
