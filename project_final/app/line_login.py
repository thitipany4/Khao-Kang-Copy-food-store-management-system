import hashlib
import random
import time
import requests
import json
import base64

class LineLogin:
    CLIENT_ID = '2002071461'
    CLIENT_SECRET = 'ccdce5af4dca9056f145c473d7193d11'
    REDIRECT_URL = 'http://127.0.0.1:8000/login/callback/' ####เปลี่ยน
    AUTH_URL = 'https://access.line.me/oauth2/v2.1/authorize'
    PROFILE_URL = 'https://api.line.me/v2/profile'
    TOKEN_URL = 'https://api.line.me/oauth2/v2.1/token'
    REVOKE_URL = 'https://api.line.me/oauth2/v2.1/revoke'
    VERIFYTOKEN_URL = 'https://api.line.me/oauth2/v2.1/verify'

    def get_link(self):
        #เป็นการสร้าง code csrf โดยดึงข้อมูล เวลาปัจจุบัน และสุ่มตัวเลข 512 บิต โดยใช้เป็น str และเข้สรหัสเวลากับตัวเลขนั้น เป็นรหัส utf 8 และรวมตัวเลขนั้นเข้าด้วยกัน และแฮชข้อมูลนั้น  
        session_state = hashlib.sha256(str(time.time()).encode() + str(random.getrandbits(512)).encode()).hexdigest()
        link = f"{self.AUTH_URL}?response_type=code&client_id={self.CLIENT_ID}&redirect_uri={self.REDIRECT_URL}&scope=profile%20openid%20email&state={session_state}"
        return link
    #เป็นกำหนดข้อมูลเพื่อขอรับข้อมูล token จากไลน์
    def token(self, code, state):

        header = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.REDIRECT_URL,
            "client_id": self.CLIENT_ID,
            "client_secret": self.CLIENT_SECRET
        }
        response = self.send_curl(self.TOKEN_URL, header, 'POST', data) #เป็นการเรียกใช้งานเพื่อส่งข้อมูลไป url ไลน์ทีกำหนด
        return json.loads(response)
    
    def profile_from_id_token(self, token):
        payload = token['id_token'].split('.')
        datas = {
            'access_token':  token['access_token'],
            'refresh_token': token['refresh_token'],
            'user_id':'',
            'name': '',
            'picture': '',
            'email': ''  }
        if len(payload) == 3: # header payload(ข้อมูลที่เกี่ยวกับผู้ใช้งา่น) signature 
            #print(payload)
            #เป็นการถอดรหัส ข้อมูล payload ที่้เป็นข้อมูล base64 ที่ได้รับมาเป็น json เพื่อรับข้อมูลของผู้ใช้งาน
            padded_payload = payload[1] + '=' * ((4 - len(payload[1]) % 4) % 4) #base ต้องมี len เป็นทวีคูณของ 4
            #เป็นการถอดรหัส base64 เป็นข้อมูลบิต และเเปลงเป็น utf 8 
            data = json.loads(base64.urlsafe_b64decode(padded_payload).decode('utf-8'))
            datas['user_id'] = data.get('sub', '')
            datas['name'] = data.get('name', '')
            datas['picture'] = data.get('picture', '')
            datas['email'] = data.get('email', '')
        return datas
    
    def send_curl(self, url, header, type, data=None):
        if header is not None:
            headers = header
        else:
            headers = {}

        if type.upper() == 'POST':
            response = requests.post(url, headers=headers, data=data) #ใช้ในการเปลี่ยนแปลงข้อมูลหรือใช้ในการเข้าสู่ระบบด้วยการส่งฟอร์มข้อมูล
        else:
            response = requests.get(url, headers=headers) #ใช้ในการร้องขอข้อมูลของผู้ใช้งานจากไลน์
        return response.text
