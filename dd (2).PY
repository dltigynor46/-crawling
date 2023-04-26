import requests
from bs4 import BeautifulSoup
import mysql.connector
import schedule
import time

# DB 접속 설정
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='password',
    database='mydatabase'
)

# 검색어로 상품 검색 후 결과 반환하는 함수
def search_product(site, keyword):
    if site == 'naver':
        url = f'https://search.shopping.naver.com/search/all?query={keyword}'
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'lxml')

        naver_items = soup.find_all('div', attrs={'class': 'basicList_inner__eY_mq'})
        results = []
        for item in naver_items:
            name = item.find('a', attrs={'class': 'basicList_link__1MaTN'}).text
            price = item.find('span', attrs={'class': 'price_num__2WUXn'}).text
            rating = item.find('em', attrs={'class': 'basicList_star__3ARtR'}).text
            results.append({
                'name': name,
                'price': price,
                'rating': rating
            })
        return results
    elif site == 'coupang':
        url = f'https://www.coupang.com/np/search?q={keyword}'
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'lxml')

        coupang_items = soup.find_all('li', attrs={'class': 'search-product'})
        results = []
        for item in coupang_items:
            name = item.find('div', attrs={'class': 'name'}).text
            price = item.find('strong', attrs={'class': 'price-value'}).text
            rating = item.find('span', attrs={'class': 'rating-total-count'}).text
            results.append({
                'name': name,
                'price': price,
                'rating': rating
            })
        return results

# DB에 저장된 상품코드를 이용하여 쿠팡과 네이버에서 검색하고, 검색 결과를 DB에 저장하는 함수
def search_products():
    # DB에서 상품코드 가져오기
    cursor = conn.cursor()
    cursor.execute('SELECT code FROM products')
    rows = cursor.fetchall()

    for row in rows:
        code = row[0]
        # 네이버에서 상품 검색
        naver_result = search_product('naver', code)
        # 쿠팡에서 상품 검색
        coupang_result = search_product('coupang', code)

        # 검색 결과 DB에 저장
        for item in naver_result:
            name = item['name']
            price = item['price']
            rating = item['rating']
            # 추출한 정보를 DB에 저장
            cursor = conn.cursor()
            cursor.execute("INSERT INTO products (name, price, rating, site) VALUES (%s, %s, %s, 'naver')",
