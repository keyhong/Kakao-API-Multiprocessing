.. -*- mode: rst -*-

=========================
Kakao-API-Multiprocessing
=========================

Kakao RestfulAPI(GetHttp)를 multi-processing으로 Separte된 Pandas DataFrame에 도로명 주소, 지번 주소 대로 Param을 날려서 위경도 좌표를 생성하고 병합하는 프로그램``

How to use
-----------
1. src/api_keys 안에 rest api key 를 기입

2. main.py 코드에 안에 읽어들일 csv 파일의 이름을 명시적 기재 (지역별 신고접수 데이터의 파일 이름이 다르기 때문에 하드코딩)

3. python main.py

Notes
------
- API 키가 많으면 많을 수록 분산처리 속도 증가

- 읽어들이는 파일은 넣은 API 개수만큼 분할

- 메인 프로세스에서 생긴 서브 프로세스에서 에러가 날 경우 처리된 데이터와 에러가 발생한 데이터를 따로 모아 로컬 디렉토리에 파일을 따로 저장
