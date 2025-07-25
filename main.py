from keep_alive import keep_alive
keep_alive()  # Render나 Replit에서 서버 유지용

import requests
import time
import feedparser
from datetime import datetime, timedelta

# ✅ 설정
KEYWORD = "새마을금고"
BOT_TOKEN = "7154715773:AAGEHbCEtnvrZ5LNVZxUw3WiUiRINfO6iHU"
CHAT_ID = "-1002887632454"  # ✅ 단톡방 chat_id
INTERVAL = 600  # 10분 간격 (초 단위)
MAX_NEWS_COUNT = 10  # 한 번에 전송할 뉴스 수 제한
TIME_LIMIT_MINUTES = 10  # 최근 10분 이내 뉴스만 전송

sent_titles = set()  # 이미 전송한 제목 저장용

def shorten_url(url):
    """TinyURL을 사용하여 링크 축소"""
    try:
        res = requests.get(f"https://tinyurl.com/api-create.php?url={url}", timeout=5)
        if res.status_code == 200:
            return res.text
    except Exception as e:
        print("❌ URL 축소 실패:", e)
    return url  # 실패 시 원본 링크 사용

def is_recent_news(published_time_str):
    """뉴스가 최근 10분 이내에 발행됐는지 확인"""
    try:
        published_time = datetime(*feedparser._parse_date(published_time_str)[:6])
        now = datetime.utcnow()
        return (now - published_time) <= timedelta(minutes=TIME_LIMIT_MINUTES)
    except:
        return False

def get_news():
    """RSS에서 뉴스 수집"""
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
    """텔레그램 메시지 전송"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "disable_web_page_preview": False
    }
    try:
        requests.post(url, data=payload, timeout=5)
    except Exception as e:
        print("❌ 텔레그램 전송 실패:", e)

# ✅ 메인 루프
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
