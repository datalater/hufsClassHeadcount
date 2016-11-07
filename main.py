import requests
from bs4 import BeautifulSoup
from datetime import date

import re


#구현되어야 할 기능, 모든 학부 & 교양 데이터 받아오기            [finished] def parsing_all
#전공을 인자로 받아서 전공별로 데이터를 받아오는 기능              [finished] def parsing_major_name
#모델의 검색 시간을 보고 과목 선별적으로 데이터를 받아오는 기능
#
#---------------------------------------------------------------------------------------------------------#
#
# * 코드 로직
# 1) 수업별 현재 인원을 파악하려면 먼저 모든 수업을 조회해야 한다
# 2) 강의시간표는 검색 옵션을 params data에 담고 post로 보내서 결과를 보여준다
# 3) 모든 수업을 조회하려면 params data를 검색 옵션별로 다르게 만들어야 한다
#
#
# * 함수 설명
# __init__(self): 전공 및 교양 목록 데이터 파싱
# parsing_all(self): 학부 내 모든 전공 & 교양 데이터 파싱을 위한 params 생성
# parsing_major_name(self, major_name): 전공이름을 인자로 받아 전공 데이터 파싱을 위한 params 생성
# parsing(self, params): params 데이터를 인자로 받아 데이터 파싱
#
#---------------------------------------------------------------------------------------------------------#


