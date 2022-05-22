import pymysql
import requests as rq
from bs4 import BeautifulSoup


def open_db():
    conn = pymysql.connect(host='localhost', user='user',
                           password='password', db='naverMovie')

    cur = conn.cursor(pymysql.cursors.DictCursor)

    return conn, cur


def movieCrawling():
    conn, cur = open_db()

    url = "https://movie.naver.com/movie/running/current.naver"
    soup = BeautifulSoup(urllib.request.urlopen(url).read(), 'html.parser')

    data = soup.select(
        '#content > div.article > div.obj_section > div.lst_wrap > ul > li')

    cnt = 0

    for tempData in data:
        cnt += 1

        # 1. title: 영화 제목
        titleData = tempData.select_one('dl > dt > a')
        title = titleData.string

        # 2. movie_rate: 영화 등급
        movie_rateData = tempData.select_one('dl > dt > span')
        if movie_rateData is not None:
            movie_rate = movie_rateData.string
        else:
            movie_rate = None  # null로 넣기

        # 3. netixen_rate: 네티즌 평점
        netizen_rateData = tempData.select_one(
            'dl > dd.star > dl > dd:nth-child(2) > div > a > span.num')
        if netizen_rateData is not None:
            netizen_rate = float(netizen_rateData.string)
        else:
            netizen_rate = None  # null로 넣기

        # 4. netizen_count: 네티즌 평점 참여자 수
        netizen_count = tempData.select_one(
            'dl > dd.star > dl > dd > div > a > span.num2 > em')
        if netizen_count is not None:
            temp = netizen_count.string
            netizen_count = temp.replace(",", "")
        else:
            netizen_count = 0  # 네티즌 평점이 null인 경우 _ 참여자 0명

        # 5. journalist_score: 기자 평론가 평점
        journalist_scoreData = tempData.select_one(
            'dl > dd.star > dl > dd:nth-child(4) > div > a > span.num')
        if journalist_scoreData is not None:
            journalist_score = float(journalist_scoreData.string)
        else:
            journalist_score = None  # null로 넣기

        # 6. journalist_count: 기자 평론가 참여자 수
        journalist_count = tempData.select_one(
            'dl > dd.star > dl > dd:nth-child(4) > div.star_t1 > a > span.num2 > em')
        if journalist_count is not None:
            temp = journalist_count.string
            journalist_count = temp.replace(",", "")
        else:
            journalist_count = 0  # 기자 평론가 평점이 null인 경우 _ 참여자 0명

        # 7. scope: 개요
        scope = ""
        scopeList = tempData.select(
            'dl > dd:nth-child(3) > dl > dd:nth-child(2) > span.link_txt > a')
        if scopeList is not None:
            for temp in scopeList:
                scope += temp.string + ", "
            scope = scope[:-2]
        else:
            scope = None  # null로 넣기

        # 8. playing_time: 상영 시간
        playing_timeData = tempData.select_one(
            'dl > dd:nth-child(3) > dl > dd:nth-child(2)')
        count = 0
        playing_time = int(list(playing_timeData)[4].string.strip()[:-1])

        # 9. opening_date: 개봉 날짜
        opening_dateData = tempData.select_one(
            'dl > dd:nth-child(3) > dl > dd:nth-child(2)')
        opening_date = list(opening_dateData)[6].string.strip()[:-3]

        # 10. director: 감독
        director = ""
        directorList = tempData.select(
            'dl > dd:nth-child(3) > dl > dd:nth-child(4) > span > a')
        if directorList is not None:
            for temp in directorList:
                director += temp.string + ", "
            director = director[:-2]
        else:
            director = None  # null로 넣기

        # 11. image: 영화 대표 이미지 주소
        image = tempData.select(
            'div > a > img')[0]['src']

        insert_sql = """
            insert into movie(title, movie_rate, netizen_rate, netizen_count, journalist_score, journalist_count, scope, playing_time, opening_date, director, image)
            values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        cur.execute(insert_sql, (title, movie_rate, netizen_rate, netizen_count,
                    journalist_score, journalist_count, scope, playing_time, opening_date, director, image))
        conn.commit()

    driver.close()
    driver.quit()

    close_db(conn, cur)


def close_db(conn, cur):
    cur.close()
    conn.close()


if __name__ == '__main__':
    movieCrawling()
