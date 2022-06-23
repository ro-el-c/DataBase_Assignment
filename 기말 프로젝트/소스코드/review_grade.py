import pymysql
import requests
from bs4 import BeautifulSoup
import re

conn = pymysql.connect(host='localhost', user='user',
                       password='password', db='navermovie')
cur = conn.cursor(pymysql.cursors.DictCursor)
conn2 = pymysql.connect(host='localhost', user='user',
                       password='password', db='navermovie')
cur2 = conn2.cursor(pymysql.cursors.DictCursor)

def put_db(grade, review):
    gradesql = "insert ignore into grade(mcode, g_nickname, grade, g_content, g_date) values(%s, %s, %s, %s, %s)"
    reviewsql = "insert ignore into review(rno, mcode, r_nickname, r_date, r_view, r_title, r_content, r_goodcnt) values(%s, %s, %s, %s, %s, %s, %s, %s)"

    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("!!!!!!!!!!!!!!!!!!!!!!!!! DB 중간 저장 !!!!!!!!!!!!!!!!!!!!!!!!!")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    print()

    if len(grade) > 0:
        print(grade[len(grade)-1]) # db에 넣는 평점 중 마지막 항목 출력
    cur2.executemany(gradesql, grade)
    conn2.commit()

    print()

    if len(review) > 0:
        print(review[len(review)-1]) # db에 넣는 리뷰 중 마지막 항목 출력
    cur2.executemany(reviewsql, review)
    conn2.commit()

    print()

    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("!!!!!!!!!!!!!!!!!!!!!!!!! DB 저장 완료 !!!!!!!!!!!!!!!!!!!!!!!!!")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")


grade = []
review = []
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

    """if mcode == 51022:
        print(count).gitignore
        break

    movie_code = cur.fetchone()"""

    if count < 4046:
        movie_code = cur.fetchone()
        continue

    movieDetail = requests.get("https://movie.naver.com/movie/bi/mi/basic.naver?code=" + str(mcode))
    movieDetailPage = BeautifulSoup(movieDetail.content, 'html.parser')

    basicData = movieDetailPage.select_one("#content > div.article > div.mv_info_area > div.mv_info")

    # 영화 제목
    title = basicData.select_one("h3 > a").string
    print("title: {0}\n".format(title))

    try:
        print()
        print("관람객, 네티즌, 기자/평론가 평점 - 한 줄 평")
        print()

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

        totalgradeNum = 0
        nowgradecnt = 0
        pageNum = 1
        flag = 0

        while (True):
            movieGrade = requests.get("https://movie.naver.com/movie/point/af/list.naver?st=mcode&sword=" + str(mcode) + "&target=after&page=" + str(pageNum))
            movieGradePages = BeautifulSoup(movieGrade.content, 'html.parser')

            # 총 평점 수
            if pageNum == 1:
                totalgradeNum = int(movieGradePages.select_one("#old_content > h5 > div > strong").string)
                print("totalgradeNum:", totalgradeNum)
                print()
                '''print()
                print("--------------------------------------------------------------")
                print()
                print()'''

                # 평점 없는 경우 생략
                if totalgradeNum == 0:
                    break

            gradeTable = movieGradePages.select_one("#old_content > table")

            # 페이지 당 평점 리스트
            gradeList = gradeTable.select("tbody > tr")

            for gradeTemp in gradeList:
                # 평점
                gradeNum = int(gradeTemp.select_one("td.title > div > em").string)
                print("gradeNum:", gradeNum)

                # 닉네임
                g_nickname = gradeTemp.select_one("td:nth-child(3) > a").string
                print("g_nickname:", g_nickname)

                # 내용
                g_content = list(gradeTemp.select_one("td.title"))[6].replace("\n", "").replace("\t", "").strip()
                print("g_content:", g_content)

                # 작성일
                g_date = "20" + list(gradeTemp.select_one("td:nth-child(3)"))[2].strip().replace(".", "-")
                print("g_date:", g_date)

                gradeOne = (mcode, g_nickname, gradeNum, g_content, g_date)
                grade.append(gradeOne)

                nowgradecnt += 1

            print("{0} page, grade count: {1}".format(pageNum, nowgradecnt))
            if pageNum >= 1000:
                break
            if nowgradecnt >= totalgradeNum:
                break
            if nowgradecnt >= 50:
                break
            pageNum += 1

        # 리뷰
        totalReview = 0
        nowReviewcnt = 0
        pageNum = 1
        flag = 0

        realSaveNum = 0

        while (True):
            reviewContainPage = requests.get(
                "https://movie.naver.com/movie/bi/mi/review.naver?code=" + str(mcode) + "&page=" + str(pageNum))
            reviewListPage = BeautifulSoup(reviewContainPage.content, 'html.parser')
            if pageNum == 1:
                totalReview = int(
                    reviewListPage.select_one("#reviewTab > div > div > div.top_behavior > span > em").string)
                print()
                print("totalReview:", totalReview)

            # 리뷰 없는 경우 생략
            if totalReview == 0:
                break

            reviewList = reviewListPage.select("#reviewTab > div > div > ul > li")

            for reviewTemp in reviewList:
                strTemp = str(reviewTemp.contents[1]).replace(" ", "").split(";")
                # 리뷰 번호
                rno = int(strTemp[1].split(">")[0][17:-2])
                print("rno:", rno)

                reviewDetailPage = requests.get("https://movie.naver.com/movie/bi/mi/reviewread.naver?nid=" + str(rno) + "&code=" + str(mcode) + "&order=#tab")
                reviewData = BeautifulSoup(reviewDetailPage.content, 'html.parser')

                basicData = reviewData.select_one("#content > div.article > div.obj_section.noline.center_obj")

                # 닉네임
                r_nicknameData = reviewData.select("div.review > div.board_title > ul > li > a")
                r_nickname = ""
                if len(r_nicknameData) == 2:
                    r_nickname = r_nicknameData[1].select_one("em").string
                else:
                    r_nickname = r_nicknameData[0].select_one("em").string
                print("r_nickname:", r_nickname)

                # 작성일
                r_date = reviewData.select_one("div.review > div.top_behavior > span").string.replace(".", "-")
                print("r_date:", r_date)

                # 조회수
                r_view = int(reviewData.select_one(
                    "div.review > div.board_title > div > span:nth-child(1) > em").string.replace(",", ""))
                print("r_view:", r_view)

                # 제목
                r_title = reviewData.select_one("div.review > div.top_behavior > strong").string
                print("r_title:", r_title)

                # 내용
                r_contentData = reviewData.select_one("div.review")
                contentText = ""
                try:
                    for contentTemp in r_contentData:
                        contentText += contentTemp.text
                    r_content = contentText
                    print()
                    print("r_content:", r_content.strip())
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
                print("r_goodcnt:", r_goodcnt)

                reviewOne = (rno, mcode, r_nickname, r_date, r_view, r_title, r_content, r_goodcnt)
                review.append(reviewOne)

                nowReviewcnt += 1

            print("{0} page, review count: {1}".format(pageNum, nowReviewcnt))
            if (nowReviewcnt >= totalReview):
                break
            if nowReviewcnt >= 20:
                break
            pageNum += 1

        print()
        print("review 개수:", len(review), ", 실제 저장 개수:", realSaveNum)
        print()

        print()
        print()
        print("--------------------------------------------------------------")
        print()
        print()

        if count%5 == 0:
            put_db(grade, review)

            grade = []
            review = []

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
            put_db(grade, review)

            grade = []
            review = []

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

put_db(grade, review)

print()
print()

print("{0} movie".format(count))