head={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'}
timetable_url = "http://webs.hufs.ac.kr:8989/src08/jsp/lecture/LECTURE2020L.jsp"

class parsing_class():
    def __init__(self):

        ######-----시간표 url의 params 데이터를 실시간으로 반영하는 초기화 함수-----#####
        
        #-----today()로 해당연도, 해당학기 구하기-----#

        now = date.today()

        self.default_year = now.year

        if now.month >=8:
            self.default_session = '3'
        else:
            self.default_session = '1'

        #-----학부, 서울 캠퍼스-----#
        
        self.default_school = 'A' # 학부
        self.default_campus = 'H1' # 서울캠퍼스

        #-----default 옵션을 제외한 나머지 옵션 가져오기-----#

        self.current_session = requests.session()
        
        self.current_session.get(timetable_url,headers=head)
        self.timetable = self.current_session.get(timetable_url,headers=head)
        html = BeautifulSoup(self.timetable.text, "lxml")

        self.gubun_list = ['1','2'] # 1=전공/부전공, 2=실용외국어/교양과목
        self.major_code_list = [] # 전공 코드 목록
        self.liberal_code_list = [] # 교양 코드 목록
        
        liberals = html.find_all("select", attrs={"name":"ag_compt_fld_cd"})
        
        liberals = liberals[0].find_all("option")
        for liberal in liberals:
            self.liberal_code_list.append(liberal['value'])
   
        #-----전공 코드(params 데이터)와 전공명 딕셔너리 만들기-----#

        self.major_dict = dict()
        self.liberal_dict = dict()

        majors = html.find_all("select", attrs={"name":"ag_crs_strct_cd"})
        majors = majors[0].find_all("option")
        liberals = html.find_all("select", attrs={"name":"ag_compt_fld_cd"})
        liberals = liberals[0].find_all("option")

        for major in majors:
            major_name = major.get_text()
            major_name = major_name.replace('\xa0',"").replace('\r','').replace('\n','').replace('\t','')
            cut = major_name.find("-")
            major_name = major_name[cut+1:]
            cut = major_name.find("(")
            major_name = major_name[:cut]

            self.major_dict[major_name] = major['value']

        self.major_key = list(self.major_dict.keys())
        self.major_code_list = list(self.major_dict.values())
        
        for liberal in liberals:
            liberal_name = liberal.get_text()
            liberal_name = liberal_name.replace('\xa0',"").replace('\r','').replace('\n','').replace('\t','')
            cut_count = liberal_name.count("(")
            for i in range(cut_count):
                cut = liberal_name.rfind("(")
                liberal_name = liberal_name[:cut]

            self.liberal_dict[liberal_name] = liberal['value']

        self.liberal_key = list(self.liberal_dict.keys())
        self.liberal_code_list = list(self.liberal_dict.values())

    def parsing_all(self):

        ######-----학부내 모든 전공 및 교양 데이터 파싱-----#####

        #self.current_session = requests.session()

        #-----조회할 데이터 옵션 선택-----#

        self.course_info_list = list()

        for i in range(len(self.gubun_list)):
            if  i == 0:
                for j in range(len(self.major_code_list)):
                    params ={
                        'tab_lang':'K',
                        'type':'',
                        'ag_ledg_year': self.default_year, # 년도
                        'ag_ledgr_sessn': self.default_session, # 1=1학기, 2=여름계절, 3=2학기, 4=겨울계절
                        'ag_org_sect':'A', # A=학부, B=대학원, D=통번역대학원, E=교육대학원, G=정치행정언론대학원, H=국제지역대학원, I=경영대학원(주간), J=경영대학원(야간), L=법학전문대학원, M=TESOL대학원, T=TESOL전문교육원
                        'campus_sect':'H1', # H1=서울, H2=글로벌
                        'gubun': self.gubun_list[i], # 1=전공/부전공, 2=실용외국어/교양과목
                        'ag_crs_strct_cd': self.major_code_list[j], # 전공 목록
                        'ag_compt_fld_cd':'' # 교양 목록
                        }

                    self.major_data = list(self.parsing(params))
            else:
                for k in range(len(self.liberal_code_list)):
                    params ={
                        'tab_lang':'K',
                        'type':'',
                        'ag_ledg_year': self.default_year, # 년도
                        'ag_ledgr_sessn': self.default_session, # 1=1학기, 2=여름계절, 3=2학기, 4=겨울계절
                        'ag_org_sect':'A', # A=학부, B=대학원, D=통번역대학원, E=교육대학원, G=정치행정언론대학원, H=국제지역대학원, I=경영대학원(주간), J=경영대학원(야간), L=법학전문대학원, M=TESOL대학원, T=TESOL전문교육원
                        'campus_sect':'H1', # H1=서울, H2=글로벌
                        'gubun': self.gubun_list[i], # 1=전공/부전공, 2=실용외국어/교양과목
                        'ag_crs_strct_cd': '', # 전공 목록
                        'ag_compt_fld_cd': self.liberal_code_list[k] # 교양 목록
                        }

                    self.liberal_data = list(self.parsing(params))

        self.all_data = self.major_data + self.liberal_data

    def parsing_major_name(self, major_name):

        #-----조회할 데이터 옵션 선택-----#

        self.course_info_list = list()
        

        if major_name in list(self.major_dict.keys()):
            params ={
                'tab_lang':'K',
                'type':'',
                'ag_ledg_year': self.default_year, # 년도
                'ag_ledgr_sessn':self.default_session, # 1=1학기, 2=여름계절, 3=2학기, 4=겨울계절
                'ag_org_sect':'A', # A=학부, B=대학원, D=통번역대학원, E=교육대학원, G=정치행정언론대학원, H=국제지역대학원, I=경영대학원(주간), J=경영대학원(야간), L=법학전문대학원, M=TESOL대학원, T=TESOL전문교육원
                'campus_sect':'H1', # H1=서울, H2=글로벌
                'gubun': '1', # 1=전공/부전공, 2=실용외국어/교양과목
                'ag_crs_strct_cd': self.major_dict[major_name], # 전공 목록
                'ag_compt_fld_cd': '' # 교양 목록
                }

            self.major_name_data = list(self.parsing(params))
        
        else:
            params ={
                'tab_lang':'K',
                'type':'',
                'ag_ledg_year':self.default_year, # 년도
                'ag_ledgr_sessn':self.default_session, # 1=1학기, 2=여름계절, 3=2학기, 4=겨울계절
                'ag_org_sect':'A', # A=학부, B=대학원, D=통번역대학원, E=교육대학원, G=정치행정언론대학원, H=국제지역대학원, I=경영대학원(주간), J=경영대학원(야간), L=법학전문대학원, M=TESOL대학원, T=TESOL전문교육원
                'campus_sect':'H1', # H1=서울, H2=글로벌
                'gubun': '2', # 1=전공/부전공, 2=실용외국어/교양과목
                'ag_crs_strct_cd': '', # 전공 목록
                'ag_compt_fld_cd': self.liberal_dict[major_name] # 교양 목록
                }

            self.major_name_data = list(self.parsing(params))


    def parsing(self, params):

        #####-----params를 인자로 받아서 파싱하는 함수-----#####
        
        self.current_session.post(timetable_url,data=params,headers=head)

        #-----파싱 시작-----#
        
        self.timetable = self.current_session.post(timetable_url,data=params,headers=head)

        html = BeautifulSoup(self.timetable.text, "lxml")
        tr_courses = html.find_all("tr", attrs={"height":"55"})
        
        for tr_course in tr_courses:
            course_area = tr_course.find_all("td")[1].string # 개설영역
            course_year = tr_course.find_all("td")[2].string # 학년
            course_number = tr_course.find_all("td")[3].string # 학수번호

            self.course_name = tr_course.find_all("td")[4].get_text() # 교과목명
            self.course_name = self.course_name.replace("\n","")
            cut_count = self.course_name.count("(")
            for i in range(cut_count):
                cut = self.course_name.rfind("(")
                self.course_name = self.course_name[:cut]
            
            self.course_professor = tr_course.find_all("td")[10].get_text() # 담당교수
            self.course_professor = self.course_professor.replace("\r","").replace("\t","").replace("\n","")
            cut = self.course_professor.rfind("(")
            if cut!=-1:
                self.course_professor = self.course_professor[:cut]

            self.course_time = tr_course.find_all("td")[13].get_text() # 강의시간
            cut = self.course_time.find("(")
            self.course_time = self.course_time[:cut-1]
            
            self.course_people = tr_course.find_all("td")[14].string # 현재인원
            self.course_people = self.course_people.replace("\xa0","")

            self.course_info_list.append([self.course_name, self.course_professor, self.course_time, self.course_people])

        self.parsing_data = self.course_info_list

        return self.parsing_data


if __name__ == '__main__':
    p = parsing_class()
    #p.parsing_all()
    p.parsing_major_name('군사학')
    
    
