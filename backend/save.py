# 전처리한 파일을 읽어 db에 저장하는 역할의 코드
import pandas as pd
from db import db_engine # db.py에서 만들어진 db_engine을 가져온다.

# 한글 데이터 들어간건 인코딩 관련 설정 필수.
# 전처리 코드에서 저장할 때 utf-8-sig로 저장했으므로 인코딩도 똑같이 맞춰줘야 함.
df = pd.read_csv('data/csv/ys_food_market_result.csv', encoding='utf-8-sig')

# school_Store라는 이름으로 sql 결과물을 받아오는데, 이것의 이름은 school_store
# 연결 설정은 db_engine 위에서 가져온거, 이미 데이터 있으면(if_exists) 교체, 각 컬럼마다 인덱싱 여부는 false
df.to_sql(name='school_store', con=db_engine, if_exists='replace', index=False)
print("데이터 업로드 완료.")

# 커밋 확인용 주석