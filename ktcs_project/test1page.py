import requests
from bs4 import BeautifulSoup as bs
from collections import Counter
try:
    import jpype
    import jpype1
except:
    import jpype
from konlpy.utils import pprint
from konlpy.tag import *
from konlpy.tag import Komoran
from eunjeon import Mecab 
#mecab = Mecab(dicpath='C:/mecab/mecab-ko-dic') 

global stop_words
# 불용어 사전 불러오기
with open('stopwords.txt', 'r', encoding = 'utf-8') as file:
    stop_words = []
    line = None    # 변수 line을 None으로 초기화
    while line != '':
        line = file.readline()
        stop_words.append(line.strip('\n'))
    #print(stop_words)  

def get_tags(text, ntags= 10):
    spliter = Mecab() #konlpy의 Mecab 객체
    try:
        nouns = spliter.nouns(text) # nouns 함수를 이용해 text에서 명사만 분리(추출)
        count = Counter(nouns) # Counter객체를 생성하고 참조변수 nouns할당
        keyword_list = [] # 명사 빈도수 저장할 변수
        for n, c in count.most_common(ntags): # 정수를 입력받아 객체 안의 명사중 빈도수 ntags인만큼인 것을 저장
            if n not in stop_words:
                data = {'keyword': n, 'count': c}
                keyword_list.append(data)
                
        return keyword_list 
    except Exception as e:
        return None



headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'}
url = "https://news.v.daum.net/v/20201023123039594"

res = requests.get(url, headers = headers)
if res.status_code == 200:

    present_html = bs(res.text, 'html.parser') # 뷰티플숲 인자값 지정
    present_head = present_html.find('div', {'class' : 'head_view'})
    headline = present_head.find('h3', {'class' : 'tit_view'}).text # 뉴스 제목
    present_contents = present_html.find('div', {'id' : 'mArticle'})
    content = present_contents.find('div', {'id' : 'harmonyContainer'}).get_text() #뉴스 내용
    categories = present_html.find('div', {'class' : 'inner_gnb'}).ul
    try:
        present_category = categories['data-category'] # 뉴스 카테고리
    except Exception as e:
        present_category = 'etc'
    present_res = requests.get(url)
    resent_html = bs(present_res.text, 'html.parser')
    

    print(get_tags((headline + content), ntags = 10)) #Komoran 경우 replace('\n', '') 필요
    print(present_category)
    #print(get_tags("서울에서 비가 내립니다.", ntags = 50))