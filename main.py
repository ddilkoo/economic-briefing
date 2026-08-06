import requests
import feedparser


RSS_URLS = [
    ("🇰🇷 국내 경제", "https://news.google.com/rss/search?q=한국경제"),
    ("🇺🇸 해외 경제", "https://news.google.com/rss/search?q=미국경제"),
    ("💱 금융시장", "https://news.google.com/rss/search?q=환율+금리"),
    ("🏠 부동산", "https://news.google.com/rss/search?q=부동산+정책"),
]

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1534793981769027594/1JxOyILur5MJen6gw4PWgkG-kmTZo8lLrK4uDRIDmvd-_L3oqx7UrRwAqBE4QUL_7DmH"


message = "📊 오늘의 경제 브리핑\n\n"


for category, url in RSS_URLS:

    news = feedparser.parse(url)

    message += f"{category}\n\n"

    for item in news.entries[:3]:

        title = item.title

        # 뉴스 설명 가져오기
        summary = ""

        if "summary" in item:
            summary = item.summary

        # 너무 긴 내용 자르기
        summary = summary[:200]

        message += f"■ {title}\n"
        message += f"{summary}\n\n"

    message += "--------------------\n"


requests.post(
    DISCORD_WEBHOOK,
    json={
        "content": message[:1900]
    }
)
