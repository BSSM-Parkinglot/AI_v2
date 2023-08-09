from threading import Thread
import cv2
import os
import requests
import uuid
import time
import json
import re

# 웹캠에서 비디오 캡쳐
cap = cv2.VideoCapture(0)

api_url = 'https://jxipvnd5gr.apigw.ntruss.com/custom/v1/23940/23d399aece734a838e4a57babf9b53de95e487b0011119e00a8269b3e7fca1ad/general'
secret_key = 'RGl2dlRmaFZrZ0ZPQWVCR2ZUZW5UTE5hYkJhbFRhY0c='
image_file = './saved_frames/frame.png'
result = []

def extract_license_plate(text):
    # 정규 표현식 패턴
    pattern = r'(\d{1,4}[가-힣]{1}\d{1,4})'
    
    # 패턴과 일치하는 모든 차량 번호판을 찾음
    license_plates = re.findall(pattern, text)

    if not license_plates:
        return ""
    return license_plates[0]

def api_request(image_file):
    global result

    request_json = {
      'images': [
          {
              'format': 'jpg',
              'name': 'demo'
          }
      ],
      'requestId': str(uuid.uuid4()),
      'version': 'V2',
      'timestamp': int(round(time.time() * 1000))
    }

    payload = {'message': json.dumps(request_json).encode('UTF-8')}
    files = [
      ('file', open(image_file,'rb'))
    ]
    headers = {
      'X-OCR-SECRET': secret_key
    }

    response = requests.request("POST", api_url, headers=headers, data=payload, files=files)

    result = response.json()
    return 

# 이미지 파일을 저장할 디렉토리 생성 (디렉토리가 없는 경우에만)
output_dir = 'saved_frames'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)


while True:
    # 웹캠에서 프레임 캡처
    ret, frame = cap.read()

    # 프레임을 화면에 표시
    cv2.imshow('Video Capture', frame)

    # 이미지 파일 저장
    cv2.imwrite(os.path.join(output_dir, 'frame.png'), frame)

    th = Thread(target=api_request, args=(image_file))
    th.start()
    th.join()

    
    with open('result.json', 'w', encoding='utf-8') as make_file:
        json.dump(result, make_file, indent="\t")

    text = ""
    for field in result['images'][0]['fields']:
        text += field['inferText']

      
    print(extract_license_plate(text))

    # 'q'키를 누르면 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 비디오 캡처 및 윈도우 종료
cap.release()
cv2.destroyAllWindows()