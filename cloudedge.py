import uuid
import requests
import json
import random
import time
from urllib.parse import urlencode
from crypto import *


class Cloudedge:

    HOST = "apis-eu-frankfurt.cloudedge360.com"
    # API EndPoints
    LOGIN = "meari/app/login"
    LOGOUT = "ppstrongs/logOut.action"

    KEY = "bc29be30292a4309877807e101afbd51"

    def getHeaders(self):

        timestamp = str(round(time.time() * 1000))
        nonce = str(random.randint(100000, 999999))
        sign = "api=/ppstrongs//meari/app/login|X-Ca-Key={key}|X-Ca-Timestamp={timestamp}|X-Ca-Nonce={nonce}".format(key=KEY, timestamp=timestamp, nonce=nonce)

        headers = {
            "accept-language" : "es-ES;q=0.8",
            "user-agent" : "Mozilla/5.0 (Linux; U; Android 7.0; es-es; T10(E3C5) Build/NRD90M) AppleWebKit/533.1 (KHTML, like Gecko) Version/5.0 Mobile Safari/533.1",
            "x-ca-key" : KEY,
            "x-ca-sign" : make_digest(sign, "35a69fd1-6527-4566-b190-921f9a651488"),
            "x-ca-timestamp": timestamp,
            "x-ca-nonce": nonce,
            "content-type": "application/x-www-form-urlencoded",
        }

        return headers

    def __init__(self):
        self.session = requests.Session()


    def login(self, user, password):

        data = {
            "phoneType": "a",
            "sourceApp": 8,
            "appVer": "4.3.3",
            "iotType": 3,
            "lngType": "es",
            "userAccount": user,
            "password": triple_des_encrypt(password),
            "phoneCode": "+34",
            "appVerCode": 433,
            "t": str(round(time.time() * 1000)),
            "countryCode": "ES",
        }

        form = urlencode(data)

        response = self.session.post("https://%s/%s" % (self.HOST,self.LOGIN), data=form, headers=self.getHeaders() )
        data = response.json()
        self.userId = data["result"]["userID"]
        self.token = data["result"]["userToken"]
        return data


    def logout(self):
        data = {
            "userID" : self.userId,
            "phoneCode" : "34",
            "t" : str(round(time.time() * 1000)),
            "countryCode" : "ES",
            "phoneType" : "a",
            "appVer" : "4.3.3",
            "IngType" : "es",
            "userToken" : self.token,
            "sourceApp" : 8,
            "appVerCode" : 433
        }

        form = urlencode(data)
        response = self.session.post("https://%s/%s" % (self.HOST,self.LOGOUT), data=form, headers=self.getHeaders() )
        data = response.json()
        return data
