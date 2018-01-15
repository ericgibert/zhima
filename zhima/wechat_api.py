#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Encapsulate the WeChat calls

- attention: Python 2 library only: https://cloud.tencent.com/document/product/436/6275
- pip install qcloud_cos_v4

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
        with open("../Private/wechat.data") as fin:
            self.app_id = fin.readline().strip() #.decode("utf-8")
            self.app_secret = fin.readline().strip() #.decode("utf-8")
        region = "shanghai"  # # 替换为用户的region，目前可以为 shanghai/guangzhou
        #self.cos_client = CosClient(1000, self.app_id, self.app_secret, region)
        config = {'Region':'shanghai', 'secretId':self.app_id, 'secretKey':self.app_secret, 'Version':'2017-03-20'}
        params = {'Limit':1}
        # 接口参数
        module = 'cvm'
        action = 'DescribeInstances'
        action_params = {
            'limit':1,
        }
        self.config = {
            'Region': 'sh',
            'secretId': self.app_secret,
            'secretKey': self.app_id,
            'method': 'GET',
            #'Version':'2017-03-20',
            'SignatureMethod': 'HmacSHA1'
        }
        try:
            service = QcloudApi(module, self.config)

            # 请求前可以通过下面几个方法重新设置请求的secretId/secretKey/region/method/SignatureMethod参数
            # 重新设置请求的secretId
            secretId = self.app_secret
            service.setSecretId(secretId)
            # 重新设置请求的secretKey
            secretKey = self.app_id
            service.setSecretKey(secretKey)
##            # 重新设置请求的region
##            region = 'ap-shanghai'
##            service.setRegion(region)
##            # 重新设置请求的method
##            method = 'POST'
##            service.setRequestMethod(method)
##            # 重新设置请求的SignatureMethod
##            SignatureMethod = 'HmacSHA256'
##            service.setSignatureMethod(SignatureMethod)

            # 生成请求的URL，不发起请求
            print(service.generateUrl(action, action_params))
            # 调用接口，发起请求
            response=json.loads(service.call(action, action_params).decode("utf-8"))
            print(response)
        except Exception as e:
            import traceback
            print('traceback.format_exc():\n%s' % traceback.format_exc())
    
        

    def upload(self, source=None, target=None):
        """Upload a local file to Wechat server"""
        module = 'cdn'
        action = 'UploadCdnEntity'
        config = {
            'secretId': self.app_id,
            'secretKey': self.app_secret,
            'Region': 'ap-shanghai',
            'method': 'post',
            'SignatureMethod': 'HmacSHA1'
        }
        params = {
            'entityFileName': 'test_file.txt',
            'entityFile': '../Private/test_file.txt'
        }
        service = QcloudApi(module, config)
        print(('URL:\n' + service.generateUrl(action, params)))
        response=json.loads(service.call(action, params).decode("utf-8"))
        print(response["code"], response["codeDesc"], response["message"])
##        bucket = u''   # 设置要操作的bucket
##        if target[0]!='/': target = '/'+target
##        request = UploadFileRequest(bucket, target, source)
##        upload_file_ret = self.cos_client.upload_file(request)
##        return upload_file_ret


if __name__ == "__main__":
    wc = Wechat_API()
    print(wc.app_id)
    print(wc.app_secret)
    wc.upload()
    #print("File uploaded:", wc.upload(u'../Private/test_file.txt', u'test_file.txt'))


    #ticket="https://u.wechat.com/ICOI-lxiB6M2J10OK-8q0BQ"
    #client = WeChatClient(wc.app_id, wc.app_secret)
    #url = client.qrcode.show(ticket)
    #print(url)
