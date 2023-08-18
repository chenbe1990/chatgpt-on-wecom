#!/usr/bin/python3
# -*- coding:utf-8 -*-
# from fileupload import seve_file
from voice.xunfei.fileupload import seve_file
import requests
import datetime
import hashlib
import base64
import hmac
import json
import os
import re
#-----------------------------
from bridge.reply import Reply, ReplyType
from common.log import logger
from config import conf
from voice.voice import Voice

# path_pwd = os.path.split(os.path.realpath(__file__))[0]
# os.chdir(path_pwd)


# 创建和查询
class XunfeiVoice(Voice):

    def __init__(self):
        # 以下为POST请求
        self.Host = "ost-api.xfyun.cn"
        self.RequestUriCreate = "/v2/ost/pro_create"
        self.RequestUriQuery = "/v2/ost/query"
        # 设置url
        if re.match("^\d", self.Host):
            self.urlCreate = "http://" + self.Host + self.RequestUriCreate
            self.urlQuery = "http://" + self.Host + self.RequestUriQuery
        else:
            self.urlCreate = "https://" + self.Host + self.RequestUriCreate
            self.urlQuery = "https://" + self.Host + self.RequestUriQuery
        self.HttpMethod = "POST"
        # self.APPID = appid
        self.Algorithm = "hmac-sha256"
        self.HttpProto = "HTTP/1.1"

        #self.UserName = apikey
        # self.Secret = apisecret
        #self.apikey = apikey
        # self.file_path = file_path
        self.APPID =  str(conf().get("xunfei_app_id"))
        self.UserName = str(conf().get("xunfei_api_key"))
        # self.apikey = str(conf().get("xunfei_api_key"))
        self.Secret = str(conf().get("xunfei_secret_key"))


        # 设置当前时间
        cur_time_utc = datetime.datetime.utcnow()
        self.Date = self.httpdate(cur_time_utc)
        # 设置测试音频文件
        self.BusinessArgsCreate = {
            "language": "zh_cn",
            "accent": "mandarin",
            "domain": "pro_ost_ed",
            # "callback_url": "http://IP:端口号/xxx/"
        }

    def img_read(self, path):
        with open(path, 'rb') as fo:
            return fo.read()

    def hashlib_256(self, res):
        m = hashlib.sha256(bytes(res.encode(encoding='utf-8'))).digest()
        result = "SHA-256=" + base64.b64encode(m).decode(encoding='utf-8')
        return result

    def httpdate(self, dt):
        """
        Return a string representation of a date according to RFC 1123
        (HTTP/1.1).
        The supplied date must be in UTC.
        """
        weekday = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][dt.weekday()]
        month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
                 "Oct", "Nov", "Dec"][dt.month - 1]
        return "%s, %02d %s %04d %02d:%02d:%02d GMT" % (weekday, dt.day, month,
                                                        dt.year, dt.hour, dt.minute, dt.second)

    def generateSignature(self, digest, uri):
        signature_str = "host: " + self.Host + "\n"
        signature_str += "date: " + self.Date + "\n"
        signature_str += self.HttpMethod + " " + uri \
                         + " " + self.HttpProto + "\n"
        signature_str += "digest: " + digest
        signature = hmac.new(bytes(self.Secret.encode('utf-8')),
                             bytes(signature_str.encode('utf-8')),
                             digestmod=hashlib.sha256).digest()
        result = base64.b64encode(signature)
        return result.decode(encoding='utf-8')

    def init_header(self, data, uri):
        digest = self.hashlib_256(data)
        sign = self.generateSignature(digest, uri)
        auth_header = 'api_key="%s",algorithm="%s", ' \
                      'headers="host date request-line digest", ' \
                      'signature="%s"' \
                      % (self.UserName, self.Algorithm, sign)
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Method": "POST",
            "Host": self.Host,
            "Date": self.Date,
            "Digest": digest,
            "Authorization": auth_header
        }
        return headers

    def get_create_body(self, fileurl):
        post_data = {
            "common": {"app_id": self.APPID},
            "business": self.BusinessArgsCreate,
            "data": {
                "audio_src": "http",
                "audio_url": fileurl,
                "encoding": "raw"
            }
        }
        body = json.dumps(post_data)
        return body

    def get_query_body(self, task_id):
        post_data = {
            "common": {"app_id": self.APPID},
            "business": {
                "task_id": task_id,
            },
        }
        body = json.dumps(post_data)
        return body

    def call(self, url, body, headers):

        try:
            response = requests.post(url, data=body, headers=headers, timeout=8)
            status_code = response.status_code
            interval = response.elapsed.total_seconds()
            if status_code != 200:
                info = response.content
                return info
            else:
                resp_data = json.loads(response.text)
                return resp_data
        except Exception as e:
            print("Exception ：%s" % e)

    def task_create(self):
        body = self.get_create_body(self.fileurl)
        headers_create = self.init_header(body, self.RequestUriCreate)
        task_id = self.call(self.urlCreate, body, headers_create)
        print(task_id)
        return task_id

    def task_query(self, task_id):
        if task_id:
            body = self.get_create_body(self.fileurl)
            query_body = self.get_query_body(task_id)
            headers_query = self.init_header(body, self.RequestUriQuery)
            result = self.call(self.urlQuery, query_body, headers_query)
            return result
    #修改
    def get_fileurl(self,file_path):
        #self.file_path = file_path   ##########!!!!!!!!!!
        # 文件上传
        api = seve_file.SeveFile(app_id=self.APPID, api_key=self.UserName, api_secret=self.Secret, upload_file_path=file_path)
        file_total_size = os.path.getsize(file_path)
        if file_total_size < 31457280:
            print("-----不使用分块上传-----")
            self.fileurl = api.gene_params('/upload')['data']['url']
        else:
            print("-----使用分块上传-----")
            self.fileurl = api.gene_params('/mpupload/upload')
        return self.fileurl

    def get_resule(self):

        # 创建订单
        print("\n------ 创建任务 -------")
        task_id = self.task_create()['data']['task_id']

        # 查询任务
        print("\n------ 查询任务 -------")
        print("任务转写中······")
        while True:
            result = self.task_query(task_id)
            if isinstance(result, dict) and result['data']['task_status'] != '1' and result['data']['task_status'] != '2':
                # 新添加
                result = result['data']['result']['lattice'][0]['json_1best']['st']['rt'][0]['ws']
                ws = [c['w'] for item in result for c in item['cw']]
                result = ''.join(ws)
                logger.info("xuinfei语音识别完成: {}".format(result))
                reply = Reply(ReplyType.TEXT, result)
                break
            elif isinstance(result, bytes):
                logger.info("xuinfei语音识别出错了: {}".format(result))
                reply = Reply(ReplyType.ERROR, "百度语音识别出错了；{0}".format(result))
                break
        return reply
    # def get_result(self):
    #
    #     # 创建订单
    #     print("\n------ 创建任务 -------")
    #     task_id = self.task_create()['data']['task_id']
    #     # 查询任务
    #     print("\n------ 查询任务 -------")
    #     print("任务转写中······")
    #     while True:
    #         result = self.task_query(task_id)
    #         if isinstance(result, dict) and result['data']['task_status'] != '1' and result['data'][
    #             'task_status'] != '2':
    #             #新添加
    #             result = result['data']['result']['lattice'][0]['json_1best']['st']['rt'][0]['ws']
    #             ws = [c['w'] for item in result for c in item['cw']]
    #             result = ''.join(ws)
    #             logger.info("xuinfei语音识别完成: {}".format(result))
    #             reply = Reply(ReplyType.TEXT, result)
    #             break
    #         elif isinstance(result, bytes):
    #             logger.info("xuinfei语音识别出错了: {}".format(result))
    #             reply = Reply(ReplyType.ERROR, "百度语音识别出错了；{0}".format(result))
    #             break
    #     return  result
    def voiceToText(self, voice_file):
        # 识别本地文件
        # logger.debug("[xunfei] voice file name={}".format(voice_file))

        # #self.APPID, self.UserName, self.Secret,
        # gClass01 = XunfeiVoice( )
        # gClass01.get_fileurl(voice_file) #上传文件
        # text= gClass01.get_result()  #发送语音文件到讯飞返回文字
        #新添加-------------
        logger.debug("[xunfei] voice file name={}".format(voice_file))
        gClass01 = XunfeiVoice( )
        gClass01.get_fileurl(voice_file) #上传文件
        reply = gClass01.get_resule()
        return  reply


