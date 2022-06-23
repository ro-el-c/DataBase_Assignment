import pymysql
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import re

conn = pymysql.connect(host='localhost', user='user',
                       password='password', db='navermovie')
cur = conn.cursor(pymysql.cursors.DictCursor)
conn2 = pymysql.connect(host='localhost', user='user',
                       password='password', db='navermovie')
cur2 = conn2.cursor(pymysql.cursors.DictCursor)

options = webdriver.ChromeOptions()
options.add_argument("headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.implicitly_wait(3)

def put_db(actor, movie_actor, director, movie_director):
    actorsql = "insert ignore into actor(ano, aname, aname_eng, a_imgurl, a_status, a_birth, a_death) values(%s, %s, %s, %s, %s, %s, %s)"
    movie_actorsql = "insert ignore into movie_actor(mcode, ano, role_ms, role_name) values(%s, %s, %s, %s)"
    directorsql = "insert ignore into director(dno, dname, dname_eng, d_imgurl) values(%s, %s, %s, %s)"
    movie_directorsql = "insert ignore into movie_director(mcode, dno) values(%s, %s)"

    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("!!!!!!!!!!!!!!!!!!!!!!!!! DB 중간 저장 !!!!!!!!!!!!!!!!!!!!!!!!!")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    print()

    print(actor)
    cur2.executemany(actorsql, actor)
    conn2.commit()

    print()

    print(movie_actor)
    cur2.executemany(movie_actorsql, movie_actor)
    conn2.commit()

    print()

    print(director)
    cur2.executemany(directorsql, director)
    conn2.commit()

    print()

    print(movie_director)
    cur2.executemany(movie_directorsql, movie_director)
    conn2.commit()

    print()

    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("!!!!!!!!!!!!!!!!!!!!!!!!! DB 저장 완료 !!!!!!!!!!!!!!!!!!!!!!!!!")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    """print()

    print("actor:", len(actor))
    print("director:", len(director))
    print("movie_actor:", len(movie_actor))
    print("movie_director:", len(movie_director))"""

actor = []
movie_actor = []
director = []
movie_director = []
count=0

getmcodesql = "select mcode from movie"
cur.execute(getmcodesql)

# 결과 하나씩(tuple) 가져오기
movie_code = cur.fetchone()

while movie_code:
    count+=1
    print("{0} 번째 영화\n".format(count))

    mcode = movie_code['mcode']
    print(mcode)

    movieDetail = requests.get("https://movie.naver.com/movie/bi/mi/basic.naver?code=" + str(mcode))
    movieDetailPage = BeautifulSoup(movieDetail.content, 'html.parser')

    basicData = movieDetailPage.select_one("#content > div.article > div.mv_info_area > div.mv_info")

    # 영화 제목
    title = basicData.select_one("h3 > a").string
    print("title: {0}\n".format(title))

    try:
        '''배우/감독'''

        url = "https://movie.naver.com/movie/bi/mi/detail.naver?code=" + str(mcode)
        driver.get(url)
        try:
            driver.find_element(by=By.XPATH, value="//*[@id='actorMore']").click()
        except:
            pass

        movieActorPage = BeautifulSoup(driver.page_source, 'html.parser')

        # 주조연 배우 - movie_actor, actor

        actorMSList = movieActorPage.select("#content > div.article > div.section_group.section_group_frst > div.obj_section.noline > div > div.lst_people_area.height100 > ul > li")

        for actorTemp in actorMSList:
            # 배우 번호
            ano = int(actorTemp.select_one("div.p_info > a")['href'].split("=")[1])
            print("ano:", ano)

            # 주조연
            role_ms = actorTemp.select_one("div > div > p.in_prt > em").string
            print("role_ms:", role_ms)

            # 배역 이름
            role_nameData = actorTemp.select_one("div > div > p.pe_cmt > span")
            if role_nameData is not None:
                role_name = role_nameData.string[:-2]
            else:
                role_name = None
            print("role_name:", role_name)

            '''배우'''

            url = "https://movie.naver.com/movie/bi/pi/basic.naver?code=" + str(ano)
            actorDetailPage = BeautifulSoup(requests.get(url).content, 'html.parser')

            # 배우 이름
            aname = actorDetailPage.select_one("div.mv_info.character > h3 > a").string
            print("aname:", aname)

            # 배우 이름 eng
            aname_engData = actorDetailPage.select_one("div.mv_info.character > strong")
            if aname_engData is not None and len(aname_engData.string.strip()) != 0:
                aname_eng = aname_engData.string.strip().replace("\r\n\t\t\t\r\n\t\t\t", " ")
            else:
                aname_eng = None
            print("aname_eng:", aname_eng)

            # 출생
            a_birthData = actorDetailPage.select_one("div.mv_info.character > dl.info_spec > dd")
            a_status = 1
            a_death = None

            if a_birthData is not None and a_birthData.string is not None:
                a_birth = a_birthData.string.split("/")[0].strip().replace(" ", "")
                a_birth = a_birth.replace("년", "-").replace("월", "-").replace("일", "")

                dieFormat = [re.compile("^(19[0-9][0-9]|20[0-9][0-9])-~(19[0-9][0-9]|20[0-9][0-9])-$"),
                            re.compile(
                                "^(19[0-9][0-9]|20[0-9][0-9])-~(19[0-9][0-9]|20[0-9][0-9])-([1-9]|0[0-9]|1[0-2])-$"),
                            re.compile(
                                "^(19[0-9][0-9]|20[0-9][0-9])-~(19[0-9][0-9]|20[0-9][0-9])-([1-9]|0[0-9]|1[0-2])-([1-9]|0[1-9]|[1-2][0-9]|3[0-1])$"),
                            re.compile(
                                "^(19[0-9][0-9]|20[0-9][0-9])-([1-9]|0[0-9]|1[0-2])-~(19[0-9][0-9]|20[0-9][0-9])-$"),
                            re.compile(
                                "^(19[0-9][0-9]|20[0-9][0-9])-([1-9]|0[0-9]|1[0-2])-~(19[0-9][0-9]|20[0-9][0-9])-([1-9]|0[0-9]|1[0-2])-$"),
                            re.compile(
                                "^(19[0-9][0-9]|20[0-9][0-9])-([1-9]|0[0-9]|1[0-2])-~(19[0-9][0-9]|20[0-9][0-9])-([1-9]|0[0-9]|1[0-2])-([1-9]|0[1-9]|[1-2][0-9]|3[0-1])$"),
                            re.compile(
                                "^(19[0-9][0-9]|20[0-9][0-9])-([1-9]|0[0-9]|1[0-2])-([1-9]|0[1-9]|[1-2][0-9]|3[0-1])~(19[0-9][0-9]|20[0-9][0-9])-$"),
                            re.compile(
                                "^(19[0-9][0-9]|20[0-9][0-9])-([1-9]|0[0-9]|1[0-2])-([1-9]|0[1-9]|[1-2][0-9]|3[0-1])~(19[0-9][0-9]|20[0-9][0-9])-([1-9]|0[0-9]|1[0-2])-$"),
                            re.compile(
                                "^(19[0-9][0-9]|20[0-9][0-9])-([1-9]|0[0-9]|1[0-2])-([1-9]|0[1-9]|[1-2][0-9]|3[0-1])~(19[0-9][0-9]|20[0-9][0-9])-([1-9]|0[0-9]|1[0-2])-([1-9]|0[1-9]|[1-2][0-9]|3[0-1])$")
                            ]
                birthFormat = re.compile(
                    "^(19[0-9][0-9]|20[0-9][0-9])-([1-9]|0[0-9]|1[0-2])-([1-9]|0[1-9]|[1-2][0-9]|3[0-1])$")

                formatTemp = re.compile("^(19[0-9][0-9]|20[0-9][0-9])-~(19[0-9][0-9]|20[0-9][0-9])-$")

                # 배우 사망 -> 별세 날짜 insert
                for formatTemp in dieFormat:
                    if formatTemp.match(a_birth):
                        a_status = 0
                        print("actor died")
                        break

                # 배우 사망 X -> 출생일 insert
                if a_status == 1:
                    if birthFormat.match(a_birth) is None:
                        a_birth = None
                        print("birth format match fail")

                # 배우 사망시, 별세일 다시 포맷 확인
                elif a_status == 0:
                    a_birthTemp = a_birth
                    a_birth, a_death = a_birthTemp.split("~")
                    if birthFormat.match(a_birth) is None:
                        a_birth = None
                    if birthFormat.match(a_death) is None:
                        a_death = None

            else:  # 생일 data 존재 X
                a_birth = None

            print("a_birth:", a_birth, ", a_death:", a_death)

            # 배우 사진 url
            a_imgurl = actorDetailPage.select_one("div.poster > img")['src']
            print("a_imgurl:", a_imgurl)

            m_actorOne = (mcode, ano, role_ms, role_name)
            movie_actor.append(m_actorOne)

            actorOne = (ano, aname, aname_eng, a_imgurl, a_status, a_birth, a_death)
            actor.append(actorOne)

        print("movie_actor:")
        for tempData in movie_actor:
            print(tempData)
        print()
            
        print("actor:")
        for tempData in actor:
            print(tempData)
        print()

        # 감독 - movie_director, director _ 감독 번호, 이름, 영화 코드

        directorList = movieActorPage.select("#content > div.article > div.section_group.section_group_frst > div:nth-child(2) > div > div.dir_obj")

        for directorTemp in directorList:
            # 감독 번호
            dno = int(directorTemp.select_one("div > a")['href'].split("=")[1])
            print("dno:", dno)

            # 감독 이름
            dname = directorTemp.select_one("div > a").string
            print("dname:", dname)

            # 감독 이름 eng
            dname_engData = directorTemp.select_one("div > em.e_name")
            if dname_engData is not None:
                dname_eng = dname_engData.string
            else:
                dname_eng = None
            print("dname_eng:", dname_eng)

            # 감독 사진
            d_imgurl = directorTemp.select_one("p > a > img")['src']
            print("d_imgurl:", d_imgurl)

            m_dOne = (mcode, dno)
            dOne = (dno, dname, dname_eng, d_imgurl)

            movie_director.append(m_dOne)
            director.append(dOne)

        print("movie_director:")
        for tempData in movie_director:
            print(tempData)
        print()
        print("director:")
        for tempData in director:
            print(tempData)

        print()
        print()
        print("--------------------------------------------------------------")
        print()
        print()

        if count%5 == 0:
            put_db(actor, movie_actor, director, movie_director)

            actor = []
            movie_actor = []
            director = []
            movie_director = []

            print()
            print()
            print("--------------------------------------------------------------")
            print()
            print()

        movie_code = cur.fetchone()
    except:
        print()
        print("--------------------------------------------------------------")
        print("data 가져올 수 없음. continue")
        print("--------------------------------------------------------------")
        print()

        if count%5 == 0:
            put_db(actor, movie_actor, director, movie_director)

            actor = []
            movie_actor = []
            director = []
            movie_director = []

            print()
            print()
            print("--------------------------------------------------------------")
            print()
            print()

        movie_code = cur.fetchone()
        continue


print("--------------------------------------------------------------")
print("--------------------------------------------------------------")
print("-------------------------Crawling End-------------------------")
print("--------------------------------------------------------------")
print("--------------------------------------------------------------")
print()
print()

put_db(actor, movie_actor, director, movie_director)

print()
print()

print("{0} movie".format(count))

