import os
import requests
from bs4 import BeautifulSoup
from google import genai


# =====================
# Gemini 설정
# =====================

client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)


DISCORD_WEBHOOK = os.environ["DISCORD_WEBHOOK"]


# =====================
# 네이버증권 뉴스 수집
# =====================

NAVER_URL = "https://finance.naver.com/news/mainnews.naver"


KEYWORDS = [
    "금리",
    "한국은행",
    "연준",
    "환율",
    "달러",
    "원달러",
    "부동산",
    "주택",
    "전세",
    "코스피",
    "코스닥",
    "반도체",
    "삼성전자",
    "하이닉스"
]


def get_news():

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(
        NAVER_URL,
        headers=headers
    )

    response.encoding = "euc-kr"

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )


    articles = soup.select(
        "dd.articleSubject a"
    )


    news = []

    for article in articles:

        title = article.text.strip()

        if any(
            keyword in title
            for keyword in KEYWORDS
        ):
            news.append(title)


    return news[:10]



# =====================
# Gemini 분석
# =====================

def make_briefing(news):

    news_text = "\n".join(news)


    prompt = f"""
너는 한국 경제 전문 애널리스트다.

아래 경제 뉴스 제목을 분석해서
아침 경제 브리핑을 작성해라.

조건:
- 뉴스 제목 나열 금지
- 중요한 이슈만 선정
- 경제적 의미 설명
- 투자자 관점 설명

반드시 포함:

📊 오늘의 경제 브리핑

🔥 핵심 이슈

💰 금리·환율 영향

📈 증시 영향

🏠 부동산 영향


뉴스:
{news_text}
"""


    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )


    return response.text



# =====================
# Discord 전송
# =====================

def send_discord(message):

    requests.post(
        DISCORD_WEBHOOK,
        json={
            "content": message[:1900]
        }
    )



# =====================
# 실행
# =====================

news = get_news()


if news:

    briefing = make_briefing(news)

    send_discord(briefing)

else:

    send_discord(
        "오늘 분석할 경제 뉴스가 없습니다."
    )
