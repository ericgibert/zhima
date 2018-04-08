"""

Test the APIs developped for John's Wechat application

- prerequisite:  pip install requests   in the virtual environment
- http_view.py is running in bg

"""
import unittest
import requests
from datetime import datetime
from zhima.model_db import Database

class TestApi(unittest.TestCase):
    """
    Perform various API calls to test their responses
    """
    base_url = "http://127.0.0.1:8080/api/v1.0"

    def test_get_by_openid_1(self):
        """GET the Admin profile - openid=1"""
        url = "{}/member/openid/{}".format(self.base_url, 1)
        response = requests.get(url)
        self.assertEqual(200, response.status_code)
        admin = response.json()
        print("test_get_by_openid_1: JSON:", admin)
        self.assertEqual(admin['basicInfo']['nickName'], "admin")

    def test_get_by_openid_unknown(self):
        """GET unknown user to check the returned respose object in error"""
        url = "{}/member/openid/{}".format(self.base_url, "unknown_member")
        response = requests.get(url)
        self.assertEqual(200, response.status_code)
        unknown = response.json()
        print("test_get_by_openid_unknown: JSON:", unknown)
        self.assertEqual('1001', unknown['errno'])


    def test_add_new_member(self, keep_member=False):
        """POST new member profile"""
        url = "{}/member/new".format(self.base_url)
        openid = datetime.now().strftime('%Y%m%d%H%M%S.%f')
        minimum_data = {
                "openid": openid,
                "avatarUrl": "https://wx.qlogo.cn/mmopen/vi_32/GPm0HkJtcIsWkZmVNaxJP19ibl1g2YJTEibglP0UibOZstaRN1lbuMavu1a1Y795p6J1vHz0bM27icibCiat9ERricyng/0",
                'basicInfo':{
                    'nickName': "test_" + openid,
                    'country': "China",
                    'gender': 1,
                    'language': "zh_CN",
                }
        }
        response = requests.post(url, json=minimum_data)
        self.assertEqual(200, response.status_code)
        result = response.json()
        print(result)
        self.assertEqual('1000', result['errno'])
        new_id = result['data']['new_id']
        if not keep_member: self.delete_user(new_id)
        return new_id

    def test_add_new_member_with_payment(self, keep_member=False):
        """POST new member profile with a new payment record"""
        url = "{}/member/new".format(self.base_url)
        openid = datetime.now().strftime('%Y%m%d%H%M%S.%f')
        minimum_data = {
            "openid": openid,
            "avatarUrl": "https://wx.qlogo.cn/mmopen/vi_32/GPm0HkJtcIsWkZmVNaxJP19ibl1g2YJTEibglP0UibOZstaRN1lbuMavu1a1Y795p6J1vHz0bM27icibCiat9ERricyng/0",
            'basicInfo':{
                'nickName': "test_" + openid,
            },
            'paymentInfo': {
                'paidTime': '201803121929',
                'payIndex': '9cu293820xxjfiuewfdsfdse32',
                'CNYAmount': 3200.00,
            }
        }
        response = requests.post(url, json=minimum_data)
        self.assertEqual(200, response.status_code)
        result = response.json()
        print(result)
        self.assertEqual('1000', result['errno'])
        new_id = result['data']['new_id']
        if not keep_member: self.delete_user(new_id)
        return new_id

    def test_upd_member_profile(self, keep_member=False):
        # create a member
        new_id = self.test_add_new_member(keep_member=True)
        # call update API
        url = "{}/member/openid/{}".format(self.base_url, new_id)
        patch = {
            "op": "update",
            "data": {
                "avatarUrl": "https://new/link/to_avatar.html",
                'nickName': "new_nickName"
            }
        }
        response = requests.patch(url, json=patch)
        self.assertEqual(200, response.status_code)
        result = response.json()
        print(result)
        if not keep_member: self.delete_user(new_id)


    def delete_user(self, id):
        db = Database()
        db.execute_sql("DELETE from users where id=%s", (id, ))
        print("deleted row", id)

if __name__ == '__main__':
    unittest.main()