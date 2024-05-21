# Kakao-API-Multi-Processing

이 프로그램은 수평 분할된 pandas DataFrame을 여러 서브 프로세스에서 도로명/지번 주소를 인자로 넣어 Kakao Restful API에 요청을 보내고, 응답으로 받은 위·경도 좌표 데이터에서 컬럼을 생성하여 다시 하나의 데이터프레임으로 병합합니다. 구현 과정에서 Multi-processing을 사용하여 병렬 처리 효율을 높였습니다.

## Why did you make it?

기존의 주소 좌표에 위경도를 추가하는 Restful API Get 요청 코드는 단일 API 호출로 인해 속도가 느리고, 호출 횟수 제한(6만 회)을 초과할 경우 여러 번 실행해야 하는 문제가 있었습니다.

## How to use it?

1. `src/api_keys.py` 모듈의 `RestApiKey` 클래스의 `__rest_api_key` 리스트에 Kakao API 키를 여러 개 입력합니다.

```python
__rest_api_key: List[str] = [
    'Message : Insert your kakao REST-API Keys'
]
```

2. `src/main.py` 모듈에서 위경도를 추가할 때 사용할 CSV 파일의 이름을 명시적으로 기재합니다. <br> (타 DBMS에서 소싱하는 데이터 파일 이름이 매번 다르기 때문입니다.)

```python
CSV_FILE_NAME = "test.csv"
```

3. `src/main.py` 모듈에서 불러온 `src/data_cleanser.py`와 같이 데이터를 본인의 코드에 맞게 전처리한 후 사용할 수도 있습니다.

```python
# 전처리 객체 생성 및 기능 사용
obj = DataCleanser(rcp_df, CITY_NAME)
obj.delete_na_location()
obj.replace_location_strings()
obj.delete_ambiguous_location()
obj.delete_other_district()
logging.info("Data preprocessing is fininshed")
```

4. 프로그램 실행을 실행합니다.

```bash
$ python main.py
```


Notes
------
- API 키가 더 많으면 더 많은 프로세스를 생성하여 분산 처리 속도를 증가시킵니다.
- 하나의 데이터 파일은 스포닝하는 여러 프로세스(=API 개수)로 분할됩니다.
- 메인 프로세스에서 스포닝한 서브 프로세스 중에 오류가 발생한 경우, 처리되기 직전까지의 데이터와 이후 데이터를 별도의 로컬 파일에 저장한 후 종료하는 예외 처리를 구현했습니다.
