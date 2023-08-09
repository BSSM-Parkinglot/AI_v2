import requests
import uuid
import time
import json

api_url = 'https://jxipvnd5gr.apigw.ntruss.com/custom/v1/23940/23d399aece734a838e4a57babf9b53de95e487b0011119e00a8269b3e7fca1ad/general'
secret_key = 'RGl2dlRmaFZrZ0ZPQWVCR2ZUZW5UTE5hYkJhbFRhY0c='
image_file = './saved_frames/frame.png'


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

response = requests.request("POST", api_url, headers=headers, data = payload, files = files)

result = response.json()
with open('result.json', 'w', encoding='utf-8') as make_file:
	json.dump(result, make_file, indent="\t")

text = ""
for field in result['images'][0]['fields']:
	text += field['inferText']
print(text)