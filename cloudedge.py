import uuid
import requests
import json
import random
import time
from urllib.parse import urlencode
from crypto import *


class Cloudedge:

    BROWSER = "Mozilla/5.0 (Linux; U; Android 7.0; es-es; T10(E3C5) Build/NRD90M) AppleWebKit/533.1 (KHTML, like Gecko) Version/5.0 Mobile Safari/533.1"

    HOST = "apis-eu-frankfurt.cloudedge360.com"
    # API EndPoints
    LOGIN = "meari/app/login"
    LOGOUT = "ppstrongs/logOut.action"

    GET_DEVICE = "ppstrongs/getDevice.action"
    GET_ALERT_LIST = "pps/msg/alert/list"
    PPS_MESSAGE_HAS = "pps/message/has"
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
            "userID" : str(self.userId),
            "phoneCode" : "34",
            "t" : str(round(time.time() * 1000)),
            "countryCode" : "ES",
            "phoneType" : "a",
            "appVer" : "4.3.3",
            "IngType" : "es",
            "userToken" : self.token,
            "sourceApp" : str(8),
            "appVerCode" : str(433)
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
        '''
        {...
            "alertMsg": [
                {
                    "imgUrl" : "https...",
                    "devLocalTime" : "YYYYMMDDHHmmSS",
                    "expire" : "-timestamp-",
                    "deviceId" : "..."
                }, ....
            ]
        }
        '''
        return data

    def hasMessages(self):
        data = self.getNormalData()
        form = urlencode(data)
        response = self.session.post("https://%s/%s" % (self.HOST,self.PPS_MESSAGE_HAS), data=data, headers=self.getHeaders(endpoint=self.PPS_MESSAGE_HAS,form=True) )
        data = response.json()
        return data

    def getOssDownToken(self,deviceID):
        data = self.getNormalData()
        token = jwt(data,self.token)
        data = {}
        if verify_jwt(token, self.token):
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
            response = self.session.get("https://%s/%s?%s" % (self.HOST,self.CLOUD_APP_ALERT_OSS_TOKEN,form), headers=headers )
            data = response.json()
        return data

    def getImage(self, url, expires, accessKey, signature, token):
        response = self.request.get("%s?Expires=%s&OSSAccessKeyId=%s&Signature=%s&security-token=%s" % (url,expires,accessKey,signature,token), stream=True)
        if response.status_code == 200:
            file_name = url[url.rfind("/")+1:]
            with open(file_name, 'wb') as out_file:
                for chunk in r:
                    f.write(chunk)



    '''
    In dev...
    next it's a big TODO xD
    '''
    def getAppHomeList(self):
        data = self.getNormalData()
        #form = urlencode(data)
        response = self.session.get("https://%s/%s" % (self.HOST,self.APP_HOME_LIST), data=data, headers=self.getHeaders(endpoint=self.APP_HOME_LIST,form=False) )
        data = response.json()
        return data
