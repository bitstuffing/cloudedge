import pyDes
import hashlib
import hmac
import base64
import json
import hashlib
from datetime import datetime, timedelta


KEY = "123456781234567812345678"
IV = "01234567"


def triple_des_encrypt(text):
    des = pyDes.triple_des(key=KEY, mode=pyDes.CBC, padmode=pyDes.PAD_PKCS5, IV=IV)
    return base64.b64encode(des.encrypt(text)).decode()


def make_digest(message, key):
    key = bytes(key, "UTF-8")
    message = bytes(message, "UTF-8")

    digester = hmac.new(key, message, hashlib.sha1)
    signature1 = digester.digest()

    signature2 = base64.urlsafe_b64encode(signature1)
    return str(signature2, "UTF-8")


def make_digest_hex(message, key):
    key = bytes(key, "UTF-8")
    message = bytes(message, "UTF-8")

    digester = hmac.new(key, message, hashlib.sha1)
    return digester.digest().hex().upper()

def base64url_encode(input: bytes):
    return base64.urlsafe_b64encode(input).decode('utf-8').replace('=','')

'''
Custom implementation for SHA1 v1
'''
def jwt(payload, token):

    segments = []

    header = {
        "typ": "JWT",
        "alg": "HS1"
    }

    json_header = json.dumps(header, separators=(",",":")).encode()
    json_payload = json.dumps(payload, separators=(",",":")).encode()

    segments.append(base64url_encode(json_header))
    segments.append(base64url_encode(json_payload))

    signing_input = ".".join(segments).encode()
    key = token.encode()
    signature = hmac.new(key, signing_input, hashlib.sha1).digest()

    segments.append(base64url_encode(signature))

    encoded_string = ".".join(segments)

    return encoded_string

'''
Custom v2 devs for JWT

def base64url_decode(input):
    return base64.urlsafe_b64decode(input+'==')

def base64url_encode(input):
    stringAsBytes = input.encode('ascii')
    stringAsBase64 = base64.urlsafe_b64encode(stringAsBytes).decode('utf-8').replace('=','')
    return stringAsBase64

def jwt(payload, secret_key):
    header = {
        "alg": "HS1",
        "typ": "JWT"
    }
    total_params = str(base64url_encode(json.dumps(header))) + '.' + str(base64url_encode(json.dumps(payload)))
    signature = hmac.new(secret_key.encode(), total_params.encode(), hashlib.sha1).hexdigest()
    token = total_params + '.' + str(base64url_encode(signature))
    return token
'''
