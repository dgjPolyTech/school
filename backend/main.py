from fastapi import FastAPI # FastAPI: 웹 서버 만드는 역할. 쉽게 말해 남들이 접속할 수 있는 인터넷 주소(URL)로 접근할 수 있게함.
from sqlalchemy import create_engine # SQLAlchemy: DB 연동 관련 설정하는 라이브러리
import pandas as pd # 늘 쓰던 데이터프레임 형식의 데이터 계산할 때 쓰는 그거
import pymysql # SQL 문 날릴 때 사용하는 라이브러리

from db import db_engine # db.py에서 생성한 db 엔진을 가져옴.

app = FastAPI() # FastAPI를 통해 만든 웹 서버를 app 이라는 이름으로 제어? 함

# 위에서 만든 app(=FastAPI 서버)로부터 응답을 받아옴. /인거 보니 기본? 상태다 라는 응답을 받으면 정상적으로 됐다고 판단하는 것 같음.
# 대충 url 뒤에 / 라고 붙이는게 기본 상태.
@app.get("/")
def road_root():
    return {"message":"서버가 정상 작동 중"}

# /stores 라는 이름으로 api를 불러오면 학교 주변 가게 정보를 불러옴.
@app.get("/stores")
def get_stores():
    
    try:
        query = "SELECT * FROM school_store"
        
        # 학교 주변 가게 목록을 SELECT 문으로 읽음
        df = pd.read_sql(query, con=db_engine)
        
        # 불러들인 정보를 파이썬 객체(Object) 형태로 바꿈.
        # 판다스에서는 숫자는 정수나 소수의 값만 들어갈 수 있으며, 빈 값(None)의 경우 NaN이라는 값으로 대신 채워 넣음.(숫자 없음 이라는 의미라는 듯)
        # 하지만 이 형태는 JSON 형식에서는 받아들일 수 없기에, JSNO에서도 받아들일 수 있는 none으로 바꾸기 위해서 이렇게 해주는 것(none은 null처럼 받아들인다고 함.)
        df = df.astype(object).where(pd.notnull(df), None)
        
        # 해당 정보를 JSON 형태로 변환.
        # 정확히는 파이썬에서는 딕셔너리 리스트 형태로 바꿔주는데, 이를 api로 호출해서 보내는 과정에서 JSON 형태로 가공되는 것.
        # 이것도 프론트 단계에서 보여주기 위한 작업이라 보면 됨
        result = df.to_dict(orient='records')
        print("데이터 호출 완료. ", result)
        
        return result

    except Exception as e:
        print(f"데이터 조회 중 오류 발생: {e}")
        return {"error_message": str(e)}