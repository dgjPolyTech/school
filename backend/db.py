# 데이터베이스 연결 설정 관련 파일.
import os # 내 운영장치에 있는 파일에 접근하기 위함
from dotenv import load_dotenv # dotenv 라이브러리로부터 load_dotenv만 따로 빼낸다는 소리.
from sqlalchemy import create_engine # db 엔진을 만든다는데 대충 연결 설정 같은걸 만든다는 소리 같음.

# env 파일 읽어들이는 함수
# 따로 경로명 지정안하고 저렇게 () 식으로 두면 알아서 같은 폴더 내의 .env 파일 찾아서 실행됨.
load_dotenv() 

# env 파일에서 설정한 거 다 가져옴.
db_user = os.getenv('DB_USER')
db_pass = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')

# 해당 설정대로 db 연결하는 문장 생성(_str)
db_connection_str = f'mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}?charset=utf8mb4'
db_engine = create_engine(db_connection_str)

# 이런 __name__ 같은 구문은 엔트리 포인트라고 함. 이 프로그램이 여기서부터 시작된다. 라는 의미
# 정확히는, 내가 직접 db.py를 눌러 실행한 경우에는 아래의 print가 실행되고, 아니면 그냥 위의 db 엔진만 생성되어
# 다른 코드에서 가져다 쓸 수 있게 하기 위함.
if __name__ == "__main__":
    print(f"DB 엔진 생성 완료. 주소: {db_host}")