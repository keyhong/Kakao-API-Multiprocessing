# Kakao-API-Multi-Processing

Kakao RestfulAPI(Request)를 multi-processing으로 Separte된 pandas.DataFrame에 도로명 주소, 지번 주소 순서대로 Argument를 날려서 위경도 좌표를 생성하고 병합하는 프로그램입니다.

## Why did you make it?

기존에 있던 주소 좌표에 위경도를 만들어주는 RestfulAPI Get Request 코드가 단일 API로 호출하다 보니, 속도가 느리고 호출 횟수(Kako API당 6만회 요청 가능)를 넘어가는 경우의 여러 번 돌려야 하는 문제가 있었습니다.

## How to use it?

1. src/api_keys.py 모듈의 RestApiKey 클래스의 __rest_api_key 리스트에 Kako API Key를 여러 개 입력합니다.

```python
__rest_api_key: List[str] = [
    'Message : Insert your kakao REST-API Keys'
]
```

2. src/main.py 모듈에서 위경도를 넣기 위해 읽어들일 csv 파일의 이름을 명시적 기재합니다. (데이터의 파일 이름이 매번 상이하기 때문)

```python
CSV_FILE_NAME = "test.csv"
```

3. src/main.py 모듈에서 불러온 src/data_cleanser.py처럼 데이터를 본인의 코드에 맞춰 전처리 후 사용할 수도 있습니다.

```python
# 전처리 객체 생성 및 기능 사용
obj = DataCleanser(rcp_df, CITY_NAME)
obj.delete_na_location()
obj.replace_location_strings()
obj.delete_ambiguous_location()
obj.delete_other_district()
logging.info("Data preprocessing is fininshed")
```

4. 프로그램 실행

```bash
$ python main.py
```


Notes
------
- API 키가 많으면 많을수록 생성하는 프로세스의 개수가 늘어나 분산처리 속도 증가합니다.
- 하나의 데이터 파일은 Spawning하는 여러 개의 프로세스(=API 개수) 만큼 분할 합니다.
- Main Process에서 Spawning하는 Sub Process에서 에러가 날 경우, 처리 도중 직전까지 에러가 나기 직전까지 처리된 데이터와 그 이후의 데이터를 따로 로컬 디렉터리에 파일에 저장 후 종료하도록 Exception을 설정하였습니다.
