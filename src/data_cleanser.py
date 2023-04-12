import pandas as pd

import logging
logger = logging.getLogger('my_logger3')
logger.setLevel(logging.INFO)

class DataCleanser:

    all_districts = [
        '서울특별시', '경기도', '강원도',
        '전라남도', '전라북도', '경상남도', '경상북도', '충청남도', '충청북도',
        '인천광역시', '광주광역시', '대구광역시', '대전광역시', '울산광역시', '부산광역시',
        '세종특별자치시', '제주특별자치도',
        '서울', '경기', '강원',
        '전남', '전북', '경남', '경북', '충남', '충북',
        '인천', '광주', '대구', '대전', '울산', '부산',
        '세종', '제주'
    ]
        
    def __init__(self, df: 'pandas.DataFrame', district_name: str) -> None:

        self.__df = df

        if district_name not in self.all_districts:
            raise ValueError('행정 구역을 정확히 기재해주새요.')
        else:
            new_district_name = district_name.replace('광역시', '')
            self.__district_name = new_district_name

    def delete_na_location(self):

        # 도로명주소와 지번주소가 모두 결측치인 행 제거
        cond = (self.__df['도로명주소'].notnull()) | (self.__df['지번주소'].notnull())
        # total_null_df = self.__df[~cond]
        self.__df = self.__df[cond]

        self.__df.reset_index(drop=True, inplace=True)

    def replace_location_strings(self):

        # [공중전화] => 문자열 제거
        self.__df['도로명주소'] = self.__df['도로명주소'].str.replace(pat=r"^\[공중전화\] ", repl='', regex=True)
        self.__df['지번주소'] = self.__df['지번주소'].str.replace(pat=r"^\[공중전화\] ", repl='', regex=True)

        # (~ 읍/면/동) => 문자열 제거
        self.__df['지번주소'] = self.__df['지번주소'].str.replace(pat=r"\([ㄱ-ㅣ가-힣0-9\s.:]+\)", repl='', regex=True).str.replace('  ', ' ')    

    def delete_ambiguous_location(self):

        ### 상담문의나 내용확인 불가 항목 제거
        elems = ['상담문의', '내용확인불가']
        cond = ~((self.__df['사건종별'].isin(elems)) & (self.__df['종결분류'] == '비출동종결') & (self.__df['신고종결'] == '조치없이 종결'))
        # total_not_df3 = self.__df[~cond]
        self.__df = self.__df[cond]

        self.__df.reset_index(drop=True, inplace=True)

        ### 허위신고, 오작동, 오인신고, 동일신고, FTX(기동훈련), 신고취소, 불발견, 타청/타서 항목 제거
        elems = ['허위', '오작동', '오인', '동일', 'FTX', '신고취소', '불발견', '타청,타서', '110/120']
        cond = ~(self.__df['신고종결'].isin(elems))
        # total_not_df4 = self.__df[~cond]
        self.__df = self.__df[cond]

        self.__df.reset_index(drop=True, inplace=True)

    def delete_other_district(self):

        del_districts = [ district_iter for district_iter in self.all_districts if self.__district_name not in district_iter ]

        # 도로명주소에 타 지역 이름이 들어간 주소 제거
        for district in del_districts:
            
            self.__df.query(
                expr=f'~도로명주소.str.startswith("{district} ", na=False)',
                inplace=True,
                engine='python'
            )
        else:
            # 도로명 주소가 notnull인 데이터를 self.__roadAddr_df에 저장
            self.__roadAddr_df = self.__df.query('도로명주소.notnull()', engine='python').reset_index(drop=True)

            # 도로명 주소가 null인 데이터를 self.df에 저장
            self.__df.query('도로명주소.isnull()', engine='python', inplace=True)

        # 지번주소 타 지역 이름이 들어간 주소 제거
        for district in del_districts:
            
            self.__df.query(
                expr=f'~지번주소.str.startswith("{district} ", na=False)',
                inplace=True,
                engine='python'
            )
        else:
            # 남은 데이터 중에서 지번주소가 notnull인 데이터를 self.__lotNumber_df에 저장
            self.__lotNumber_df = self.__df.reset_index(drop=True)

            # self.df는 더 이상 사용하지 않으므로 'END'를 입력
            self.__df = 'END'

    @property
    def get_roadAddr_df(self):
        
        return self.__roadAddr_df

    @property
    def get_lotNumber_df(self):
        
        return self.__lotNumber_df