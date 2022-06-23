import pymysql
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import re

conn = pymysql.connect(host='localhost', user='user', password='password', db='navermovie')
cur = conn.cursor()

def put_db(movie, genre, nation, opening_date, movie_rate, photo):
    moviesql = "insert ignore into movie(mcode, title, subtitle, viewer_rate, viewer_cnt, ntz_rate, ntz_cnt, jour_rate, jour_cnt, playing_time, sum_audi, mainimgurl) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    genresql = "insert ignore into genre(mcode, genre) values (%s, %s)"
    nationsql = "insert ignore into nation(mcode, nation) values(%s, %s)"
    opening_datesql = "insert ignore into opening_date(mcode, open_reopen, opening_date) values(%s, %s, %s)"
    movie_ratesql = "insert ignore into rate(mcode, rate_nation, rate) values(%s, %s, %s)"
    photosql = "insert ignore into photo(mcode, photo_src) values(%s, %s)"

    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("!!!!!!!!!!!!!!!!!!!!!!!!! DB 중간 저장 !!!!!!!!!!!!!!!!!!!!!!!!!")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    print(movie)
    cur.executemany(moviesql, movie)
    conn.commit()

    print(genre)
    cur.executemany(genresql, genre)
    conn.commit()

    print(nation)
    cur.executemany(nationsql, nation)
    conn.commit()

    print(opening_date)
    cur.executemany(opening_datesql, opening_date)
    conn.commit()

    print(movie_rate)
    cur.executemany(movie_ratesql, movie_rate)
    conn.commit()

    print(photo)
    cur.executemany(photosql, photo)
    conn.commit()

    movie = []
    genre = []
    nation = []
    opening_date = []
    movie_rate = []
    photo = []

    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("!!!!!!!!!!!!!!!!!!!!!!!!! DB 저장 완료 !!!!!!!!!!!!!!!!!!!!!!!!!")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    print("{0}개 movie:".format(len(movie)))
    print("{0}개 genre:".format(len(genre)))
    print("{0}개 nation:".format(len(nation)))
    print("{0}개 opening_date:".format(len(opening_date)))
    print("{0}개 movie_rate:".format(len(movie_rate)))
    print("{0}개 photo:".format(len(photo)))



movie=[]
genre = []
nation = []
opening_date = []
movie_rate = []
photo = []

realSaveCnt=0

