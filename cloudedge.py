import uuid
import requests
import json
import random
import time
from urllib.parse import urlencode
from authlib.jose import jwt
from crypto import *


class Cloudedge:

    BROWSER = "Mozilla/5.0 (Linux; U; Android 7.0; es-es; T10(E3C5) Build/NRD90M) AppleWebKit/533.1 (KHTML, like Gecko) Version/5.0 Mobile Safari/533.1"

    HOST = "apis-eu-frankfurt.cloudedge360.com"
    # API EndPoints
    LOGIN = "meari/app/login"
    LOGOUT = "ppstrongs/logOut.action"

    GET_DEVICE = "ppstrongs/getDevice.action"
    GET_ALERT_LIST = "pps/msg/alert/list"

    CLOUD_APP_ALERT_OSS_TOKEN = "cloud/app/alert-img/oss-down-token"

    APP_HOME_LIST = "v1/app/home/list"

    KEY = "bc29be30292a4309877807e101afbd51"
    SIGNATURE = "35a69fd1-6527-4566-b190-921f9a651488"

    def getHeaders(self,endpoint="meari/app/login",form=True):

        timestamp = str(round(time.time() * 1000))
        nonce = str(random.randint(100000, 999999))
        sign = "api=/ppstrongs//{endpoint}|X-Ca-Key={key}|X-Ca-Timestamp={timestamp}|X-Ca-Nonce={nonce}".format(endpoint=endpoint,key=KEY, timestamp=timestamp, nonce=nonce)

        headers = {
            "accept-language" : "es-ES;q=0.8",
            "user-agent" : self.BROWSER,
            "x-ca-key" : self.KEY,
            "x-ca-sign" : make_digest(sign, self.SIGNATURE),
            "x-ca-timestamp": timestamp,
            "x-ca-nonce": nonce
        }
        if form:
            headers["content-type"] = "application/x-www-form-urlencoded"

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

    def getNormalData(self):
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
        return data

    def logout(self):
        data = self.getNormalData()
        form = urlencode(data)
        response = self.session.post("https://%s/%s" % (self.HOST,self.LOGOUT), data=form, headers=self.getHeaders() )
        data = response.json()
        return data

    def getDevicesInfo(self):
        data = self.getNormalData()
        form = urlencode(data)
        response = self.session.post("https://%s/%s" % (self.HOST,self.GET_DEVICE), data=form, headers=self.getHeaders(endpoint=self.GET_DEVICE,form=True) )
        data = response.json()
        return data

    def getAlertList(self, day="20220725", deviceId=""):
        data = self.getNormalData()
        data["day"] = day
        data["deviceID"] = deviceId
        form = urlencode(data)
        response = self.session.post("https://%s/%s" % (self.HOST,self.GET_ALERT_LIST), data=form, headers=self.getHeaders(endpoint=self.GET_ALERT_LIST,form=True) )
        data = response.json()
        return data

    '''

    In dev...
    next it's a big TODO xD

    '''


    '''
    To get it working you just need to know how to manage a JWT.
    Target is -> "alg": "HS1"
    '''
    def getOssDownToken(self,deviceID):
        data = self.getNormalData()
        '''
        token = jwt.encode(
            payload = data,
            key = self.token, #getUserInfo().getUserToken()
            algorithm = "HMAC-SHA1" #it's too insecure, so we need other library or a vanilla implementation :'(
        )
        print(token)
        '''
        header = {
            "typ": "JWT",
            "alg": "HS1" #needs HMAC-SHA1 - HS1 and it's unsupported in current production implementations for insecure SHA1 algorithm
        }
        token = jwt.encode(header,data,self.token)
        print(token)
        headers = {
            "accept-language" : "es-ES,es;q=0.8",
            "user-agent" : self.BROWSER,
            "phonetype" : "a",
            "jwt" : token
        }
        form = {
            "deviceID" : deviceID
        }
        form = urlencode(form)
        response = self.session.get("https://%s/%s" % (self.HOST,self.CLOUD_APP_ALERT_OSS_TOKEN), data=form, headers=headers )
        data = response.json()
        return data

    def getAppHomeList(self):
        data = self.getNormalData()
        #form = urlencode(data)
        response = self.session.get("https://%s/%s" % (self.HOST,self.APP_HOME_LIST), data=data, headers=self.getHeaders(endpoint=self.APP_HOME_LIST,form=False) )
        data = response.json()
        return data
