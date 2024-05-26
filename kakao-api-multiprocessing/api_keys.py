
"""Kakao API Key를 등록하는 모듈"""
from typing import List


class RestApiKey:
    """Kakao RestfulAPI에 Get 메서드로 데이터를 가져오기 위해 request 파라미터로 넘기는 API Key"""

    __rest_api_key: List[str] = ["Message : Insert your kakao REST-API Keys"]

    @property
    def get_rest_api_key(self) -> List[str]:
        """get rest api key"""
        return self.__rest_api_key
