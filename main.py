import os

import warnings
warnings.filterwarnings(action='ignore')


# 프로세스 메모리 공유 변수
from multiprocessing import Manager
# from multiprocessing import shared_memory 사용 가능 (파이썬 3.8 )
# from multiprocessing import Value, Array (명시적인 방법. 코드에 더 좋다)
# share_value = Value('i', 0)

from multiprocessing import Process
from concurrent.futures import ProcessPoolExecutor, as_completed

import logging
logging.getLogger()

import numpy as np
import pandas as pd

from typing import List

from kakao_api_multi_processing import get_kakao_api_multiprocessing

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
        
    def __init__(self, df, district_name) -> None:

        self.df = df

        if district_name not in self.all_districts:
            raise ValueError('행정 구역을 정확히 기재해주새요.')
        else:
            new_district_name = district_name.replace('광역시', '')
            self.district_name = new_district_name

    def delete_na_location(self):

        # 도로명주소와 지번주소가 모두 결측치인 행 제거
        cond = (self.df['도로명주소'].notnull()) | (self.df['지번주소'].notnull())
        # total_null_df = self.df[~cond]
        self.df = self.df[cond]

        self.df.reset_index(drop=True, inplace=True)

    def replace_location_strings(self):

        # 도로명주소, 지번주소 문자열 전처리
        
        # [공중전화] => 문자열 제거
        self.df['도로명주소'] = self.df['도로명주소'].str.replace(pat=r"^\[공중전화\] ", repl='', regex=True)
        self.df['지번주소'] = self.df['지번주소'].str.replace(pat=r"^\[공중전화\] ", repl='', regex=True)

        # (~ 읍/면/동) => 문자열 제거
        self.df['지번주소'] = self.df['지번주소'].str.replace(pat=r"\([ㄱ-ㅣ가-힣0-9\s.:]+\)", repl='', regex=True).str.replace('  ', ' ')    

    def delete_ambiguous_location(self):

        ### 상담문의나 내용확인 불가 항목 제거
        elems = ['상담문의', '내용확인불가']
        cond = ~((self.df['사건종별'].isin(elems)) & (self.df['종결분류'] == '비출동종결') & (self.df['신고종결'] == '조치없이 종결'))
        # total_not_df3 = self.df[~cond]
        self.df = self.df[cond]

        self.df.reset_index(drop=True, inplace=True)

        ### 허위신고, 오작동, 오인신고, 동일신고, FTX(기동훈련), 신고취소, 불발견, 타청/타서 항목 제거
        elems = ['허위', '오작동', '오인', '동일', 'FTX', '신고취소', '불발견', '타청,타서', '110/120']
        cond = ~(self.df['신고종결'].isin(elems))
        # total_not_df4 = self.df[~cond]
        self.df = self.df[cond]

        self.df.reset_index(drop=True, inplace=True)

    def delete_other_district(self):

        del_districts = [ district_iter  for district_iter in self.all_districts if self.district not in district_iter ]

        # 도로명주소에 타 지역 이름이 들어간 주소 제거
        for district in del_districts:
            
            self.df.query(
                expr=f'~도로명주소.str.startswith("{district} ", na=False)',
                inplace=True,
                engine='python'
            )
        else:
            self.roadAddr_df = self.df.copy()

        # 지번주소 타 지역 이름이 들어간 주소 제거
        for district in del_districts:
            
            self.df.query(
                expr=f'~지번주소.str.startswith("{district} ", na=False)',
                inplace=True,
                engine='python'
            )
        else:
            self.lotNumber_df = self.df.copy()

    @property
    def get_roadAddr_df(self):
        
        return self.roadAddr_df

    @property
    def get_lotNumber_df(self):
        
        return self.lotNumber_df


def main():

    # Data Loading
    rcp_df = pd.read_csv('./third_no.csv')

    rest_api_key: List[str] = [
        'e85fb0270567a4c0b8990b126b539078', # 수인님1
        '0652f1f78bc666ceaadb84aa97eb30ef', # 수연님1
        '117d85f90b9caa725058c8104c7b867c', # 수연님2
        '250cc48a64b2c6cf49c3dc59cacad26f', # 상수님1
        'ad0c6b655b7ea561018af3e6b9df04b2', # 상수님2
        'a1e70650fec9c18983f5fc5260f2d35f', # 아현님1
        '284ff67f2b076ee55d79add46d6f03d3'  # 아현님2
    ]


    # api키 개수만큼 데이터프레임을 수평분할
    split_dfs: List['pandas.DataFrame'] = np.array_split(ary=rcp_df, indices_or_sections=len(rest_api_key))

    # Process간 Proxy를 이용해서 Data를 교환
    with Manager() as manager:
        d = manager.dict()

        # process context 객체를 담을 리스트 
        processes: List['multiprocessing.context.Process'] = []

        for df, key in zip(split_dfs, rest_api_key):
            p = Process(target=get_kakao_api_multiprocessing, args=(d, df, key))

            processes.append(p)

            p.start()

        for p in processes:
            p.join()

        """
        with ProcessPoolExecutor(max_workers=len(process_lst)) as executor:

            future_to_api = {
                executor.submit(get_kakao_api, df, api_key, df_dict): process  for api_key, df in zip(rest_api_key, split_dfs)
            } 

            # for future in as_completed(future_to_api):
        """

if __name__ == '__main__':

    main()