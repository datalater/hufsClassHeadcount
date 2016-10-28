import requests
from bs4 import BeautifulSoup

import re

'''
params 옵션

'''

head={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'}
choice_url = "http://webs.hufs.ac.kr:8989/src08/jsp/lecture/LECTURE2020L.jsp"

#테스트: 학부 - 서울 - EICC학과
class parse_headcount():
    def __init__(self):
        self.current_session = requests.session()

        params={
            'tab_lang':'K',
            'type':'',
            'ag_ledg_year':'2016', #년도
            'ag_ledgr_sessn':'3', #1=1학기, 2=여름계절, 3=2학기, 4=겨울계절
            'ag_org_sect':'A', #A=학부, B=대학원, D=통번역대학원, E=교육대학원, G=정치행정언론대학원, H=국제지역대학원, I=경영대학원(주간), J=경영대학원(야간), L=법학전문대학원, M=TESOL대학원, T=TESOL전문교육원
            'campus_sect':'H1', #H1=서울, H2=글로벌
            'gubun':'1', #1=전공/부전공, 2=실용외국어/교양과목
            'ag_crs_strct_cd':'A1CE1_H1', #전공 목록
            'ag_compt_fld_cd':'301_H1' #교양 목록
            }
        
        self.current_session.post(choice_url,data=params,headers=head)
        #self.current_session.get(main_url,headers=head)

        self.timetable = self.current_session.post(choice_url,data=params,headers=head)

        html = BeautifulSoup(self.timetable.text, "html.parser")
        tr_courses = html.find_all("tr", attrs={"height":"55"})
        for tr_course in tr_courses:
            course_area = tr_course.find_all("td")[1].string
            course_year = tr_course.find_all("td")[2].string
            course_number = tr_course.find_all("td")[3].string
            course_name = tr_course.find_all("td")[4].get_text()
            course_name = course_name.replace("\n","")
            
            course_professor = tr_course.find_all("td")[10].get_text()
            course_professor = course_professor.replace("\r","").replace("\t","").replace("\n","")

            course_time = tr_course.find_all("td")[13].get_text()
            cut = course_time.find("(")
            course_time = course_time[:cut-1]

            course_people = tr_course.find_all("td")[14].string
            

            print(course_name,"|",course_professor,"|",course_time,"|",course_people)
        
        

if __name__ == '__main__':
    p = parse_headcount()
    
