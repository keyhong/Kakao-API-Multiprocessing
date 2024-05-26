"""Main Entrypoint"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import multiprocessing
import warnings
from multiprocessing import Manager, Process
from typing import List

import numpy as np
import pandas as pd
from api_keys import RestApiKey
from data_cleanser import DataCleanser
from kakao_api_multi_processing import get_kakao_api_multiprocessing

warnings.filterwarnings(action="ignore")


CSV_FILE_NAME = "test.csv"
CITY_NAME = "인천"


def main():
    """main function"""

    # logging setting
    logging.basicConfig(format="%(asctime)s: %(message)s", level=logging.INFO, datefmt="%H:%M:%S")
    logging.info("Main-Process : Before Createing Sub-Process")

    # Data Loading
    rcp_df = pd.read_csv(CSV_FILE_NAME, dtype=str)
    logging.info("Data file loading is fininshed")
    logging.info("Loading Data Rows : %s", rcp_df.shape[0])

    # 전처리 객체 생성 및 기능 사용
    obj = DataCleanser(rcp_df, CITY_NAME)
    obj.delete_na_location()
    obj.replace_location_strings()
    obj.delete_ambiguous_location()
    obj.delete_other_district()
    logging.info("Data preprocessing is fininshed")

    # target 지정
    rn_adrs_df = obj.get_rn_adrs_df.copy()
    logging.info("target_col: rn_adrs")
    logging.info("Target Data Rows : %s", rn_adrs_df.shape[0])

    # API KEY 개수만큼 데이터프레임을 수평 분할
    split_df_lst: List[pd.DataFrame] = np.array_split(ary=rn_adrs_df, indices_or_sections=len(RestApiKey.rest_api_key))

    # 분할된 데이터프레임 리스트와 API KEY 리스트를 엮기
    api_args = zip(split_df_lst, RestApiKey.rest_api_key)

    # Process간 Proxy를 이용해서 Data를 교환
    with Manager() as manager:

        # mangager를 통한 ListProxy 객체 생성
        lproxy: multiprocessing.managers.ListProxy = manager.list()

        # process context 객체를 담을 리스트
        processes: List[multiprocessing.context.Process] = []

        for enum_it, args in enumerate(api_args):

            p = Process(
                target=get_kakao_api_multiprocessing,
                args=(
                    lproxy,
                    "rn_adrs",
                    args[0],
                    args[1],
                ),
                name="Kakao-api-prog Sub-Process" + str(enum_it),
            )

            processes.append(p)

            p.start()

        try:
            for p in processes:
                p.join()
        except KeyboardInterrupt:
            logging.warning("Keyboard interrupt in Main-Process")
        finally:
            # 프로세스별 API를 돌린 데이터프레임을 수평병합
            rn_adrs_df = pd.concat(lproxy)

            rn_adrs_df[rn_adrs_df["lo"].notnull()].to_csv("rn_adrs.csv", index=False)

            if rn_adrs_df[rn_adrs_df["lo"].isnull()].empty:
                lno_adrs_df = obj.get_lno_adrs_df.copy()
            else:
                lno_adrs_df = pd.concat([rn_adrs_df[rn_adrs_df["lo"].isnull()], obj.get_lno_adrs_df.copy()])

            lno_adrs_df.to_csv("lno_adrs.csv", index=False)

    # new target 지정
    lno_adrs_df.reset_index(drop=True, inplace=True)
    logging.info("target_col: lno_adrs")
    logging.info("Target Data Rows : %s", lno_adrs_df.shape[0])

    # API KEY 개수만큼 데이터프레임을 수평 분할
    split_df_lst: List[pd.DataFrame] = np.array_split(
        ary=lno_adrs_df, indices_or_sections=len(RestApiKey.rest_api_key)
    )

    # 분할된 데이터프레임 리스트와 API KEY 리스트를 엮기
    api_args = zip(split_df_lst, RestApiKey.rest_api_key)

    # Process간 Proxy를 이용해서 Data를 교환
    with Manager() as manager:

        # mangager를 통한 ListProxy 객체 생성
        lproxy: "multiprocessing.managers.ListProxy" = manager.list()

        # process context 객체를 담을 리스트
        processes: List["multiprocessing.context.Process"] = []

        for enum_it, args in enumerate(api_args):

            p = Process(
                target=get_kakao_api_multiprocessing,
                args=(
                    lproxy,
                    "lno_adrs",
                    args[0],
                    args[1],
                ),
                name="Kakao-api-prog Sub-Process" + str(enum_it),
            )

            processes.append(p)

            p.start()

        try:
            for p in processes:
                p.join()
        except KeyboardInterrupt:
            logging.warning("Keyboard interrupt in Main-Process")
        finally:
            # 프로세스별 API를 돌린 데이터프레임을 수평병합
            lno_adrs_df = pd.concat(lproxy)

            lno_adrs_df[lno_adrs_df["lo"].notnull()].to_csv("lno_adrs.csv", index=False)
            lno_adrs_df[lno_adrs_df["lo"].isnull()].to_csv("null_adrs.csv", index=False)

    logging.info("Main-Process : Finished")


if __name__ == "__main__":
    main()
