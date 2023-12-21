.. -*- mode: rst -*-

=========================
Kakao-API-Multiprocessing
=========================

Kakao RestfulAPI(GetHttp)를 multi-processing으로 Separte된 Pandas DataFrame에 도로명 주소, 지번 주소 대로 Param을 날려서 위경도 좌표를 생성하고 병합하는 프로그램입니다.

How to use
-----------
1. src/api_keys 안에 rest api key를 기입합니다.
2. main.py 코드에 안에 읽어들일 csv 파일의 이름을 명시적 기재합니다. (지역별 데이터의 파일 이름이 다르기 때문에 하드코딩)
3. data_cleanser.py 안의 지역의 이름을 수정합니다.
3. 프로그램 실행 : python main.py

Notes
------
- API 키가 많으면 많을수록 분산처리 속도 증가합니다.
- 데이터 파일은 넣은 API 개수만큼 분할합니다.
- Main Process에서 Spawning한 Sub Process에서 에러가 날 경우 직전까지 처리된 Row와 그 이후의 Row를 따로 로컬 디렉토리에 파일로 저장하도록 Exception 코딩하였습니다.
