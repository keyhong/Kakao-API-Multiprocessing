"""kakao api 병렬처리 함수를 정의한 모듈"""

import logging
import math
import multiprocessing
from multiprocessing import current_process
from typing import Dict

import pandas as pd
import requests

HTTP_ERROR_STATUS_CODE: Dict[int, str] = {
    400: "Bad Request",  # 일반적인 오류 (API에 필요한 필수 파라미터와 관련하여 서버가 클라이언트 오류 감지)
    401: "Unauthorized",  # 인증오류
    403: "Forbidden",
    # 쿼터 초과 (Daum 검색, 로컬, 모먼트, 키워드광고 API에만 해당) 정해진 사용량이나 초당 요청 한도를 초과
    429: "Too Many Request",
    500: "Internal Server Error",  # 시스템 오류서버
    502: "Bad Gateway",  # 게이트웨이 오류
    503: "Service Unavailable",  # 서비스 점검중
}


def get_kakao_api_multiprocessing(
    list_proxy: multiprocessing.managers.ListProxy,
    target_col: str,
    df: pd.DataFrame,
    api_key: str,
):
    """kakao api를 이용하여 데이터프레임을 분할하여 multi-processing으로 전처리하는 함수"""

    logging.info("%s : start", current_process().name)

    try:
        for idx, data in df.iterrows():

            addr = data[target_col]

            # 주소가 nan인 경우 스킵하여 api 호출 횟수를 아낌
            if isinstance(addr, float) and math.isnan(addr):
                continue

            url = f"https://dapi.kakao.com/v2/local/search/address.json?query={addr}"
            respose: requests.models.Response = requests.get(
                url, headers={"Authorization": f"KakaoAK {api_key}"}, timeout=10
            )

            # 요청값이 비정상적인 경우
            if respose.status_code in HTTP_ERROR_STATUS_CODE:

                logging.error(
                    "%s : ERROR[%s] %s",
                    current_process().name,
                    respose.status_code,
                    HTTP_ERROR_STATUS_CODE.get(respose.status_code),
                )

                if respose.status_code == 400:
                    continue
                else:
                    break

            # 데이터를 정상으로 받아왔을 때
            if respose.status_code == 200:

                # json으로 파싱하여 위경도 데이터 적재
                result = respose.json()

                # result['documents']가 []인 경우 (호출은 정상이나, 주소에 대한 위경도를 못 찾는 경우)
                if not result["documents"]:
                    continue

                # result['documents']가 []가 아닌 경우(위경도를 찾은 경우) 위경도 값을 대입
                df.loc[idx, "lo"] = result["documents"][0]["x"]
                df.loc[idx, "la"] = result["documents"][0]["y"]

    except KeyboardInterrupt:
        logging.warning("%s : Finished (Keyboard interrupt in Main-Process)", current_process().name)
    else:
        logging.info("%s : Finished", current_process().name)
    finally:
        list_proxy.append(df)
