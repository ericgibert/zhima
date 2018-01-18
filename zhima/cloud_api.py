#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Encapsulate the WeChat calls
https://github.com/QcloudApi/qcloudapi-sdk-python
pip install qcloudapi-sdk-python


### - attention: Python 2 library only: https://cloud.tencent.com/document/product/436/6275
### - pip install qcloud_cos_v4

"""
__author__ = "Eric Gibert"
__version__ = "1.0.20170113"
__email__ =  "ericgibert@yahoo.fr"
__license__ = "MIT"
#from qcloud_cos import CosClient, UploadFileRequest
#from wechatpy import WeChatClient
from QcloudApi.qcloudapi import QcloudApi
import json



class Wechat_API(object):
    def __init__(self):
        self.qdata = json.load(open("../Private/wechat.data"))
        # params = {'Limit':1}
        # 接口参数
        module = 'cvm'
        action = 'DescribeInstances'
        action_params = {
            'limit':1,
        }
        self.config = {
            'Region': 'sh',
            'secretId': self.qdata["Eric"]["SecretId"],
            'secretKey': self.qdata["Eric"]["SecretKey"],
            'method': 'GET',
            #'Version':'2017-03-20',
            'SignatureMethod': 'HmacSHA1'
        }
        try:
            service = QcloudApi(module, self.config)
            # 生成请求的URL，不发起请求
            # print(service.generateUrl(action, action_params))
            # 调用接口，发起请求
            response=json.loads(service.call(action, action_params).decode("utf-8"))
            if response["code"]:
                print(response)
        except Exception as e:
            import traceback
            print('traceback.format_exc():\n%s' % traceback.format_exc())
    
        

    def upload(self, source, target):
        """Upload a local file to qcloud.tencent.com server"""
        module = 'cdn'
        action = 'UploadCdnEntity'
        params = {
            'entityFileName': target,
            'entityFile': source
        }
        service = QcloudApi(module, self.config)
        # print(('URL:\n' + service.generateUrl(action, params)))
        response=json.loads(service.call(action, params).decode("utf-8"))
        if response["code"]:
            print(response["code"], response["codeDesc"], response["message"])

if __name__ == "__main__":
    wc = Wechat_API()
    wc.upload('../Private/test_file.txt', '/test_file.txt')

