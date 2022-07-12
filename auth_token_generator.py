import uuid as uuid_library
import hmac
import json
import hashlib
from datetime import datetime
import requests
import six.moves.urllib as urllib
from dotenv import load_dotenv
load_dotenv()


USERNAME, PASSWORD = os.getenv("ig_username"), os.getenv("ig_password") # Replace the user credentials here!



LOGIN_URL = 'https://i.instagram.com/api/v1/accounts/login/'
REQUEST_HEADERS = { 'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8' }
IG_SIG_KEY = '99e16edcca71d7c1f3fd74d447f6281bd5253a623000a55ed0b60014467a53b1'


DEVICE = {
    'instagram_version': '26.0.0.10.86',
    'android_version': 24,
    'android_release': '7.0',
    'dpi': '640dpi',
    'resolution': '1440x2560',
    'manufacturer': 'HUAWEI',
    'device': 'LON-L29',
    'model': 'HWLON',
    'cpu': 'hi3660'
}

USER_AGENT_BASE = (
    'Instagram {instagram_version} '
    'Android ({android_version}/{android_release}; '
    '{dpi}; {resolution}; {manufacturer}; '
    '{device}; {model}; {cpu}; en_US)'
)

user_agent = USER_AGENT_BASE.format(**DEVICE) # just insert params


def hex_digest(*args):
    m = hashlib.md5()
    m.update(b''.join([arg.encode('utf-8') for arg in args]))
    return m.hexdigest()

def generate_device_id(seed):
    volatile_seed = "12345"  # Important ! :) :)
    m = hashlib.md5()
    m.update(seed.encode('utf-8') + volatile_seed.encode('utf-8'))
    return 'android-' + m.hexdigest()[:16]

def generate_uuid():
    return str(uuid_library.uuid4())

def generate_signature(data):
    body = hmac.new(IG_SIG_KEY.encode('utf-8'), data.encode('utf-8'),
                    hashlib.sha256).hexdigest() + '.' + urllib.parse.quote(data)
    signature = 'ig_sig_key_version=4&signed_body={body}'
    # signature = 'signed_body={body}'
    return signature.format(body=body)



def login(data):
    url = "https://i.instagram.com/api/v1/accounts/login/"

    payload = data
    
    headers = {
    'User-Agent': 'Instagram 212.0.0.38.119 Android (31/12; 450dpi; 1080x2327; samsung; SM-G985F; y2s; exynos990; en_GB; 329675731)',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Accept-Encoding': 'gzip, deflate',
    'Host': 'i.instagram.com',
    'X-FB-HTTP-Engine': 'Liger',
    'X-FB-Client-IP': 'True',
    'X-FB-Server-Cluster': 'True',
    'Connection': 'close',
    'Content-Length': '1038'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    # print(response.content)
    assert response.status_code == 200
    auth = response.headers['ig-set-authorization']

    auth = auth#.split(":")[-1]
    # print("auth", auth)
    print(auth)
    return auth


phone_id = generate_uuid()
uuid = generate_uuid()
device_id = generate_device_id(hex_digest(USERNAME, USERNAME))




import time

def current_milli_time():
    return round(time.time() )

time = current_milli_time()

data = {
    "jazoest":"22292",
    "country_codes":"[{\"country_code\":\"44\",\"source\":[\"default\"]}]",
    "phone_id":phone_id,
    "enc_password":"#PWD_INSTAGRAM:0:{}:{}".format(time,PASSWORD),
    "username": USERNAME,
    "adid":"6b57fe85-7222-49c4-85fe-a77cb116e7a6",
    "guid":uuid,
    "device_id":device_id,
    "google_tokens":"[]",
    "login_attempt_count":"0"
}

login(data)
