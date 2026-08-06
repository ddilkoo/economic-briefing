import os
import requests
from bs4 import BeautifulSoup
from google import groq
from datetime import datetime


# =====================
# 환경 설정
# =====================

client = genai.Client(
    api_key=os.environ["GROQ_API_KEY"]
)

DISCORD_WEBHOOK = os.environ["DISCORD_WEBHOOK_GROQ"]


# =====================
# 네이버증권 뉴스 페이지
# =====================

NEWS_PAGES = {
    "시황·전망": "https://finance.naver.com/news/news_list.naver?mode=LSS3D&section_id=101&section_id2=258&section_id3=401",

    "기업·종목분석": "https://finance.naver.com/news/news_list.naver?mode=LSS3D&section_id=101&section_id2=258&section_id3=402",

    "해외증시": "https://finance.naver.com/news/news_list.naver?mode=LSS3D&section_id=101&section_id2=258&section_id3=403",

    "채권·선물": "https://finance.naver.com/news/news_list.naver?mode=LSS3D&section_id=101&section_id2=258&section_id3=404",

    "공시·메모": "https://finance.naver.com/news/news_list.naver?mode=LSS3D&section_id=101&section_id2=258&section_id3=406",

    "환율": "https://finance.naver.com/news/news_list.naver?mode=LSS3D&section_id=101&section_id2=258&section_id3=429"
}



# =====================
# 뉴스 수집
# =====================

def get_news():

    all_news = []

    headers = {
        "User-Agent": "Mozilla/5.0"
    }


    for category, url in NEWS_PAGES.items():

        try:

            response = requests.get(
                url,
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


            count = 0


            for article in articles:

                title = article.text.strip()


                if title:

                    all_news.append(
                        f"[{category}] {title}"
                    )

                    count += 1


                if count >= 50:
                    break


        except Exception as e:

            print(
                category,
                "수집 실패:",
                e
            )


    # 중복 제거
    all_news = list(
        dict.fromkeys(all_news)
    )


    return all_news



# =====================
# Gemini 분석
# =====================

def make_briefing(news):


    news_text = "\n".join(
        f"- {item}"
        for item in news
    )


    today = datetime.now().strftime(
        "%Y-%m-%d"
    )


    prompt = f"""

너는 한국 금융시장 전문 애널리스트다.

오늘 날짜:
{today}


아래 뉴스는 네이버증권 6개 분야에서 수집한 금융 뉴스다.


목표:

투자자가 아침 5분 안에 읽고
오늘 시장 방향성을 파악할 수 있는
"종합 경제 브리핑"을 작성한다.


중요 작성 원칙:

- 기사 제목을 그대로 나열하지 않는다.
- 반드시 "무슨 일이 발생했는지 + 시장에 어떤 영향을 주는지" 중심으로 작성한다.
- 사용자가 추가 검색하지 않아도 핵심 내용을 이해할 수 있게 한다.
- 같은 이슈의 여러 뉴스는 하나로 묶는다.
- 중요도가 낮은 기사, 반복 기사, 단순 홍보성 기사는 제외한다.
- 시장 영향력이 큰 순서대로 정리한다.
- 각 항목은 2~3줄 이내로 작성한다.
- 긴 리포트처럼 작성하지 않는다.
- 뉴스 요약이 아니라 투자자 관점의 브리핑으로 작성한다.
- 분야별 적절한 이모티콘을 사용한다.


반드시 아래 형식을 유지한다.


📊 오늘의 종합 경제 브리핑

{today}


🌎 글로벌 시장

미국·중국 등 글로벌 시장 핵심 이슈와
국내 시장 영향 요약


📈 국내 증시

코스피·코스닥 흐름,
주요 업종 및 투자심리 변화


🏢 기업·산업

주요 기업,
실적,
산업 변화 관련 핵심 내용


💵 금융시장

금리,
채권,
선물시장 변화와 영향


💱 환율

원달러 환율,
외국인 수급,
외환시장 영향


📌 주요 공시

시장 영향력이 있는 기업 공시만 정리


⚠️ 오늘 체크 포인트

• 투자자가 확인해야 할 변수
• 시장 리스크


💡 투자자 시각

긍정 요인:
-

주의 요인:
-


한 줄 판단:
오늘 시장에서 가장 중요한 변수는 ○○이다.


분석 대상 뉴스:


{news_text}

"""


response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ],
    temperature=0.4
)

return response.choices[0].message.content



# =====================
# Discord 전송
# =====================

def send_discord(message):

    limit = 1900


    if len(message) > limit:

        message = (
            message[:limit]
            +
            "\n\n(분량 제한으로 일부 생략)"
        )


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
        "📢 오늘 수집된 금융 뉴스가 없습니다."
    )
