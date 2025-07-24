from keep_alive import keep_alive
keep_alive()  # Replit 서버 유지용

import requests
import time
import feedparser

# ✅ 설정
KEYWORD = "새마을금고"
BOT_TOKEN = "7154715773:AAGEHbCEtnvrZ5LNVZxUw3WiUiRINfO6iHU"
CHAT_ID = "7370751504"
INTERVAL = 600  # 10분 간격 (초 단위)
MAX_NEWS_COUNT = 10  # 한 번에 전송할 뉴스 수 제한

sent_titles = set()

def shorten_url(url):
    """TinyURL을 사용하여 링크를 축소"""
    try:
        res = requests.get(f"https://tinyurl.com/api-create.php?url={url}", timeout=5)
        if res.status_code == 200:
            return res.text
    except Exception as e:
        print("❌ URL 축소 실패:", e)
    return url  # 실패 시 원본 링크 사용

def get_news():
    """RSS 피드에서 최근 10분 이내의 새 뉴스 수집"""
    url = f"https://news.google.com/rss/search?q={KEYWORD}&hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(url)
    now = time.time()
    news_list = []

    for entry in feed.entries:
        if hasattr(entry, 'published_parsed'):
            published_time = time.mktime(entry.published_parsed)
            elapsed = now - published_time

            # 최근 10분 이내 뉴스만 필터링
            if elapsed <= INTERVAL and entry.title not in sent_titles:
                short_link = shorten_url(entry.link)
                news_list.append((entry.title, short_link))
                sent_titles.add(entry.title)

        if len(news_list) >= MAX_NEWS_COUNT:
            break

    return news_list

def send_telegram_message(text):
    """텔레그램 메시지 전송"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
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
