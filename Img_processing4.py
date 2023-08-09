import cv2
import os
import requests
import uuid
import time
import json
import re
import threading
import pymysql

# 기존 코드 생략 ...
cap = cv2.VideoCapture(0)

api_url = 'https://jxipvnd5gr.apigw.ntruss.com/custom/v1/23940/23d399aece734a838e4a57babf9b53de95e487b0011119e00a8269b3e7fca1ad/general'
secret_key = 'RGl2dlRmaFZrZ0ZPQWVCR2ZUZW5UTE5hYkJhbFRhY0c='
image_file = './saved_frames/frame.png'

def extract_license_plate(text):
    # 정규 표현식 패턴
    pattern = r'(\d{1,4}[가-힣]{1}\d{1,4})'
    
    # 패턴과 일치하는 모든 차량 번호판을 찾음
    license_plates = re.findall(pattern, text)

    if not license_plates:
        return ""
    return license_plates[0]


def api_request():
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

    return response.json()

def api_request_thread():
    while True:
        if os.path.exists(image_file):
            result = api_request()
            # print("result :", result)
            with open('result.json', 'w', encoding='utf-8') as make_file:
                json.dump(result, make_file, indent="\t")

            con = pymysql.connect(host="svc.sel4.cloudtype.app",user="root",password="mysql",db="parkinglot",port=32676)
            cur = con.cursor()
            try:
              text = ""
              for field in result['images'][0]['fields']:
                  text += field['inferText']
              text = extract_license_plate(text)
              print("text : " , text)
              sql = "SELECT CarNum,ExitTime FROM Car_Info where CarNum='{}' and ExitTime IS NULL".format(text) 
              cur.execute(sql)

              rows = cur.fetchall()
              print("rows : ", rows)
              print("text type : ",type(text))

              if (not rows) and text != "":
                  # INSERT가 문제인듯
                  sql = "INSERT INTO Car_Info(CarNum) VALUES('{}')".format(text) 
                  cur.execute(sql)
                  con.commit()
                  print("입력이되었습니다 !")
                  # pass
              else:
                  # sql = "INSERT INTO Car_Info(Time,Money,EnterTime,ExitTime,CarNum,Spot) VALUES(null,null,null,now(),'{}',null)".format(text) 
                  # cur.execute(sql)
                  pass

              #자동차번호랑 exit값이 null이면 select ?

              # STEP 5: DB 연결 종료
              con.close()
            except Exception as e:
                print("error : ",e)
                pass

        time.sleep(0.5)  # API 요청 간격 조절

# 기존 코드 생략 ...

# API 요청 스레드 시작
api_thread = threading.Thread(target=api_request_thread, daemon=True)
api_thread.start()

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

    # 'q'키를 누르면 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 비디오 캡처 및 윈도우 종료
cap.release()
cv2.destroyAllWindows()
