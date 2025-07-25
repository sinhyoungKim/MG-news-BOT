import requests
import schedule
import time
from bs4 import BeautifulSoup
from telegram import Bot
from collections import deque
from keep_alive import keep_alive  # 웹서버용

# ✅ 텔레그램 정보 (직접 입력)
TOKEN = '7154715773:AAGEHbCEtnvrZ5LNVZxUw3WiUiRINfO6iHU'
CHAT_ID = '-1002887632454'
bot = Bot(token=TOKEN)

# ✅ 키워드 및 필터
KEYWORDS = ["새마을금고", "금고", "MG"]
FILTER_KEYWORDS = ["새마을금고", "MG"]  # 메시지 전송 필터

# ✅ 최근 뉴스 링크 저장 (중복 방지, 최대 100개)
SENT_NEWS = deque(maxlen=100)

def shorten_url(url):
    try:
        res = requests.get(f"https://tinyurl.com/api-create.php?url={url}")
        if res.status_code == 200:
            return res.text.strip()
        else:
            return url
    except Exception as e:
        print(f"[❌] URL 단축 실패: {e}")
        return url

def get_news():
    print("🔍 뉴스 수집 중...")
    for keyword in KEYWORDS:
        url = f"https://news.google.com/rss/search?q={keyword}&hl=ko&gl=KR&ceid=KR:ko"
        try:
            res = requests.get(url)
            res.raise_for_status()
            soup = BeautifulSoup(res.content, 'xml')
            items = soup.findAll('item')

            for entry in items:
                title = entry.title.text
                link = entry.link.text

                if not any(fk in title for fk in FILTER_KEYWORDS):
                    continue
                if link in SENT_NEWS:
                    continue

                short_url = shorten_url(link)
                message = f"📰 [{keyword}] {title}\n{short_url}"

                try:
                    bot.send_message(chat_id=CHAT_ID, text=message)
                    print(f"✅ 전송됨: {title}")
                    SENT_NEWS.append(link)
                except Exception as e:
                    print(f"[❌] 메시지 전송 실패: {e}")
                    time.sleep(5)

        except Exception as e:
            print(f"[❌] 뉴스 수집 오류 ({keyword}): {e}")
            time.sleep(5)

# ✅ keep_alive 서버 실행
keep_alive()

# ✅ 10분마다 실행
schedule.every(10).minutes.do(get_news)

# ✅ 루프 실행
print("🚀 뉴스 봇 실행 중...")
while True:
    schedule.run_pending()
    time.sleep(1)
