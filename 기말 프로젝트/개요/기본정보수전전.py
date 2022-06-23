import pymysql
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import re

options = webdriver.ChromeOptions()
options.add_argument("headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.implicitly_wait(3)
"""
conn = pymysql.connect(host='localhost', user='ro-el-c',
                       password='password', db='test')
cur = conn.cursor()
"""
movie=[]
for i in range(1, 41):
    url = "https://movie.naver.com/movie/sdb/rank/rmovie.naver?sel=pnt&date=20220603&page=" + str(i)
    soup = BeautifulSoup(requests.get(url).content, 'html.parser')

    data = soup.select('#old_content > table > tbody > tr')

    j = 1
    for tempData in data:
        checkNone = tempData.select_one("td")['class'][0]
        if checkNone == "blank01" or checkNone == "line01":
            continue

        print("{0} page, {1} 번째 영화. total: {2}".format(i, j, 50 * (i - 1) + j))

        # 영화 번호
        mcode = int(tempData.select_one('td.title > div.tit5 > a')['href'].split("=")[1])
        print("movieCode:", mcode)

        movieDetail = requests.get("https://movie.naver.com/movie/bi/mi/basic.naver?code=" + str(mcode))
        movieDetailPage = BeautifulSoup(movieDetail.content, 'html.parser')

        basicData = movieDetailPage.select_one("#content > div.article > div.mv_info_area > div.mv_info")

        # 영화 제목
        title = basicData.select_one("h3 > a").string
        print("title:", title)

        # 영화 부제목
        subtitle = basicData.select_one("strong")['title']
        #print("subtitle:", subtitle)

        # 장르
        genre = []
        genreData = basicData.select("dl > dd:nth-child(2) > p > span:nth-child(1) > a")
        for tempGenre in genreData:
            genreToStr = tempGenre.string
            genreOne = (mcode, genreToStr)
            genre.append(genreOne)
        print("{0}개 genre:".format(len(genreData)))
        for tempData in genre:
            print(tempData)

        # 나라
        nation = []
        nationData = basicData.select("dl > dd:nth-child(2) > p > span:nth-child(2) > a")
        for tempNation in nationData:
            nationToStr = tempNation.string
            nationOne = (mcode, nationToStr)
            nation.append(nationOne)
        print("{0}개 nation:".format(len(nationData)))
        for tempData in nation:
            print(tempData)

        # 상영 시간
        playing_time = int(basicData.select_one("dl > dd:nth-child(2) > p > span:nth-child(3)").string.strip()[:-1])
        #print("playing_time:", playing_time)

        # 개봉 날짜
        opening_date = []
        opening_dateData = basicData.select("dl > dd:nth-child(2) > p > span:nth-child(4)")
        if opening_dateData is None:
            opening_date = None
        else:
            opening_dateData = list(opening_dateData)
            waitdata = ""
            opening_dateVal = ""
            for yearandday in opening_dateData:
                yearandday = list(yearandday)
                k = 0
                for tempData in yearandday:
                    yndDataToStr = tempData.string.replace("[", "").replace("]", "")
                    yndDataToStr = yndDataToStr.replace("\r", "").replace("\n", "").replace("\t", "")
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
        print("opening_date:")
        for tempData in opening_date:
            print(tempData)

        # 누적 관객수
        sum_audiData = basicData.select_one("dl > dd:nth-child(10) > div > p")
        if sum_audiData is None:
            sum_audi = None
        else:
            sum_audi = int(list(sum_audiData)[0].string.replace(",", "").strip()[:-1])
        #print("sum_audi:", sum_audi)

        # 관람가 등급
        movie_rate = []
        rateData = basicData.select_one("dl > dd:nth-child(8) > p")
        if rateData is None:
            movie_rate = None
        else:
            rateDataList = list(rateData)
            k = 0
            rate_nation = ""
            rate = ""
            for tempData in rateDataList:
                rateDataToStr = tempData.string.replace("[", "").replace("]", "")
                rateDataToStr = rateDataToStr.replace("\r", "").replace("\n", "").replace("\t", "").strip()
                if rateDataToStr[:4] == "N=a:" or rateDataToStr == "도움말" or rateDataToStr == "":
                    continue
                if k % 2 == 0:
                    rate_nation = rateDataToStr
                else:
                    rate = rateDataToStr
                    rateOne = (mcode, rate_nation, rate)
                    movie_rate.append(rateOne)
                k += 1
        print("movie_rate:")
        for tempData in movie_rate:
            print(tempData)

        # 대표 이미지
        mainimgurl = movieDetailPage.select_one("#content > div.article > div.mv_info_area > div.poster > a > img")[
            'src']
        #print("mainimgurl:", mainimgurl)

        # 포토
        photoDetail = requests.get("https://movie.naver.com/movie/bi/mi/photo.naver?code=" + str(mcode) + "#tab")
        photoDetailPage = BeautifulSoup(photoDetail.content, 'html.parser')

        totalPhotoNumTostr = list(photoDetailPage.select_one(
            "#content > div.article > div.obj_section2.noline > div > div.title_area > span.count"))[1]
        totalPhotoNum = int(totalPhotoNumTostr.replace("/", "").strip())
        # print(totalPhotoNum)
        cntPhotoNum = 0

        photo = []
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
        # print(len(photo))
        print("photo:")
        for tempData in photo:
            print(tempData)


        #print()
        #print("관람객, 네티즌, 기자/평론가 평점")
        #print()
        # 평점
        """ 평점

            - 관람객 평점
            - 관람객 참여수
            - 네티즌 평점
            - 네티즌 참여수
            - 평론가 평점
            - 평론가 참여수
        """
        rateDetail = requests.get("https://movie.naver.com/movie/bi/mi/point.naver?code=" + str(mcode))
        rateDetailPage = BeautifulSoup(rateDetail.content, 'html.parser')


        # 관람객 평점
        viewer_rateData = rateDetailPage.select("#actual_point_tab_inner > div > em")
        if len(viewer_rateData) > 0 and viewer_rateData is not None:
            viewer_rate = ""
            for tempData in viewer_rateData:
                viewer_rate += tempData.string
        else:
            viewer_rate = None
        #print("viewer_rate:", viewer_rate)

        # 관람객 참여수
        viewer_cntData = rateDetailPage.select_one("#actual_point_tab_inner > span > em")
        if viewer_cntData is not None:
            viewer_cnt = viewer_cntData.string.replace(",", "")
        else:
            viewer_cnt = None
        #print("viewer_cnt:", viewer_cnt)

        # 네티즌 평점
        ntz_rateData = rateDetailPage.select("#netizen_point_tab_inner > em")
        if len(ntz_rateData) > 0 and ntz_rateData is not None:
            ntz_rate = ""
            for tempData in ntz_rateData:
                ntz_rate += tempData.string
        else:
            ntz_rate = None
        #print("ntz_rate:", ntz_rate)

        # 네티즌 참여수
        ntz_cntData = rateDetailPage.select_one(
            "#graph_area > div.grade_netizen > div.title_area.grade_tit > div.sc_area > span > em")
        if ntz_cntData is not None:
            ntz_cnt = ntz_cntData.string.replace(",", "")
        else:
            ntz_cnt = None
        #print("ntz_cnt:", ntz_cnt)

        # 평론가 평점
        jour_rateData = rateDetailPage.select(
            "#content > div.article > div.section_group.section_group_frst > div:nth-child(6) > div > div.title_area > div > em")
        if len(jour_rateData) > 0 and jour_rateData is not None:
            jour_rate = ""
            for tempData in jour_rateData:
                jour_rate += tempData.string
        else:
            jour_rate = None
        #print("jour_rate:", jour_rate)

        # 평론가 참여수
        jour_cntData = rateDetailPage.select_one(
            "#content > div.article > div.section_group.section_group_frst > div:nth-child(6) > div > div.title_area > span > em")
        if jour_cntData is not None:
            jour_cnt = jour_cntData.string.replace(",", "")
        else:
            jour_cnt = None
        #print("jour_cnt:", jour_cnt)

        """movie table tuple 추가"""
        movieOne = (mcode, title, subtitle, viewer_rate, viewer_cnt, ntz_rate, ntz_cnt, jour_rate, jour_cnt, playing_time, sum_audi, mainimgurl)
        movie.append(movieOne)

        #print()
        #print("관람객, 네티즌, 기자/평론가 평점 - 한 줄 평")
        #print()

        # 평점
        gradeDetail = requests.get("https://movie.naver.com/movie/point/af/list.naver?st=mcode&sword=" + str(mcode) + "&target=after")
        gradeDetailPage = BeautifulSoup(gradeDetail.content, 'html.parser')

        ''' # grade - 평점

            평점 번호 - gno
            영화 코드 - mcode
            평점 - grade
            닉네임 - g_nickname
            내용 - g_content
            작성일 - g_date - datetime
        ㅇ'''

        grade = [] # (g_nickname, mcode, grade, g_content)

        totalgradeNum = 0
        nowgradecnt = 0
        pageNum = 1
        flag = 0

        while(True):
            movieGrade = requests.get("https://movie.naver.com/movie/point/af/list.naver?st=mcode&sword=" + str(mcode) + "&target=after&page=" + str(pageNum))
            movieGradePages = BeautifulSoup(movieGrade.content, 'html.parser')
            #print(movieGradePages)

            # 총 평점 수
            if pageNum==1:
                totalgradeNum = int(movieGradePages.select_one("#old_content > h5 > div > strong").string)
                #print()
                #print("--------------------------------------------------------------")
                #print()
                print("totalgradeNum:", totalgradeNum)
                '''print()
                print("--------------------------------------------------------------")
                print()
                print()'''

            gradeTable = movieGradePages.select_one("#old_content > table")

            # 페이지 당 평점 리스트
            gradeList = gradeTable.select("tbody > tr")
            #print(gradeList)

            for gradeTemp in gradeList:
                # 평점
                gradeNum = int(gradeTemp.select_one("td.title > div > em").string)
                #print("gradeNum:", gradeNum)

                # 닉네임
                g_nickname = gradeTemp.select_one("td:nth-child(3) > a").string
                #print("g_nickname:", g_nickname)

                # 내용
                g_content = list(gradeTemp.select_one("td.title"))[6].replace("\n", "").replace("\t", "").strip()
                #print("g_content:", g_content)

                # 작성일
                g_date = "20" + list(gradeTemp.select_one("td:nth-child(3)"))[2].strip().replace(".", "-")
                #print("g_date:", g_date)

                gradeOne = (mcode, gradeNum, g_nickname, g_content, g_date)
                grade.append(gradeOne)

                nowgradecnt+=1

                '''print()
                print("{0} page, grade count: {1}".format(pageNum, nowgradecnt))
                print()
                print()
                print("--------------------------------------------------------------")
                print()
                print()'''

            print("{0} page, grade count: {1}".format(pageNum, nowgradecnt))
            if pageNum >= 1000:
                break
            if nowgradecnt >= totalgradeNum:
                break
            pageNum += 1

        print("grade 개수:", len(grade))
        for tempData in grade:
            print(tempData)



        '''배우/감독'''

        url = "https://movie.naver.com/movie/bi/mi/detail.naver?code=" + str(mcode)
        driver.get(url)
        try:
            driver.find_element(by=By.XPATH, value="//*[@id='actorMore']").click()
        except:
            pass

        movieActorPage = BeautifulSoup(driver.page_source, 'html.parser')

        # 주조연 배우 - movie_actor, actor
        movie_actor = []  # (mcode, ano, role_ms, role_name)
        actor = []  # (ano, aname, aname_eng, a_imgurl, a_status, a_birth, a_death)

        actorMSList = movieActorPage.select(
            "#content > div.article > div.section_group.section_group_frst > div.obj_section.noline > div > div.lst_people_area.height100 > ul > li")
        # print("주조연:", actorMSList[0])

        for actorTemp in actorMSList:
            # print(actorTemp)
            # 배우 번호
            ano = int(actorTemp.select_one("div.p_info > a")['href'].split("=")[1])
            #print("ano:", ano)

            # 주조연
            role_ms = actorTemp.select_one("div > div > p.in_prt > em").string
            #print("role_ms:", role_ms)

            # 배역 이름
            role_nameData = actorTemp.select_one("div > div > p.pe_cmt > span")
            if role_nameData is not None:
                role_name = role_nameData.string[:-2]
            else:
                role_name = None
            #print("role_name:", role_name)

            '''배우'''

            url = "https://movie.naver.com/movie/bi/pi/basic.naver?code=" + str(ano)
            actorDetailPage = BeautifulSoup(requests.get(url).content, 'html.parser')

            # 배우 이름
            aname = actorDetailPage.select_one("div.mv_info.character > h3 > a").string
            #print("aname:", aname)

            # 배우 이름 eng
            aname_engData = actorDetailPage.select_one("div.mv_info.character > strong")
            if aname_engData is not None and len(aname_engData.string.strip()) != 0:
                aname_eng = aname_engData.string.strip().replace("\r\n\t\t\t\r\n\t\t\t", " ")
            else:
                aname_eng = None
            #print("aname_eng:", aname_eng)

            # 출생
            a_birthData = actorDetailPage.select_one("div.mv_info.character > dl.info_spec > dd")
            a_status = 1
            a_death = None

            if a_birthData is not None and a_birthData.string is not None:
                a_birth = a_birthData.string.split("/")[0].strip().replace(" ", "")
                a_birth = a_birth.replace("년", "-").replace("월", "-").replace("일", "")
                # print("pre a_birth:", a_birth)

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
                        # print("actor died")
                        break

                # 배우 사망 X -> 출생일 insert
                if a_status == 1:
                    if birthFormat.match(a_birth) is None:
                        a_birth = None
                        # print("birth format match fail")
                    '''else:
                        #print("birth format match success")'''

                # 배우 사망시, 별세일 다시 포맷 확인
                elif a_status == 0:
                    a_birthTemp = a_birth
                    a_birth, a_death = a_birthTemp.split("~")
                    #print(a_birth, a_death)
                    if birthFormat.match(a_birth) is None:
                        a_birth = None
                    if birthFormat.match(a_death) is None:
                        a_death = None

            else:  # 생일 data 존재 X
                a_birth = None
                # print("a_birth:", a_birth)

            #print("a_birth:", a_birth, ", a_death:", a_death)
            # print()

            # 배우 사진 url
            a_imgurl = actorDetailPage.select_one("div.poster > img")['src']
            #print("a_imgurl:", a_imgurl)

            m_actorOne = (mcode, ano, role_ms, role_name)
            movie_actor.append(m_actorOne)

            actorOne = (ano, aname, aname_eng, a_imgurl, a_status, a_birth, a_death)
            actor.append(actorOne)

        print("movie_actor:")
        for tempData in movie_actor:
            print(tempData)
        print("actor:")
        for tempData in actor:
            print(tempData)

        ''' 주조연 배우 외 단역, 우정 출연 등 - 일단 생략
        # 그 외 - movie_actor
        actorElseList = actorDetailPage.select("#subActorList > tbody > tr:nth-child(1) > td > span")
        #print("그 외:", actorElseList)
        '''

        # 감독 - movie_director, director _ 감독 번호, 이름, 영화 코드
        movie_director = []  # (mcode, dno)
        director = []  # (dno, dname, dname_eng, d_imgurl)

        directorList = movieActorPage.select("#content > div.article > div.section_group.section_group_frst > div:nth-child(2) > div > div.dir_obj")

        for directorTemp in directorList:
            # print(actorTemp)
            # 감독 번호
            dno = int(directorTemp.select_one("div > a")['href'].split("=")[1])
            #print("dno:", dno)

            # 감독 이름
            dname = directorTemp.select_one("div > a").string
            #print("dname:", dname)

            # 감독 이름 eng
            dname_engData = directorTemp.select_one("div > em.e_name")
            if dname_engData is not None:
                dname_eng = dname_engData.string
            else:
                dname_eng = None
            #print("dname_eng:", dname_eng)

            # 감독 사진
            d_imgurl = directorTemp.select_one("p > a > img")['src']
            #print("d_imgurl:", d_imgurl)

            m_dOne = (mcode, dno)
            dOne = (dno, dname, dname_eng, d_imgurl)

            movie_director.append(m_dOne)
            director.append(dOne)

        print("movie_director:")
        for tempData in movie_director:
            print(tempData)
        print("director:")
        for tempData in director:
            print(tempData)


        # 리뷰
        ''' # review - 리뷰

            리뷰 번호 - rno (PK)
            영화 코드 - mcode (FK)
            닉네임 - r_nickname
            작성일 - r_date
            조회수 - r_view
            제목 - r_title
            내용 - r_content
            추천수 - r_goodcnt
        ㅇ'''

        ''' # review_comment - 리뷰에 달린 댓글

            리뷰 번호 - rno (PK, FK)
            닉네임 - c_nickname
            작성일 - c_date
            내용 - c_content
            추천수 - c_goodcnt
            반대수 - c_badcnt
        ㅇ'''

        totalReview=0
        nowReviewcnt=0
        pageNum=1
        flag=0

        review=[] # (rno, mcode, r_nickname, r_date, r_view, r_title, r_content, r_goodcnt)

        realSaveNum=0

        while(True):
            reviewContainPage = requests.get("https://movie.naver.com/movie/bi/mi/review.naver?code="+str(mcode)+"&page="+str(pageNum))
            reviewListPage = BeautifulSoup(reviewContainPage.content, 'html.parser')
            if pageNum==1:
                totalReview = int(reviewListPage.select_one("#reviewTab > div > div > div.top_behavior > span > em").string)
                print("totalReview:", totalReview)
            reviewList = reviewListPage.select("#reviewTab > div > div > ul > li")
            #print(reviewList)
            for reviewTemp in reviewList:
                strTemp = str(reviewTemp.contents[1]).replace(" ", "").split(";")
                # 리뷰 번호
                #print(strTemp)
                rno = int(strTemp[1].split(">")[0][17:-2])
                #print("rno:", rno)

                reviewDetailPage = requests.get("https://movie.naver.com/movie/bi/mi/reviewread.naver?nid=" + str(rno) + "&code=" + str(mcode) + "&order=#tab")
                reviewData = BeautifulSoup(reviewDetailPage.content, 'html.parser')
                '''
                ㅇ    리뷰 번호 - rno (PK)
                ㅇ    영화 코드 - mcode (FK)
                ㅇ    닉네임 - r_nickName
                ㅇ    작성일 - r_date
                ㅇ    조회수 - r_view
                ㅇ    제목 - r_title
                    내용 - r_content
                ㅇ    추천수 - r_goodcnt
                '''

                basicData = reviewData.select_one("#content > div.article > div.obj_section.noline.center_obj")

                # 닉네임
                r_nicknameData = reviewData.select("div.review > div.board_title > ul > li > a")
                r_nickname=""
                #print(len(r_nicknameData))
                #print(r_nicknameData)
                if len(r_nicknameData) == 2:
                    r_nickname = r_nicknameData[1].select_one("em").string
                else:
                    r_nickname = r_nicknameData[0].select_one("em").string
                #print("r_nickname:", r_nickname)

                # 작성일
                r_date = reviewData.select_one("div.review > div.top_behavior > span").string.replace(".", "-")
                #print("r_date:", r_date)

                # 조회수
                r_view = int(reviewData.select_one("div.review > div.board_title > div > span:nth-child(1) > em").string.replace(",", ""))
                #print("r_view:", r_view)

                # 제목
                r_title = reviewData.select_one("div.review > div.top_behavior > strong").string
                #print("r_title:", r_title)

                # 내용
                #r_contentData = reviewData.select_one("div.review > div.user_tx_area")
                r_contentData = reviewData.select_one("div.review")
                #print(r_contentData)
                contentText = ""
                #print(r_contentData)
                try:
                    for contentTemp in r_contentData:
                        #print(contentTemp.text)
                        contentText += contentTemp.text
                    r_content = contentText
                    print("r_content:", r_content.strip()[:3])
                    realSaveNum += 1
                except:
                    print("오류. 건너뛰기")
                    '''print()
                    print()
                    print("--------------------------------------------------------------")
                    print()
                    print()'''
                    nowReviewcnt += 1
                    continue


                # 추천수
                r_goodcnt = int(reviewData.select_one("#goodReviewCount").string.replace(",", ""))
                #print("r_goodcnt:", r_goodcnt)

                reviewOne = (rno, mcode, r_nickname, r_date, r_view, r_title, r_content, r_goodcnt)
                review.append(reviewOne)

                nowReviewcnt += 1

                """
                if len(review) % 25 == 0:
                    query = "insert into review(rno, mcode, r_nickname, r_date, r_view, r_title, r_content, r_goodcnt) values(%s, %s, %s, %s, %s, %s, %s, %s)"
                    cur.executemany(query, review)
                    conn.commit()
                    review = []"""


                '''print()
                print("{0} page, review count: {1}".format(pageNum, nowReviewcnt))
                print()
                print()
                print("--------------------------------------------------------------")
                print()
                print()'''

            print("{0} page, review count: {1}".format(pageNum, nowReviewcnt))
            if (nowReviewcnt >= totalReview):
                break
            pageNum += 1

        """query = "insert into review(rno, mcode, r_nickname, r_date, r_view, r_title, r_content, r_goodcnt) values(%s, %s, %s, %s, %s, %s, %s, %s)"
        cur.executemany(query, review)
        conn.commit()"""

        print("review 개수:", len(review), ", 실제 저장 개수:", realSaveNum)
        print("review:")
        for dataTemp in review:
            print(dataTemp)


        j += 1
        if j > 50:
            break


        print()
        print()
        print("--------------------------------------------------------------")
        print()
        print()
    print()
    print()
    print("--------------------------------------------------------------")
    print()
    print()

print()
print()
print()
print("--------------------------------------------------------------")
print("--------------------------------------------------------------")
print("-------------------------Crawling End-------------------------")
print("--------------------------------------------------------------")
print("--------------------------------------------------------------")
print()

print("movie: ")
for dataTemp in movie:
    print(dataTemp)
