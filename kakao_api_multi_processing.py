import math
import requests
from multiprocessing import current_process

import logging

def get_kakao_api_multiprocessing(dict_proxy: 'multiprocessing.managers.DictProxy', df: 'pandas.DataFrame', api_key: str):
    
    header = {'Authorization': 'KakaoAK ' + api_key}
    
    try:
        for idx, data in df.iterrows():
            
            addr = data['도로명주소']

            # 도로명주소가 nan인 경우 스킵하여 api 호출 횟수를 아낌
            if isinstance(addr, float) and math.isnan(addr):
                continue
                # addr = data['지번주소']

            url = 'https://dapi.kakao.com/v2/local/search/address.json?query={address}'.format(address=addr)
            respose: 'requests.models.Response' = requests.get(url, headers=header)

            # 데이터를 정상으로 받아왔을 때
            if respose.status_code == 200:

                # json으로 파싱하여 위경도 데이터 적재
                result = respose.json()

                # result['documents']가 []인 경우 (호출은 정상이나, 주소에 대한 위경도를 못 찾는 경우)
                if not result['documents']:
                    continue

                # result['documents']가 []가 아닌 경우(위경도를 찾은 경우) 위경도 값을 대입
                df.loc[idx, 'longitude'] = result['documents'][0]['x']
                df.loc[idx, 'latitude'] = result['documents'][0]['y']

            elif respose.status_code == 400:

                logging.warn("ERROR[400]")

                # 데이터 호출 응답 에러 (400번 호출 상태)시 해당 행은 스킵
                continue

            else:
                logging.error(f" {current_process().name} : ERROR[{respose.status_code}]")
                break
                
    except KeyboardInterrupt as err:
        logging.error('key interrupt 발생')
    
    finally:
        dict_proxy[api_key] = df