from keep_alive import keep_alive
import time
import requests
from bs4 import BeautifulSoup
from telegram import Bot

# 설정값
TOKEN = '7154715773:AAGEHbCEtnvrZ5LNVZxUw3WiUiRINfO6iHU'
CHAT_ID = '-1002887632454'
bot = Bot(token=TOKEN)

# 키워드 설정
KEYWORDS = ["새마을금고", "금고", "MG"]
FILTER_KEYWORDS = ["새마을금고", "MG"]  # 전송 필터 키워드 (잡음 방지)

# 중복 뉴스 방지
SENT_NEWS = set()

def shorten_url(url):
    try:
        res = requests.get(f"https://tinyurl.com/api-create.php?url={url}")
        return res.text.strip()
    except Exception as e:
        print(f"URL 단축 실패: {e}")
        return url

def get_news():
    print("🔎 뉴스 수집 중...")
    for keyword in KEYWORDS:
        url = f"https://news.google.com/rss/search?q={keyword}&hl=ko&gl=KR&ceid=KR:ko"
        try:
            res = requests.get(url)
            soup = BeautifulSoup(res.content, 'xml')
            items = soup.findAll('item')
            
            for entry in items:
                title = entry.title.text
                link = entry.link.text

                # 잡음 필터링: 제목에 필수 키워드 포함 여부 확인
                if not any(fk in title for fk in FILTER_KEYWORDS):
                    continue  # 새마을금고/MG 안 들어간 뉴스는 스킵

                if link in SENT_NEWS:
                    continue  # 중복 뉴스 스킵

                short_url = shorten_url(link)
                message = f"📰 [{keyword}] {title}\n{short_url}"
                bot.send_message(chat_id=CHAT_ID, text=message)
                SENT_NEWS.add(link)

        except Exception as e:
            print(f"뉴스 수집 오류 ({keyword}): {e}")

# 서버 활성화
keep_alive()

# 루프 실행
while True:
    get_news()
    time.sleep(60)  # 10분마다 실행
