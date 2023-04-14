# 프로세스 메모리 공유 변수
# from multiprocessing import Manager
# from multiprocessing import shared_memory 사용 가능 (파이썬 3.8 )
# from multiprocessing import Value, Array (명시적인 방법. 코드에 더 좋다)
# share_value = Value('i', 0)

# from concurrent.futures import ProcessPoolExecutor, as_completed

import warnings
warnings.filterwarnings(action='ignore')

import logging

# import signal
from multiprocessing import Process, Manager
from typing import List

import numpy as np
import pandas as pd

from kakao_api_multi_processing import get_kakao_api_multiprocessing
from api_keys import RestApiKey
from data_cleanser import DataCleanser

def main():

    # logging setting
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
    logging.info("Main-Process : before createing process")

    # Data Loading
    rcp_df = pd.read_csv('lot_not_comp_df.csv', dtype=str)
    # rcp_df = pd.read_csv('road_not_comp_df.csv')
    # rcp_df = pd.read_excel('1. ★안전서비스2.0 필요 데이터_인천경찰청(22.3.7_22.5.29).xlsx', header=2)
    logging.info("Data file loading is fininshed")
    logging.info(f"Loading Data Rows : {rcp_df.shape[0]}")
    
    print(rcp_df.isnull().sum())
    
    # 전처리 객체 생성 및 기능 사용
    obj = DataCleanser(rcp_df, '인천')
    obj.delete_na_location()
    obj.replace_location_strings()
    obj.delete_ambiguous_location()
    obj.delete_other_district()
    logging.info("Data preprocessing is fininshed")

    # targe 지정 및 분기
    target_col = '지번주소'
    
    if target_col == '도로명주소':
        target_df = obj.get_roadAddr_df
        non_target_col = '지번주소'
        non_target_df = obj.get_lotNumber_df
    elif target_col == '지번주소':
        target_df = obj.get_lotNumber_df
        non_target_col = '도로명주소'
        non_target_df = obj.get_roadAddr_df
    
    logging.info(f'target_col : {target_col}')
    logging.info(f"Target Data Rows : {target_df.shape[0]}")
    
    # API KEY 개수만큼 데이터프레임을 수평 분할
    split_df_lst: List['pandas.DataFrame'] = np.array_split(ary=target_df, indices_or_sections=len(RestApiKey.rest_api_key))

    # 분할된 데이터프레임 리스트와 API KEY 리스트를 엮기
    api_args = zip(split_df_lst, RestApiKey.rest_api_key)

    # Process간 Proxy를 이용해서 Data를 교환
    with Manager() as manager:

        # mangager를 통한 ListProxy 객체 생성
        lproxy: 'multiprocessing.managers.ListProxy' = manager.list()

        # process context 객체를 담을 리스트 
        processes: List['multiprocessing.context.Process'] = []

        for enum_it, args in enumerate(api_args):

            p = Process(
                target=get_kakao_api_multiprocessing,
                args=(lproxy, target_col, args[0], args[1], ),
                name="Kakao-api-prog Sub-Process" + str(enum_it)
            )

            processes.append(p)

            p.start()

        try:
            for p in processes:
                p.join()
        except KeyboardInterrupt:
            logging.warn("Keyboard interrupt in Main-Process")
        finally:
            total_df = pd.concat(lproxy)
            total_df.to_csv(f'{target_col}.csv', index=False)

            total_df.to_csv(f'{target_col}.csv', index=False)
            non_target_df.to_csv(f'{non_target_col}.csv', index=False)


if __name__ == '__main__':
    main()