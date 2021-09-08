import requests
from bs4 import BeautifulSoup as bs
from datetime import datetime, timedelta
from collections import Counter # collections의 Counter 객체는 counting hashable container 객체
                                # 빈도 수 계산을 위한 사전형태의 데이터 타입
try:
    import jpype
    import jpype1
except:
    import jpype
from konlpy.utils import pprint
from konlpy.tag import *
from eunjeon import Mecab
import psycopg2

global stop_words
global news_serialNum
global subtitle
try:
    conn = psycopg2.connect(host='localhost', dbname='postgres', user='postgres', password='dlxown0112!', port=5432)
except:
    print("not connect database")    
cur = conn.cursor()

# 불용어 사전 불러오기
with open('stopwords.txt', 'r', encoding = 'utf-8') as file:
    stop_words = []
    line = None    # 변수 line을 None으로 초기화
    while line != '':
        line = file.readline()
        stop_words.append(line.strip('\n'))

# 불용어 사전에 있는 단어 빼고 상위 키워드 리스트 구하기
def get_tags(text, ntags):
    spliter = Mecab() #konlpy의 Mecab 객체
    nouns = spliter.nouns(text) # nouns 함수를 이용해 text에서 명사만 분리(추출)
    count = Counter(nouns) # Counter객체를 생성하고 참조변수 nouns할당 
    keyword_list = [] # 명사 빈도수 저장할 변수
    for n, c in count.most_common(ntags): # most_common 메소드는 정수를 입력받아 객체 안의 명사중 빈도수
        if n not in stop_words:
            data = {'keyword': n, 'count': c}
            keyword_list.append(data)
    return keyword_list # 명사와 사용된 갯수를 keyword_list에 저장

# 시작 날짜와 끝 날짜 사이의 날짜들 구하기
def date_range(start, end): # 시작 날짜와 끝 날짜 사이의 날짜들을 dates 배열에 넣기
    start = datetime.strptime(start, "%Y-%m-%d")
    end = datetime.strptime(end, "%Y-%m-%d")
    dates = [(start + timedelta(days = i)).strftime("%Y%m%d") for i in range((end-start).days+1)]
    return dates

dates = date_range("2018-01-01", "2021-08-31") # 2018년 1월 1일 ~ 2021년 8월 31일

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'}
url = "https://news.daum.net/ranking/popular?regDate="

for current_date in dates:
    res = requests.get(url + current_date, headers = headers)
    if res.status_code == 200:
        print("날짜: ", current_date)

        html = bs(res.text, 'html.parser') # 뷰티플숲 인자값 지정
        news = html.find('ul', {'class': 'list_news2'}) # ul 첫번째 element의 class가 list_news2인 것을 찾음
    
        items = news.findAll('li') # 'li'와 일치하는 모든 것을 리스트 형태로 반환

        for article in items:
            link = article.find('strong', {'class' : 'tit_thumb'}).a

            press = article.find('span', {'class' : 'info_news'}).text # 언론사명
            present_url = link['href'] # 뉴스 링크
            present_res = requests.get(present_url)
            present_html = bs(present_res.text, 'html.parser')
            present_head = present_html.find('div', {'class' : 'head_view'})
            headline = present_head.find('h3', {'class' : 'tit_view'}).text # 뉴스 제목

            try:
                categories = present_html.find('div', {'class' : 'inner_gnb'}).ul
                present_category = categories['data-category'] # 뉴스 카테고리
            except Exception as e:
                present_category = 'no category'
            input_date = present_head.find('span', {'class' : 'num_date'}).text # 입력 날짜
            present_body = present_html.find('div', {'id' : 'mArticle'})
            present_contents = present_html.find('div', {'id' : 'mArticle'})
            content = present_contents.find('div', {'id' : 'harmonyContainer'}).get_text() #뉴스 내용
            news_serialNum_split = present_url.split('/') # url로부터 일련번호를 뽑기 위한 뉴스 링크 파싱
            news_serialNum = news_serialNum_split[-1] #뉴스 일련번호
            
            try: # 부제목은 없는 경우(None) 경우도 있기 때문에 try-catch
                is_subtitle = present_body.find('strong', {'class' : 'summary_view'}).text # 부제목
                subtitle = is_subtitle # 부제목
            except Exception as e:
                subtitle = None 
            
           
            category = ''
            if present_category != 'society' and present_category != 'politics' and present_category != 'economic' and present_category != 'culture' and present_category != 'digital': # 이 외의 카테고리는 '기타'로 처리
                category = 'etc'
            else:
                category = present_category
           
            cur.execute("INSERT INTO news_list (news_date, serial_num, link) VALUES(%s, %s, %s)", (current_date, news_serialNum, present_url)) # news_list 테이블에 삽입
            cur.execute("INSERT INTO news (news_date, serial_num, title, input_date, subtitle, press_agency) VALUES(%s, %s, %s, %s, %s, %s)", (current_date, news_serialNum, headline, input_date, subtitle, press)) # news 테이블에 삽입

            text = headline + content
            keywords = get_tags(text, ntags= 10) # 상위 10개 키워드 리스트
           
            for keyword in keywords:
                cur.execute("INSERT INTO news_category (news_date, serial_num, category, keyword, keyword_count) VALUES(%s, %s, %s, %s, %s)", (current_date, news_serialNum, category, keyword['keyword'], keyword['count'])) # news_category 테이블에 삽입
            
            
             
            conn.commit()

cur.close()
conn.close()
            
                
    
