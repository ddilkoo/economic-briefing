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

NAVER_URL = "https://finance.naver.com/news/mainnews.naver"


# =====================
# 뉴스 수집
# =====================

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


    return news[:50]



# =====================
# Gemini 경제 브리핑
# =====================

def make_briefing(news):


    news_text = "\n".join(
        f"- {item}"
        for item in news
    )


    prompt = f"""

너는 한국 경제 전문 애널리스트다.

아래 뉴스 목록을 기반으로
매일 아침 투자자가 읽는 경제 브리핑을 작성해라.


작성 목적:
- 5분 안에 오늘 경제 흐름 파악
- 중요한 변화만 전달
- 불필요한 뉴스 나열 금지


작성 규칙:

1. 뉴스 제목을 그대로 나열하지 말 것
2. 비슷한 뉴스는 하나의 이슈로 묶을 것
3. 각 항목은 2~3줄 이내로 작성
4. 시장 영향 또는 투자자가 봐야 할 부분 포함
5. 사회/연예/광고성 뉴스 제외
6. 전체 길이는 A4 한 장 이내


반드시 아래 형식 유지:


📊 오늘의 경제 브리핑


🌎 글로벌 경제

- 미국, 중국 등 글로벌 시장 주요 흐름
- 한국 시장 영향


💰 금리·환율

- 금리 방향
- 원달러 환율 및 금융시장 영향


📈 국내 증시

- 코스피·코스닥 흐름
- 주요 업종 및 투자 포인트


🏢 기업 주요 이슈

- 반도체, 자동차 등 주요 산업
- 기업 관련 핵심 내용


🏠 부동산

- 정책, 금리, 거래 흐름


⚠️ 오늘 체크 포인트

• 시장 위험 요소
• 투자자가 확인할 변수


💡 한 줄 정리

오늘 시장의 핵심 방향을 한 문장으로 정리


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

    # Discord 메시지 제한 고려
    max_length = 1900


    if len(message) > max_length:
        message = message[:max_length] + "\n\n(내용 일부 생략)"


    requests.post(
        DISCORD_WEBHOOK,
        json={
            "content": message
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
        "📢 오늘 수집된 경제 뉴스가 없습니다."
    )
