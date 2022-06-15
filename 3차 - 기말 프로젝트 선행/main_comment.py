import pymysql
import requests as rq
from bs4 import BeautifulSoup

# db 연결


def open_db():
    conn = pymysql.connect(host='localhost', user='user',
                           password='password', db='naverMovie')

    cur = conn.cursor(pymysql.cursors.DictCursor)

    return conn, cur


# 네이버 현재 상영 영화 정보 크롤링 함수
def movieCrawling():
    conn, cur = open_db()

    # 네이버 현재 상영 영화 페이지 url
    url = "https://movie.naver.com/movie/running/current.naver"
    # BeautifulSoup 사용하여 위 url 페이지의 정보 읽어오기
    soup = BeautifulSoup(urllib.request.urlopen(url).read(), 'html.parser')

    # 현재 상영 영화 페이지의 각 영화 정보 가져오기
    data = soup.select(
        '#content > div.article > div.obj_section > div.lst_wrap > ul > li')

    cnt = 0

    # 각 영화에 대하여 11개 애트리뷰트 값 추출
    for tempData in data:
        cnt += 1

        # 프로그램 실행 시 터미널에서의 결과 확인을 위한 출력
        print("{0} 번째 영화 :".format(cnt))
        print()

        # 1. title: 영화 제목
        titleData = tempData.select_one('dl > dt > a')
        title = titleData.string
        print("title:", title)

        # 2. movie_rate: 영화 등급
        movie_rateData = tempData.select_one('dl > dt > span')
        if movie_rateData is not None:
            movie_rate = movie_rateData.string
        else:
            # 영화 등급 데이터가 존재하지 않는 경우
            movie_rate = None  # null로 넣기
        print("movie_rate:", movie_rate)

        # 3. netixen_rate: 네티즌 평점
        netizen_rateData = tempData.select_one(
            'dl > dd.star > dl > dd:nth-child(2) > div > a > span.num')
        if netizen_rateData is not None:
            netizen_rate = float(netizen_rateData.string)
        else:
            # 네티즌 평점 데이터가 존재하지 않는 경우
            netizen_rate = None  # null로 넣기
        print("netizen_rate:", netizen_rate)

        # 4. netizen_count: 네티즌 평점 참여자 수
        netizen_count = tempData.select_one(
            'dl > dd.star > dl > dd > div > a > span.num2 > em')
        if netizen_count is not None:
            temp = netizen_count.string
            netizen_count = temp.replace(",", "")
        else:
            # 네티즌 평점 참여자 수 데이터가 존재하지 않는 경우
            netizen_count = 0  # 네티즌 평점이 null인 경우 _ 참여자 0명
        print("netizen_count:", netizen_count)

        # 5. journalist_score: 기자 평론가 평점
        journalist_scoreData = tempData.select_one(
            'dl > dd.star > dl > dd:nth-child(4) > div > a > span.num')
        if journalist_scoreData is not None:
            journalist_score = float(journalist_scoreData.string)
        else:
            # 기자평론가 평점 데이터가 존재하지 않는 경우
            journalist_score = None  # null로 넣기
        print("journalist_score:", journalist_score)

        # 6. journalist_count: 기자 평론가 참여자 수
        journalist_count = tempData.select_one(
            'dl > dd.star > dl > dd:nth-child(4) > div.star_t1 > a > span.num2 > em')
        if journalist_count is not None:
            temp = journalist_count.string
            journalist_count = temp.replace(",", "")
        else:
            # 기자평론자 참여자 수 데이터가 존재하지 않는 경우
            journalist_count = 0  # 기자 평론가 평점이 null인 경우 _ 참여자 0명
        print("journalist_count:", journalist_count)

        # 7. scope: 개요
        scope = ""
        scopeList = tempData.select(
            'dl > dd:nth-child(3) > dl > dd:nth-child(2) > span.link_txt > a')
        if scopeList is not None:
            for temp in scopeList:
                scope += temp.string + ", "
            scope = scope[:-2]
        else:
            # 개요 데이터가 존재하지 않는 경우
            scope = None  # null로 넣기
        print("scope:", scope)

        # 8. playing_time: 상영 시간
        playing_timeData = tempData.select_one(
            'dl > dd:nth-child(3) > dl > dd:nth-child(2)')
        count = 0
        playing_time = int(list(playing_timeData)[4].string.strip()[:-1])
        print("playing_time:", playing_time)

        # 9. opening_date: 개봉 날짜
        opening_dateData = tempData.select_one(
            'dl > dd:nth-child(3) > dl > dd:nth-child(2)')
        opening_date = list(opening_dateData)[6].string.strip()[:-3]
        print("opening_date:", opening_date)

        # 10. director: 감독
        director = ""
        directorList = tempData.select(
            'dl > dd:nth-child(3) > dl > dd:nth-child(4) > span > a')
        if directorList is not None:
            for temp in directorList:
                director += temp.string + ", "
            director = director[:-2]
        else:
            # 감독 데이터가 존재하지 않는 경우
            director = None  # null로 넣기
        print("director:", director)

        # 11. image: 영화 대표 이미지 주소
        image = tempData.select(
            'div > a > img')[0]['src']
        print(image)

        # 터미널에 데이터 출력시 영화 간 구분
        print()
        print()
        print("--------------------------------------------------------------")
        print()
        print()

        # movie 테이블에 추출한 값을 넣는 insert문
        insert_sql = """
            insert into movie(title, movie_rate, netizen_rate, netizen_count, journalist_score, journalist_count, scope, playing_time, opening_date, director, image)
            values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        # sql 문 수행, 각 데이터 매칭
        cur.execute(insert_sql, (title, movie_rate, netizen_rate, netizen_count,
                    journalist_score, journalist_count, scope, playing_time, opening_date, director, image))
        # 결과 반영
        conn.commit()

    driver.close()
    driver.quit()

    close_db(conn, cur)

# db 연결 닫기


def close_db(conn, cur):
    cur.close()
    conn.close()


# main 에서 크롤링 함수 실행
if __name__ == '__main__':
    movieCrawling()