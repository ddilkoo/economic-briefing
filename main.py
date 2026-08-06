import requests
import feedparser
import re


RSS_URLS = [
    ("📈 한국경제", "https://www.hankyung.com/feed/economy"),
    ("💰 매일경제", "https://www.mk.co.kr/rss/30000001/"),
    ("📰 연합뉴스 경제", "https://www.yna.co.kr/rss/economy.xml"),
]

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1534793981769027594/1JxOyILur5MJen6gw4PWgkG-kmTZo8lLrK4uDRIDmvd-_L3oqx7UrRwAqBE4QUL_7DmH"


def clean_text(text):
    # HTML 태그 제거
    text = re.sub('<[^<]+?>', '', text)

    # 불필요한 공백 제거
    text = text.replace("\n", " ")

    return text.strip()


message = "📊 오늘의 경제 브리핑\n\n"


for category, url in RSS_URLS:

    news = feedparser.parse(url)

    message += f"{category}\n\n"

    for item in news.entries[:3]:

        title = clean_text(item.title)

        summary = ""

        if "summary" in item:
            summary = clean_text(item.summary)

        summary = summary[:250]

        message += f"■ {title}\n"
        
        if summary:
            message += f"{summary}\n\n"
        else:
            message += "내용 미제공\n\n"

    message += "--------------------\n"


requests.post(
    DISCORD_WEBHOOK,
    json={
        "content": message[:1900]
    }
)