year = 2021
while(year>2009):
    yearurl = "https://movie.naver.com/movie/sdb/browsing/bmovie.naver?open=" + str(year) + "&page="

    for i in range(1,77): # 개봉 년도 2010~2022 중 최대 범위
        print()
        print()
        print("--------------------------------------------------------------")
        print()
        print()
        print("genre:", len(genre))
        print("nation:", len(nation))
        print("opening_date:", len(opening_date))
        print("rate:", len(movie_rate))
        print("photo:", len(photo))
        print()
        print()
        print("--------------------------------------------------------------")
        print()
        print()

        url = yearurl + str(i)
        soup = BeautifulSoup(requests.get(url).content, 'html.parser')

        data = soup.select('#old_content > ul > li > a')

        if i != 1:
            flagurl = yearurl + str(i - 1)
            flagsoup = BeautifulSoup(requests.get(flagurl).content, 'html.parser')
            flagData1 = flagsoup.select_one("#old_content > ul > li:nth-child(1) > a")['href'].split("=")[1]

            flagData2 = soup.select_one("#old_content > ul > li:nth-child(1) > a")['href'].split("=")[1]

            if flagData1 == flagData2:
                print("flagData1: {0}, flagData2: {1}".format(flagData1, flagData2))
                break

        j = 1
        for tempData in data:
            print("{0}년도 / {1} page, {2} 번째 영화. total: {3}".format(year, i, j, 20 * (i - 1) + j))
            print()

            movieDetailPageurl = "https://movie.naver.com" + tempData['href']
            print(movieDetailPageurl)
            movieDetailPage = BeautifulSoup(requests.get(movieDetailPageurl).content, 'html.parser')

            playing_time = None
            sum_audi = None

            # 영화 번호
            mcode = movieDetailPageurl.split("=")[1]
            print("mcode:", mcode)

            try:
                basicData = movieDetailPage.select_one("#content > div.article > div.mv_info_area > div.mv_info")
                testDataNum = len(basicData.select("dl > dd:nth-child(2) > p > span"))
                print("개요 개수:", testDataNum)
                if testDataNum != 4:
                    continue

                # 영화 제목
                title = basicData.select_one("h3 > a").string
                print("title:", title)

                # 영화 부제목
                subtitle = basicData.select_one("strong")['title']
                print("subtitle:", subtitle)

                infoSpecData = basicData.select_one("dl.info_spec")
                infolist = list(infoSpecData)
                print()
                print()

                while len(infolist) > 0:
                    infolistpop = infolist.pop(0)
                    try:
                        tempDataStr = str(infolistpop['class']).replace("\n", "").replace("\t", "").replace("\r","").strip()[2:-2]

                        # step 1
                        # : 장르, 나라, 상영 시간, 개봉 일자
                        if tempDataStr == "step1":
                            print()
                            print("step1: 개요 - 장르, 나라, 상영 시간, 개봉 일자")

                            infolist.pop(0)
                            basicData = infolist.pop(0)

                            # 장르
                            genreData = basicData.select("dd > p > span:nth-child(1) > a")
                            if genreData is not None:
                                for tempGenre in genreData:
                                    genreToStr = tempGenre.string
                                    genreOne = (mcode, genreToStr)
                                    genre.append(genreOne)
                            print("{0}개 genre:".format(len(genre)))
                            for tempData in genre:
                                print(tempData)

                            # 나라
                            nationData = basicData.select("dd > p > span:nth-child(2) > a")
                            if nationData is not None:
                                for tempNation in nationData:
                                    nationToStr = tempNation.string
                                    nationOne = (mcode, nationToStr)
                                    nation.append(nationOne)
                            print()
                            print("{0}개 nation:".format(len(nation)))
                            for tempData in nation:
                                print(tempData)

                            # 상영 시간
                            playing_timeData = basicData.select_one("dd > p > span:nth-child(3)")
                            if playing_timeData is None:
                                playing_time = None
                            else:
                                playing_time = int(playing_timeData.string.strip()[:-1])
                            print()
                            print("playing_time:", playing_time)

                            # 개봉 날짜
                            opening_dateData = basicData.select("dd > p > span:nth-child(4)")
                            if opening_dateData is not None:
                                opening_dateData = list(opening_dateData)
                                waitdata = ""
                                opening_dateVal = ""
                                for yearandday in opening_dateData:
                                    yearandday = list(yearandday)
                                    k = 0
                                    for tempData in yearandday:
                                        yndDataToStr = tempData.string.replace("[", "").replace("]", "")
                                        yndDataToStr = yndDataToStr.replace("\r", "").replace("\n", "").replace("\t",
                                                                                                                "")
                                        yndDataToStr = yndDataToStr.replace(",", "").replace(" ", "").replace(".", "-")

                                        if yndDataToStr[:4] == "N=a:" or yndDataToStr == "":
                                            continue

                                        if k % 3 == 0:
                                            waitdata = yndDataToStr
                                        elif k % 3 == 1:
                                            opening_dateVal = waitdata + yndDataToStr
                                        else:
                                            opening_dateOne = (mcode, yndDataToStr, opening_dateVal)
                                            opening_date.append(opening_dateOne)
                                        k += 1
                            print()
                            print("{0}개 opening_date:".format(len(opening_date)))
                            for tempData in opening_date:
                                print(tempData)

                        # step 9
                        # : 누적 관객수
                        if tempDataStr == "step9":
                            print()
                            print("step9: 흥행 - 누적 관객수")

                            infolist.pop(0)
                            basicData = infolist.pop(0)

                            # 누적 관객수
                            sum_audiData = basicData.select_one("dd > div > p")
                            if sum_audiData is None:
                                sum_audi = None
                            else:
                                sum_audi = int(list(sum_audiData)[0].string.replace(",", "").strip()[:-1])
                            print("sum_audi:", sum_audi)

                        # step 4
                        # : 관람가 등급
                        if tempDataStr == "step4":
                            print()
                            print("step9: 등급 - 관람가 등급")

                            infolist.pop(0)
                            basicData = infolist.pop(0)

                            rateData = basicData.select_one("dd > p")
                            if rateData is not None:
                                rateDataList = list(rateData)
                                k = 0
                                rate_nation = ""
                                rate = ""
                                for tempData in rateDataList:
                                    rateDataToStr = tempData.string.replace("[", "").replace("]", "")
                                    rateDataToStr = rateDataToStr.replace("\r", "").replace("\n", "").replace("\t",
                                                                                                              "").strip()
                                    if rateDataToStr[:4] == "N=a:" or rateDataToStr == "도움말" or rateDataToStr == "":
                                        continue
                                    if k % 2 == 0:
                                        rate_nation = rateDataToStr
                                    else:
                                        rate = rateDataToStr
                                    k += 1
                            else:
                                rate_nation = None
                                rate = None

                            rateOne = (mcode, rate_nation, rate)
                            movie_rate.append(rateOne)

                            print("{0}개 movie_rate:".format(len(movie_rate)))
                            for tempData in movie_rate:
                                print(tempData)

                        else:
                            continue

                    except:
                        continue

                # 대표 이미지
                mainimgurl = movieDetailPage.select_one("#content > div.article > div.mv_info_area > div.poster > a > img")['src']
                print()
                print("mainimgurl:", mainimgurl)

                # 포토
                photoDetail = requests.get(
                    "https://movie.naver.com/movie/bi/mi/photo.naver?code=" + str(mcode) + "#tab")
                photoDetailPage = BeautifulSoup(photoDetail.content, 'html.parser')

                totalPhotoNumTostr = list(photoDetailPage.select_one(
                    "#content > div.article > div.obj_section2.noline > div > div.title_area > span.count"))[1]
                totalPhotoNum = int(totalPhotoNumTostr.replace("/", "").strip())

                cntPhotoNum = 0

                pageNum = 1
                while (True):
                    photoTap = requests.get(
                        "https://movie.naver.com/movie/bi/mi/photo.naver?code=" + str(mcode) + "&page=" + str(
                            pageNum) + "#movieEndTabMenu")
                    photoDetailPage = BeautifulSoup(photoTap.content, 'html.parser')
                    photo_srcData = photoDetailPage.select("#gallery_group > li")
                    for photoTemp in photo_srcData:
                        photo_src = photoTemp.select_one('a > img')['src']
                        if photo_src in photo:
                            continue
                        photo_main = (mcode, photo_src)
                        photo.append(photo_main)

                        cntPhotoNum += 1
                        if cntPhotoNum == totalPhotoNum:
                            break
                    if cntPhotoNum >= totalPhotoNum:
                        break
                    pageNum += 1

                print("{0}개 photo:".format(len(photo)))
                for tempData in photo:
                    print(tempData)

                print()
                print("평점: 관람객, 네티즌, 기자/평론가 평점")
                rateDetail = requests.get("https://movie.naver.com/movie/bi/mi/point.naver?code=" + str(mcode))
                rateDetailPage = BeautifulSoup(rateDetail.content, 'html.parser')

                # 관람객 평점
                viewer_rateData = rateDetailPage.select("#actual_point_tab_inner > div > em")
                if viewer_rateData is None or len(viewer_rateData) < 1:
                    viewer_rate = None
                else:
                    viewer_rate = ""
                    for tempData in viewer_rateData:
                        viewer_rate += tempData.string
                print("viewer_rate:", viewer_rate)

                # 관람객 참여수
                viewer_cntData = rateDetailPage.select_one("#actual_point_tab_inner > span > em")
                if viewer_cntData is not None:
                    viewer_cnt = viewer_cntData.string.replace(",", "")
                else:
                    viewer_cnt = None
                print("viewer_cnt:", viewer_cnt)

                # 네티즌 평점
                ntz_rateData = rateDetailPage.select("#netizen_point_tab_inner > em")
                if ntz_rateData is None or len(ntz_rateData) < 1:
                    ntz_rate = None
                else:
                    ntz_rate = ""
                    for tempData in ntz_rateData:
                        ntz_rate += tempData.string
                print("ntz_rate:", ntz_rate)

                # 네티즌 참여수
                ntz_cntData = rateDetailPage.select_one(
                    "#graph_area > div.grade_netizen > div.title_area.grade_tit > div.sc_area > span > em")
                if ntz_cntData is None:
                    ntz_cnt = None
                else:
                    ntz_cnt = ntz_cntData.string.replace(",", "")
                print("ntz_cnt:", ntz_cnt)

                # 평론가 평점
                jour_rateData = rateDetailPage.select(
                    "#content > div.article > div.section_group.section_group_frst > div:nth-child(6) > div > div.title_area > div > em")
                if jour_rateData is None or len(jour_rateData) < 1:
                    jour_rate = None
                else:
                    jour_rate = ""
                    for tempData in jour_rateData:
                        jour_rate += tempData.string
                print("jour_rate:", jour_rate)

                # 평론가 참여수
                jour_cntData = rateDetailPage.select_one(
                    "#content > div.article > div.section_group.section_group_frst > div:nth-child(6) > div > div.title_area > span > em")
                if jour_cntData is None:
                    jour_cnt = None
                else:
                    jour_cnt = jour_cntData.string.replace(",", "")
                print("jour_cnt:", jour_cnt)

                """movie table tuple 추가"""
                movieOne = (
                mcode, title, subtitle, viewer_rate, viewer_cnt, ntz_rate, ntz_cnt, jour_rate, jour_cnt, playing_time,
                sum_audi, mainimgurl)
                movie.append(movieOne)

                if j%5 == 0:
                    put_db(movie, genre, nation, opening_date, movie_rate, photo)

                j += 1
                realSaveCnt += 1

                print()
                print()
                print("--------------------------------------------------------------")
                print()
                print()

            except:
                print("data 가져올 수 없음. continue")

                if j%5 == 0:
                    put_db(movie, genre, nation, opening_date, movie_rate, photo)

                j += 1
                print()
                print()
                print("--------------------------------------------------------------")
                print()
                print()
                continue
        print()
        print()
        print("--------------------------------------------------------------")
        print()
        print()

    year-=1

print()
print()
print()
print("--------------------------------------------------------------")
print("--------------------------------------------------------------")
print("-------------------------Crawling End-------------------------")
print("--------------------------------------------------------------")
print("--------------------------------------------------------------")
print()

put_db(movie, genre, nation, opening_date, movie_rate, photo)

print("{0} movie: ".format(realSaveCnt))
"""for dataTemp in movie:
    print(dataTemp)"""