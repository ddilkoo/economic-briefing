import requests
from bs4 import BeautifulSoup
import re


# 내가 관심 있는 분야
KEYWORDS = [
    "금리",
    "기준금리",
    "한국은행",
    "연준",
    "미국 금리",
    "환율",
    "달러",
    "원달러",
    "부동산",
    "아파트",
    "주택",
    "전세",
    "증시",
    "코스피",
    "코스닥",
    "나스닥",
    "반도체",
    "삼성전자",
    "하이닉스"
]


DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1534793981769027594/1JxOyILur5MJen6gw4PWgkG-kmTZo8lLrK4uDRIDmvd-_L3oqx7UrRwAqBE4QUL_7DmH"


# 네이버증권 주요뉴스
NAVER_URL = "https://finance.naver.com/news/mainnews.naver"


def clean_text(text):
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def get_news():

    headers = {
        "User-Agent": 
        "Mozilla/5.0"
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


    news_list = []


    # 뉴스 제목 영역 추출
    articles = soup.select(
        "dd.articleSubject a"
    )


    for article in articles:

        title = clean_text(
            article.text
        )

        link = (
            "https://finance.naver.com"
            + article.get("href")
        )


        # 관심 키워드 검사
        if any(
            keyword in title
            for keyword in KEYWORDS
        ):

            news_list.append(
                {
                    "title": title,
                    "link": link
                }
            )


    return news_list[:10]



def send_discord(news):

    message = (
        "📊 오늘의 경제 브리핑\n\n"
    )


    if not news:

        message += (
            "오늘 관심 분야 뉴스가 없습니다."
        )

    else:

        for idx, item in enumerate(news, 1):

            message += (
                f"{idx}. {item['title']}\n"
            )

            message += (
                f"{item['link']}\n\n"
            )


    requests.post(
        DISCORD_WEBHOOK,
        json={
            "content": message[:1900]
        }
    )



news = get_news()

send_discord(news)
