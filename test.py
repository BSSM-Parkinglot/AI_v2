import re

def extract_license_plate(text):
    # 정규 표현식 패턴
    pattern = r'(\d{1,4}[가-힣]{1}\d{1,4})'
    
    # 패턴과 일치하는 모든 차량 번호판을 찾음
    license_plates = re.findall(pattern, text)
    
    # 차량 번호판 제거
    result = re.sub(pattern, '', text)
    
    return result, license_plates

# 예시 문자열
text = "오늘은 정말 좋은 날 입니다. 차량 번호판이 여러 개 있는데요. 서85가1333과 서7나222이 있어요."

# 차량 번호판 추출 및 제거
processed_text, license_plates = extract_license_plate(text)

print(f"차량 번호판이 제거된 문자열: {processed_text}")
print(f"추출된 차량 번호판: {license_plates}")