# pandas: csv 기반 데이터셋 처리에 최적화된 라이브러리
# pyproj: x/y 기반 위치 데이터를 위경도 값으로 변환하기 위해 사용.
# haversine: 위경도 기반으로 거리 측정할 때 쓰는 라이브러리
# transformer: 위경도 좌표계를 필요한대로 바꿔주는 역할.
# openpyxl: 최종적으로 만들어진 데이터 프레임을 엑셀 파일로 변환.
import pandas as pd
import pyproj as pj
import haversine as hs
from pyproj import Transformer
import openpyxl as pyxl

file_path = 'data/source/ys_food_market.csv'

# 한글로 정리된 데이터는 인코딩 방식을 이렇게 해주는게 좋음.
market = pd.read_csv(file_path, encoding='cp949') # csv 파일을 읽어, 데이터 프레임 형식의 데이터로 반환함.

# 필요한 컬럼들로만 필터링
selected_col = ['영업상태코드', '영업상태명', '지번주소', '도로명주소', '사업장명', '전화번호', '업태구분명', '위생업태명', '좌표정보(X)', '좌표정보(Y)']
market_data = market[selected_col]

# 위생 업태명에 들어간 데이터 종류 확인
market_data['위생업태명'].unique()
market_data['업태구분명'].unique()

# 프로젝트에 들어갈만한 업태의 가게만 필터링
target_categories = ['편의점', '커피숍', '패스트푸드']
target_data = market_data[market_data['위생업태명'].isin(['편의점', '커피숍', '패스트푸드'])]

# 우리 학교(=폴리텍 정수) 위치 좌표를 구한다.(구글맵 등으로 구할 수 있음)
school_loc = (37.530526, 126.993484)

# epsg:5174 기반으로 정리된 위경도값을 4326 기반으로 바꾼 위경도 값을 받을 변수임.
# 구글맵으로 가져온 위경도 값은 4326 기반이기에, 우리가 가져온 위치 값과 같은 유형으로 전처리하는 과정이 필요함.
# 5174는 한국에서만 쓰이는 규격, 4326은 구글맵 필두로 세계적으로 쓰이는 규격이라함.
transform_xy = Transformer.from_crs("epsg:5174", "epsg:4326")

# 각 가게별 위경도 값을 상단의 우리 학교 위치 위경도값(school_loc)과 비교하여, 1km 이내인 경우만 추출하는 함수.
def get_distance(row):
    # 각 행을 row라는 이름으로 받아옴.
    # pandas의 isna 함수를 통해, row의 x or y 값이 비어있다면 그 행은 넘어감.
    if pd.isna(row['좌표정보(X)']) or pd.isna(row['좌표정보(Y)']):
        return None

    # 자바의 try-catch를 파이썬에서는 try-except라고 씀. 파이썬의 except가 자바의 catch 역할(둘 다 예외(에러) 발생 시 처리)
    try:
        # lat = 위도(lattitued), lon = 경도(longitude?)
        # 이번 과제에서는 문제 없었으나, 공공데이터 받아왔을 때 좌표 변환 안되는 것은 높은 확률로 위/경도가 거꾸로 기입되어 있어서인 경우가 많음.
        lat, lon = transform_xy.transform(row['좌표정보(Y)'], row['좌표정보(X)']) # 위에서 만든 변수에 변경된 위경도 값 기입.

        # haversine이라는 라이브러리 안에 haversine이라는 함수(라이브러리명과 함수명이 같음)가 거리 계산의 역할을 함.
        # 학교 위경도 값을 기준으로, 거리를 km 단위로 계산
        distance = hs.haversine(school_loc, (lat, lon), unit='km')

        return distance
    except Exception as e:
        print(f"전처리 중 오류 발생: {e}")
        return None

# target_data에서 필터링 된 데이터만 따로 보기 위해 만든 변수
# target_data의 구조를 그대로 본따서 만든다.
target_filtered = target_data.copy()
target_filtered['거리_km'] = target_data.apply(get_distance, axis=1) # 위에서 만든 함수로, 전체 가게들의 거리를 행 별로 측정하여 ['거리_km']라는 이름의 새로 만든 행(=가로)에 붙여넣는다.
# get_distance라고 쓰고 매개변수(row)를 안줬는데, 이건 판다스의 문법으로 쉽게 말하자면 이 함수(get_distance)를 토대로 너가 알아서 동작해라...라는 의미라고 함. 이런걸 콜백 함수라고 함.
# apply는 판다스의 내장 함수. axis=1은 행(row, 가로, 왼쪽에서 오른쪽)를 의미하며, axis=0이면 열(col, 세로, 위에서 아래로)를 의미. axis=0이 기본값이라 생략 가능함.
# get_distance 자체가 행을 기준으로 동작해야하므로 axis=1을 쓴 것.
# axis는 정확히는 읽는 방향으로 이해하면 편함. 이건 좀 복잡한 부분이라 나중에 혼자서 짤 때에는 모르겠으면 ai에게 질문하면서 하기

target_view = target_filtered[target_filtered['거리_km'] <= 1.0].sort_values('거리_km') # 그 거리_km가 1.0이하인 경우(=1km 이내인)만 가져오고, 거리를 기준으로 정렬
# target_filtered[target_filtered['거리_km'] <= 1.0] 이 문구 자체가 "target_filtered 데이터 안에서 target_filtered['거리_km']가(=거리 데이터) 가 1.0이하인 데이터"를 의미함.
# 정렬 기준은 기본 오름차순으로, 위처럼 아무것도 안쓰면 기본 정렬 순서로 가므로 우리 코드는 오름차순 정렬됨.

target_view[['사업장명', '위생업태명','도로명주소', '거리_km']].head(10) # 여러개의 컬럼만 뽑아 보고 싶을 때는 [[겹대괄호]] 형식 사용
# 참고로 target_view['사업장명'] 식으로 하나의 컬럼만 뽑아내면 그 데이터에 한해서는 데이터 프레임 형식이 아니라 series라는 또 다른 형식으로 취급된다고 함.
# 시리즈는 데이터 프레임의 하위 분류로, 데이터프레임 하나의 행 or 열의 데이터가 일렬로 쭉 늘어선 형태. 즉, 시리즈가 여러개 모인게 데이터프레임이라 봐도 무방함.

result_data = target_filtered.drop(columns=['좌표정보(X)', '좌표정보(Y)']) # 굳이 필요없는 x, y는 제외한 최종 결과값을 도출.
try:
    # 최종 결과물을 엑셀파일(.csv)로 변환
    # csv로 변환하는건 pandas, 엑셀 파일로 변환은 openpyxl이 해줌.
    csv_path = 'data/csv'
    excel_path = 'data/excel'

    result_data.to_csv(f'{csv_path}/ys_food_market_result.csv', index=False, encoding='utf-8-sig')
    result_data.to_excel(f'{excel_path}/ys_food_market_result.xlsx', index=False)

    print("데이터 전처리 및 파일 변환 완료.")
except Exception as e:
    print(f'파일 전환 중 오류 발생: {e}')