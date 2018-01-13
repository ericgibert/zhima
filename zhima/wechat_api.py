#!/usr/bin/env python2
# -*- coding: utf-8 -*-

""" Encapsulate the WeChat calls

- attention: Python 2 library only: https://cloud.tencent.com/document/product/436/6275
- pip install qcloud_cos_v4

"""
__author__ = "Eric Gibert"
__version__ = "1.0.20170113"
__email__ =  "ericgibert@yahoo.fr"
__license__ = "MIT"

from qcloud_cos import CosClient, UploadFileRequest

class Wechat_API(object):
    def __init__(self):
        with open("../Private/wechat.data") as fin:
            self.app_id = fin.readline().strip().decode("utf-8")
            self.app_secret = fin.readline().strip().decode("utf-8")
        region = "shanghai"  # # 替换为用户的region，目前可以为 shanghai/guangzhou
        self.cos_client = CosClient(1000, self.app_id, self.app_secret, region)

    def upload(self, source, target):
        """Upload a local file to Wechat server"""
        bucket = u''   # 设置要操作的bucket
        if target[0]!='/': target = '/'+target
        request = UploadFileRequest(bucket, target, source)
        upload_file_ret = self.cos_client.upload_file(request)
        return upload_file_ret


if __name__ == "__main__":
    wc = Wechat_API()
    print(wc.app_id)
    print(wc.app_secret)
    print("File uploaded:", wc.upload(u'../Private/test_file.txt', u'test_file.txt'))