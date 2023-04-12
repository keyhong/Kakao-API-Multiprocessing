# 프로세스 메모리 공유 변수
# from multiprocessing import Manager
# from multiprocessing import shared_memory 사용 가능 (파이썬 3.8 )
# from multiprocessing import Value, Array (명시적인 방법. 코드에 더 좋다)
# share_value = Value('i', 0)

# from concurrent.futures import ProcessPoolExecutor, as_complet ed

import warnings
warnings.filterwarnings(action='ignore')

import logging
logger = logging.getLogger('my_logger')
logger.setLevel(logging.INFO)

from multiprocessing import Process, Manager
from typing import List

import numpy as np
import pandas as pd

from kakao_api_multi_processing import get_kakao_api_multiprocessing
from api_keys import RestApiKey
from data_cleanser import DataCleanser

def main():

    # Data Loading
    rcp_df1 = pd.read_excel('1. ★안전서비스2.0 필요 데이터_인천경찰청(22.3.7_22.5.29).xlsx', header=2)
    rcp_df1.rename(columns={'도로명주소': '지번주소', '지번주소': '도로명주소'}, inplace=True)

    logger.info('파일 읽기 완료')

    obj = DataCleanser(rcp_df1, '인천')
    obj.delete_na_location()
    obj.replace_location_strings()
    obj.delete_ambiguous_location()
    obj.delete_other_district()

    logger.info('파일 전처리 완료')

    # api키 개수만큼 데이터프레임을 수평분할
    split_dfs: List['pandas.DataFrame'] = np.array_split(ary=obj.get_roadAddr_df, indices_or_sections=len(RestApiKey.rest_api_key))

    logger.info('분할 완료')

    # Process간 Proxy를 이용해서 Data를 교환
    with Manager() as manager:
        
        l = manager.dict()
        # process context 객체를 담을 리스트 
        processes: List['multiprocessing.context.Process'] = []
        
        for df, key in zip(split_dfs, RestApiKey.rest_api_key):
            p = Process(target=get_kakao_api_multiprocessing, args=(l, df, key), daemon=True)

            processes.append(p)

            p.start()

        for p in processes:
            p.join()

        total_df = pd.concat(l)
        total_df.to_csv('road_data.csv', index=False)


if __name__ == '__main__':

    main()