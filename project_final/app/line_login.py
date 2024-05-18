import hashlib
import random
import time
import requests
import json
import base64

class LineLogin:
    CLIENT_ID = '2002071461'
    CLIENT_SECRET = 'ccdce5af4dca9056f145c473d7193d11'
    REDIRECT_URL = 'https://684a-49-228-41-242.ngrok-free.app/login/callback/'

    AUTH_URL = 'https://access.line.me/oauth2/v2.1/authorize'
    PROFILE_URL = 'https://api.line.me/v2/profile'
    TOKEN_URL = 'https://api.line.me/oauth2/v2.1/token'
    REVOKE_URL = 'https://api.line.me/oauth2/v2.1/revoke'
    VERIFYTOKEN_URL = 'https://api.line.me/oauth2/v2.1/verify'

    def get_link(self):
        session_state = hashlib.sha256(str(time.time()).encode() + str(random.getrandbits(512)).encode()).hexdigest()
        link = f"{self.AUTH_URL}?response_type=code&client_id={self.CLIENT_ID}&redirect_uri={self.REDIRECT_URL}&scope=profile%20openid%20email&state={session_state}"
        return link
    '''
    def refresh(self, token):
        header = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            "grant_type": "refresh_token",
            "refresh_token": token,
            "client_id": self.CLIENT_ID,
            "client_secret": self.CLIENT_SECRET
        }
        response = self.send_curl(self.TOKEN_URL, header, 'POST', data)
        return json.loads(response)
    '''
    def token(self, code, state):
        header = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.REDIRECT_URL,
            "client_id": self.CLIENT_ID,
            "client_secret": self.CLIENT_SECRET
        }
        response = self.send_curl(self.TOKEN_URL, header, 'POST', data)
        return json.loads(response)

    def profile_from_id_token(self, token):
        print(token)
        print(',,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,')
        payload = token['id_token'].split('.')
        datas = {
            'access_token':  token['access_token'],
            'refresh_token': token['refresh_token'],
            'user_id':'',
            'name': '',
            'picture': '',
            'email': ''
        }

        if len(payload) == 3:
            # Add padding to make the length a multiple of 4
            padded_payload = payload[1] + '=' * ((4 - len(payload[1]) % 4) % 4)
            data = json.loads(base64.urlsafe_b64decode(padded_payload).decode('utf-8'))
            print('data', data)
            datas['user_id'] = data.get('sub', '')
            datas['name'] = data.get('name', '')
            datas['picture'] = data.get('picture', '')
            datas['email'] = data.get('email', '')
        print(datas)
        return datas

    def send_curl(self, url, header, type, data=None):
        if header is not None:
            headers = header
        else:
            headers = {}

        if type.upper() == 'POST':
            response = requests.post(url, headers=headers, data=data)
        else:
            response = requests.get(url, headers=headers)

        return response.text
