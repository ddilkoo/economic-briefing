import os
import requests
from bs4 import BeautifulSoup
from google import genai


# =====================
# 환경 설정
# =====================

client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)

DISCORD_WEBHOOK = os.environ["DISCORD_WEBHOOK"]


# =====================
# 네이버증권 주요뉴스 수집
# =====================

NAVER_URL = "https://finance.naver.com/news/mainnews.naver"


def get_news():

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(
        NAVER_URL,
        headers=headers,
        timeout=10
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

        if title:
            news.append(title)


    # 중복 제거
    news = list(dict.fromkeys(news))


    # 최대 50개 전달
    return news[:50]



# =====================
# Gemini 경제 분석
# =====================

def make_briefing(news):


    news_text = "\n".join(
        f"- {item}"
        for item in news
    )


    prompt = f"""

너는 한국 경제 전문 애널리스트다.

아래는 오늘 네이버증권 주요뉴스 목록이다.

이 뉴스 전체를 검토해서
투자자가 아침에 읽을 수 있는 경제 브리핑을 작성해라.


작성 기준:

1. 단순 뉴스 제목 나열 금지
2. 중요한 경제 흐름 중심으로 정리
3. 서로 관련된 뉴스는 묶어서 설명
4. 시장 영향까지 설명
5. 불필요한 연예/사회/잡뉴스 제외


반드시 아래 형식으로 작성:


📊 오늘의 경제 브리핑


🔥 핵심 경제 이슈 TOP 5

1.
[이슈 제목]

내용:
-

시장 영향:
-


2.
[이슈 제목]

내용:
-

시장 영향:
-



💰 금리·환율

- 오늘 시장에서 주목할 점


📈 주식시장 영향

- 상승 요인
- 위험 요인


🏠 부동산 영향

- 금리와 정책 관점


✅ 오늘 투자자가 체크할 사항

-


뉴스 목록:

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
        },
        timeout=10
    )



# =====================
# 실행
# =====================

news = get_news()


if news:

    briefing = make_briefing(news)

    send_discord(
        briefing
    )

else:

    send_discord(
        "오늘 수집된 경제 뉴스가 없습니다."
    )
