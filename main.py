import requests
from bs4 import BeautifulSoup

import re

#---------------------------------------------------------------------------------------------------------#
#
# * HUFS 강의시간표 작동 방식에 따른 코드 로직
# 1) 수업별 현재 인원을 파악하려면 먼저 모든 수업을 조회해야 한다
# 2) 강의시간표는 검색 옵션을 params data에 담고 post로 보내서 결과를 보여준다
# 3) 모든 수업을 조회하려면 params data를 검색 옵션별로 다르게 만들어야 한다
#
#
# * 함수 설명
# __init__(self): 시간표 조회에 대한 모든 검색옵션 파싱 (단, 옵션의 default값인 학부, 서울캠퍼스는 고정)
# making_params(self): 모든 검색 옵션을 담은 params 리스트 만들기
# parsing(self): 모든 검색 옵션이 담긴 params 리스트를 iterate하여 post로 보내고, 수업별 현재인원 파싱
#
#---------------------------------------------------------------------------------------------------------#


head={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'}
timetable_url = "http://webs.hufs.ac.kr:8989/src08/jsp/lecture/LECTURE2020L.jsp"

#테스트: 학부 - 서울 - EICC학과
class parse_headcount():
    def __init__(self):
        
        #-----시간표 조회에 대한 default 옵션 가져오기-----#
        
        self.current_session = requests.session()
        
        self.current_session.get(timetable_url,headers=head)
        self.timetable = self.current_session.get(timetable_url,headers=head)
        html = BeautifulSoup(self.timetable.text, "html.parser")

        all_option = html.find_all("option", selected=True)
        
        self.default_year = all_option[0]['value'] # 연도
        self.default_session = all_option[1]['value'] # 학기
        self.default_school = all_option[2]['value'] # 학부


    def all_params(self):
        
        #-----시간표 조회에 대한 모든 옵션 가져오기-----#
        
        self.current_session = requests.session()
        
        self.current_session.get(timetable_url,headers=head)
        self.timetable = self.current_session.get(timetable_url,headers=head)
        html = BeautifulSoup(self.timetable.text, "html.parser")

        # default에 주의
        self.year_list = [] # 년도
        self.session_list = ['1','2','3','4'] # 학기
        self.school_list = ['A','B','D','E','G','H','I','J','L','M','T'] # A=학부(default), B=대학원, D=통번역대학원, E=교육대학원, G=정치행정언론대학원, H=국제지역대학원, I=경영대학원(주간), J=경영대학원(야간), L=법학전문대학원, M=TESOL대학원, T=TESOL전문교육원
        self.campus_list = ['H1','H2'] # H1=서울(default), H2=글로벌
        self.gubun_list = ['1','2'] # 1=전공/부전공, 2=실용외국어/교양과목
        self.major_list = [] # 전공 목록
        self.liberal_list = [] # 교양 목록
        
        years = html.find_all("select", attrs={"name":"ag_ledg_year"})
        sessions = html.find_all("select", attrs={"name":"ag_ledgr_sessn"})
        schools = html.find_all("select", attrs={"name":"ag_org_sect"})
        majors = html.find_all("select", attrs={"name":"ag_crs_strct_cd"})
        liberals = html.find_all("select", attrs={"name":"ag_compt_fld_cd"})
        
        years = years[0].find_all("option")
        for year in years:
            self.year_list.append(year['value'])

        majors = majors[0].find_all("option")
        for major in majors:
            self.major_list.append(major['value'])
        
        liberals = liberals[0].find_all("option")
        for liberal in liberals:
            self.liberal_list.append(liberal['value'])

        # print(len(major_list))    # 서울 전공개수 73개
        # print(len(liberal_list))  # 서울 교양개수 15개


    def making_params(self):
        
        #-----params dictionary 리스트 만들기-----#

        self.params_list = []
        
        params_keys = ['tab_lang','type','ag_ledg_year','ag_ledgr_sessn','ag_org_sect','campus_sect','gubun','ag_crs_strct_cd','ag_compt_fld_cd']
        params_values = ['K','','','','','','','','']
        
        params_values[2] = self.default_year
        params_values[3] = self.default_session
        params_values[4] = self.default_school
        params_values[5] = 'H1'
               
        number_of_cases = len(self.gubun_list)*len(self.major_list)*len(self.liberal_list)
        #print(number_of_cases)

        self.params_values_dictionary = dict() # params의 value값 딕셔너리
        
        for i in range(len(self.gubun_list)):
            if i==0:
                params_values[6] = self.gubun_list[i]
                
                for j in range(len(self.major_list)):
                    params_values[7] = self.major_list[j]
                    self.params_values_dictionary[j] = list(params_values)
            else:
                params_values[6] = self.gubun_list[i]
                params_values[7] = ''
                
                for k in range(len(self.liberal_list)):
                    params_values[8] = self.liberal_list[k]
                    self.params_values_dictionary[j+k] = list(params_values)


    def parsing_major(self):
        self.current_session = requests.session()

        #-----조회할 데이터 옵션 선택-----#

        self.course_info_list = list()

        for i in range(len(self.major_list)):
            params={
                'tab_lang':'K',
                'type':'',
                'ag_ledg_year':'2016', # 년도
                'ag_ledgr_sessn':'3', # 1=1학기, 2=여름계절, 3=2학기, 4=겨울계절
                'ag_org_sect':'A', # A=학부, B=대학원, D=통번역대학원, E=교육대학원, G=정치행정언론대학원, H=국제지역대학원, I=경영대학원(주간), J=경영대학원(야간), L=법학전문대학원, M=TESOL대학원, T=TESOL전문교육원
                'campus_sect':'H1', # H1=서울, H2=글로벌
                'gubun':'1', # 1=전공/부전공, 2=실용외국어/교양과목
                'ag_crs_strct_cd':self.major_list[i], # 전공 목록
                'ag_compt_fld_cd':'301_H1' # 교양 목록
                }
            
            self.current_session.post(timetable_url,data=params,headers=head)

            #-----파싱 시작-----#
            
            self.timetable = self.current_session.post(timetable_url,data=params,headers=head)

            html = BeautifulSoup(self.timetable.text, "html.parser")
            tr_courses = html.find_all("tr", attrs={"height":"55"})

            
            
            for tr_course in tr_courses:
                course_area = tr_course.find_all("td")[1].string # 개설영역
                course_year = tr_course.find_all("td")[2].string # 학년
                course_number = tr_course.find_all("td")[3].string # 학수번호

                self.course_name = tr_course.find_all("td")[4].get_text() # 교과목명
                self.course_name = self.course_name.replace("\n","")
                
                self.course_professor = tr_course.find_all("td")[10].get_text() # 담당교수
                self.course_professor = self.course_professor.replace("\r","").replace("\t","").replace("\n","")

                self.course_time = tr_course.find_all("td")[13].get_text() # 강의시간
                cut = self.course_time.find("(")
                self.course_time = self.course_time[:cut-1]
                
                self.course_people = tr_course.find_all("td")[14].string # 현재인원
                self.course_people = self.course_people.replace("\xa0","")
                

                self.course_info_list.append([self.course_name, self.course_professor, self.course_time, self.course_people])

        for i in range(len(self.course_info_list)):
            print(self.course_info_list[i])


    def parsing_liberal(self):
        self.current_session = requests.session()

        #-----조회할 데이터 옵션 선택-----#

        self.course_info_list = list()

        for i in range(len(self.liberal_list)):
            params={
                'tab_lang':'K',
                'type':'',
                'ag_ledg_year':'2016', # 년도
                'ag_ledgr_sessn':'3', # 1=1학기, 2=여름계절, 3=2학기, 4=겨울계절
                'ag_org_sect':'A', # A=학부, B=대학원, D=통번역대학원, E=교육대학원, G=정치행정언론대학원, H=국제지역대학원, I=경영대학원(주간), J=경영대학원(야간), L=법학전문대학원, M=TESOL대학원, T=TESOL전문교육원
                'campus_sect':'H1', # H1=서울, H2=글로벌
                'gubun':'2', # 1=전공/부전공, 2=실용외국어/교양과목
                'ag_crs_strct_cd':'', # 전공 목록
                'ag_compt_fld_cd':self.liberal_list[i] # 교양 목록
                }
            
            self.current_session.post(timetable_url,data=params,headers=head)

            #-----파싱 시작-----#
            
            self.timetable = self.current_session.post(timetable_url,data=params,headers=head)

            html = BeautifulSoup(self.timetable.text, "html.parser")
            tr_courses = html.find_all("tr", attrs={"height":"55"})

            
            
            for tr_course in tr_courses:
                course_area = tr_course.find_all("td")[1].string # 개설영역
                course_year = tr_course.find_all("td")[2].string # 학년
                course_number = tr_course.find_all("td")[3].string # 학수번호

                self.course_name = tr_course.find_all("td")[4].get_text() # 교과목명
                self.course_name = self.course_name.replace("\n","")
                
                self.course_professor = tr_course.find_all("td")[10].get_text() # 담당교수
                self.course_professor = self.course_professor.replace("\r","").replace("\t","").replace("\n","")

                self.course_time = tr_course.find_all("td")[13].get_text() # 강의시간
                cut = self.course_time.find("(")
                self.course_time = self.course_time[:cut-1]
                
                self.course_people = tr_course.find_all("td")[14].string # 현재인원
                self.course_people = self.course_people.replace("\xa0","")
                

                self.course_info_list.append([self.course_name, self.course_professor, self.course_time, self.course_people])

        for i in range(len(self.course_info_list)):
            print(self.course_info_list[i])
        
    def parsing_all(self):
        self.current_session = requests.session()

        #-----조회할 데이터 옵션 선택-----#

        self.course_info_list = list()

        for i in range(len(self.gubun_list)):
            if  i == 0:
                for j in range(2):
                    params ={
                        'tab_lang':'K',
                        'type':'',
                        'ag_ledg_year':'2016', # 년도
                        'ag_ledgr_sessn':'3', # 1=1학기, 2=여름계절, 3=2학기, 4=겨울계절
                        'ag_org_sect':'A', # A=학부, B=대학원, D=통번역대학원, E=교육대학원, G=정치행정언론대학원, H=국제지역대학원, I=경영대학원(주간), J=경영대학원(야간), L=법학전문대학원, M=TESOL대학원, T=TESOL전문교육원
                        'campus_sect':'H1', # H1=서울, H2=글로벌
                        'gubun': self.gubun_list[i], # 1=전공/부전공, 2=실용외국어/교양과목
                        'ag_crs_strct_cd': self.major_list[j], # 전공 목록
                        'ag_compt_fld_cd':'' # 교양 목록
                        }

                    self.current_session.post(timetable_url,data=params,headers=head)

                    #-----파싱 시작-----#
                    
                    self.timetable = self.current_session.post(timetable_url,data=params,headers=head)

                    html = BeautifulSoup(self.timetable.text, "html.parser")
                    tr_courses = html.find_all("tr", attrs={"height":"55"})
                    

                    for tr_course in tr_courses:
                        
                        course_area = tr_course.find_all("td")[1].string # 개설영역
                        course_year = tr_course.find_all("td")[2].string # 학년
                        course_number = tr_course.find_all("td")[3].string # 학수번호
                        
                        self.course_name = tr_course.find_all("td")[4].get_text() # 교과목명
                        self.course_name = self.course_name.replace("\n","")
                        
                        self.course_professor = tr_course.find_all("td")[10].get_text() # 담당교수
                        self.course_professor = self.course_professor.replace("\r","").replace("\t","").replace("\n","")

                        self.course_time = tr_course.find_all("td")[13].get_text() # 강의시간
                        cut = self.course_time.find("(")
                        self.course_time = self.course_time[:cut-1]
                        
                        self.course_people = tr_course.find_all("td")[14].string # 현재인원
                        self.course_people = self.course_people.replace("\xa0","")

                        self.course_info_list.append([self.course_name, self.course_professor, self.course_time, self.course_people])
                        
            else:
                for k in range(1):
                    params ={
                        'tab_lang':'K',
                        'type':'',
                        'ag_ledg_year':'2016', # 년도
                        'ag_ledgr_sessn':'3', # 1=1학기, 2=여름계절, 3=2학기, 4=겨울계절
                        'ag_org_sect':'A', # A=학부, B=대학원, D=통번역대학원, E=교육대학원, G=정치행정언론대학원, H=국제지역대학원, I=경영대학원(주간), J=경영대학원(야간), L=법학전문대학원, M=TESOL대학원, T=TESOL전문교육원
                        'campus_sect':'H1', # H1=서울, H2=글로벌
                        'gubun': self.gubun_list[i], # 1=전공/부전공, 2=실용외국어/교양과목
                        'ag_crs_strct_cd': '', # 전공 목록
                        'ag_compt_fld_cd': self.liberal_list[k] # 교양 목록
                        }

                    self.current_session.post(timetable_url,data=params,headers=head)

                    #-----파싱 시작-----#
                    
                    self.timetable = self.current_session.post(timetable_url,data=params,headers=head)

                    html = BeautifulSoup(self.timetable.text, "html.parser")
                    tr_courses = html.find_all("tr", attrs={"height":"55"})
                    
                    for tr_course in tr_courses:
                        course_area = tr_course.find_all("td")[1].string # 개설영역
                        course_year = tr_course.find_all("td")[2].string # 학년
                        course_number = tr_course.find_all("td")[3].string # 학수번호

                        self.course_name = tr_course.find_all("td")[4].get_text() # 교과목명
                        self.course_name = self.course_name.replace("\n","")
                        
                        self.course_professor = tr_course.find_all("td")[10].get_text() # 담당교수
                        self.course_professor = self.course_professor.replace("\r","").replace("\t","").replace("\n","")

                        self.course_time = tr_course.find_all("td")[13].get_text() # 강의시간
                        cut = self.course_time.find("(")
                        self.course_time = self.course_time[:cut-1]
                        
                        self.course_people = tr_course.find_all("td")[14].string # 현재인원
                        self.course_people = self.course_people.replace("\xa0","")

                        self.course_info_list.append([self.course_name, self.course_professor, self.course_time, self.course_people])

        for i in range(len(self.course_info_list)):
            print(self.course_info_list[i])

    def parsing(self, params):
        
        self.current_session.post(timetable_url,data=params,headers=head)

        #-----파싱 시작-----#
        
        self.timetable = self.current_session.post(timetable_url,data=params,headers=head)

        html = BeautifulSoup(self.timetable.text, "html.parser")
        tr_courses = html.find_all("tr", attrs={"height":"55"})
        
        for tr_course in tr_courses:
            course_area = tr_course.find_all("td")[1].string # 개설영역
            course_year = tr_course.find_all("td")[2].string # 학년
            course_number = tr_course.find_all("td")[3].string # 학수번호

            self.course_name = tr_course.find_all("td")[4].get_text() # 교과목명
            self.course_name = self.course_name.replace("\n","")
            
            self.course_professor = tr_course.find_all("td")[10].get_text() # 담당교수
            self.course_professor = self.course_professor.replace("\r","").replace("\t","").replace("\n","")

            self.course_time = tr_course.find_all("td")[13].get_text() # 강의시간
            cut = self.course_time.find("(")
            self.course_time = self.course_time[:cut-1]
            
            self.course_people = tr_course.find_all("td")[14].string # 현재인원
            self.course_people = self.course_people.replace("\xa0","")

            self.course_info_list.append([self.course_name, self.course_professor, self.course_time, self.course_people])

        #for i in range(len(self.course_info_list)):
        #    print(self.course_info_list[i])

        return(self.course_info_list)


    def parsing_example(self):
        self.current_session = requests.session()

        #-----조회할 데이터 옵션 선택-----#
        
        params={
            'tab_lang':'K',
            'type':'',
            'ag_ledg_year':'2016', # 년도
            'ag_ledgr_sessn':'3', # 1=1학기, 2=여름계절, 3=2학기, 4=겨울계절
            'ag_org_sect':'A', # A=학부, B=대학원, D=통번역대학원, E=교육대학원, G=정치행정언론대학원, H=국제지역대학원, I=경영대학원(주간), J=경영대학원(야간), L=법학전문대학원, M=TESOL대학원, T=TESOL전문교육원
            'campus_sect':'H1', # H1=서울, H2=글로벌
            'gubun':'1', # 1=전공/부전공, 2=실용외국어/교양과목
            'ag_crs_strct_cd':'A1CE1_H1', # 전공 목록
            'ag_compt_fld_cd':'301_H1' # 교양 목록
            }
        
        self.current_session.post(timetable_url,data=params,headers=head)

        #-----파싱 시작-----#
        
        self.timetable = self.current_session.post(timetable_url,data=params,headers=head)

        html = BeautifulSoup(self.timetable.text, "html.parser")
        tr_courses = html.find_all("tr", attrs={"height":"55"})

        self.course_info_list = list()
        
        for tr_course in tr_courses:
            course_area = tr_course.find_all("td")[1].string # 개설영역
            course_year = tr_course.find_all("td")[2].string # 학년
            course_number = tr_course.find_all("td")[3].string # 학수번호

            self.course_name = tr_course.find_all("td")[4].get_text() # 교과목명
            self.course_name = self.course_name.replace("\n","")
            
            self.course_professor = tr_course.find_all("td")[10].get_text() # 담당교수
            self.course_professor = self.course_professor.replace("\r","").replace("\t","").replace("\n","")

            self.course_time = tr_course.find_all("td")[13].get_text() # 강의시간
            cut = self.course_time.find("(")
            self.course_time = self.course_time[:cut-1]
            
            self.course_people = tr_course.find_all("td")[14].string # 현재인원
            self.course_people = self.course_people.replace("\xa0","")
            

            self.course_info_list.append([self.course_name, self.course_professor, self.course_time, self.course_people])

        for i in range(len(self.course_info_list)):
            print(self.course_info_list[i])
        
        
        '''옵션의 string을 구하는 코드
        years = html.find_all("select", attrs={"name":"ag_ledg_year"})
        years = years[0].get_text()
        years = years.replace("\xa0","")
        years = years.split("\n")
        years = years[1:-1]
        '''
        

if __name__ == '__main__':
    p = parse_headcount()
    p.all_params()
    p.making_params()
    #p.parsing_major()
    #p.parsing_liberal()
    p.parsing_all()
    
