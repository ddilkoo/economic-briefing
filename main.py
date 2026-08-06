import requests
import feedparser

RSS_URL = "https://news.google.com/rss/search?q=%EA%B2%BD%EC%A0%9C&hl=ko&gl=KR&ceid=KR%3Ako"

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1534793981769027594/1JxOyILur5MJen6gw4PWgkG-kmTZo8lLrK4uDRIDmvd-_L3oqx7UrRwAqBE4QUL_7DmH"


news = feedparser.parse(RSS_URL)

message = "📌 오늘 경제 뉴스\n\n"

for item in news.entries[:5]:
    message += f"• {item.title}\n{item.link}\n\n"


requests.post(
    DISCORD_WEBHOOK,
    json={
        "content": message
    }
)
