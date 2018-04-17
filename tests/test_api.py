"""

Test the APIs developped for John's Wechat application

- prerequisite:  pip install requests   in the virtual environment
- http_view.py is running in bg

"""
import unittest
import requests
from datetime import datetime
from member import Member
from transaction import Transaction

class TestApi(unittest.TestCase):
    """
    Perform various API calls to test their responses
    """
    base_url = "http://127.0.0.1:8080/api/v1.0"

    def print_JSON(self, obj, tab_level=1, title=""):
        """Display a JSON object to allow easy reading"""
        if tab_level == 1: print('\n{}\n{{'.format(title))
        for k, v in obj.items():
            if isinstance(v, dict):
                print('\t'*tab_level, "'{}':".format(k))
                print('\t'*tab_level, '{')
                self.print_JSON(v, tab_level+1)
                print('\t'*tab_level, '}')
            else:
                print('\t'*tab_level, "'{}': '{}'".format(k, v))
        if tab_level == 1: print('}\n')

    def test_get_by_openid_1(self):
        """GET the Admin profile - openid=1"""
        url = "{}/member/openid/{}".format(self.base_url, 1)
        print("Path:", url)
        response = requests.get(url)
        self.assertEqual(200, response.status_code)
        admin = response.json()
        self.print_JSON(admin, title="test_get_by_openid_1:")
        self.assertEqual(admin['basicInfo']['nickName'], "admin")

    def test_get_by_openid_unknown(self):
        """Negative Test: GET unknown Member to check the returned response object in error"""
        unk_member = "unknown_member____"
        url = "{}/member/openid/{}".format(self.base_url, unk_member)
        print("Path:", url)
        response = requests.get(url)
        self.assertEqual(200, response.status_code)
        unknown = response.json()
        self.print_JSON(unknown, title="test_get_by_openid_unknown:")
        self.assertEqual(1999, int(unknown['errno']))
        self.assertEqual(unk_member, unknown['data']['id'])


    def test_add_new_member(self, keep_member=False):
        """POST new member profile"""
        url = "{}/member/new".format(self.base_url)
        print("Path:", url)
        openid = datetime.now().strftime('%Y%m%d%H%M%S.%f')
        minimum_data = {
                "openid": openid,
                "avatarUrl": "https://wx.qlogo.cn/mmopen/vi_32/GPm0HkJtcIsWkZmVNaxJP19ibl1g2YJTEibglP0UibOZstaRN1lbuMavu1a1Y795p6J1vHz0bM27icibCiat9ERricyng/0",
                'basicInfo':{
                    'nickName': "test_" + openid,
                    'country': "China",
                    'gender': 1,
                    'language': "zh_CN",
                },
            'memberInfo':{
                'tags': 'Master'
            }

        }
        response = requests.post(url, json=minimum_data)
        self.assertEqual(200, response.status_code)
        result = response.json()
        self.print_JSON(result, title="test_add_new_member:")
        self.assertEqual('1000', result['errno'])
        new_id = result['data']['new_id']
        member = Member(new_id)
        print("Created as [role:", member['role'], "] with status:", member["status"])
        self.assertEqual('NOT_OK', member["status"])
        if not keep_member: self.delete_member(new_id)
        return new_id

    def test_add_new_member_with_payment(self, keep_member=False):
        """POST new member profile with a new payment record"""
        url = "{}/member/new".format(self.base_url)
        print("Path:", url)
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
        self.print_JSON(result, title="test_add_new_member_with_payment:")
        self.assertEqual('1000', result['errno'])
        new_id = result['data']['new_id']
        member = Member(new_id)
        print("Created as [role:", member['role'], "] with status:", member["status"])
        self.assertEqual('OK', member["status"])
        print("Transaction:", member.transactions)
        if not keep_member: self.delete_member(new_id)
        return new_id

    def test_upd_member_profile(self, keep_member=False):
        """Positive test: Update a new Member"""
        # create a member
        new_id = self.test_add_new_member(keep_member=True)
        member = Member(id=new_id)
        current_avatarUrl = member["avatar_url"]
        current_username = member["username"]
        # call update API
        url = "{}/member/openid/{}".format(self.base_url, member["openid"])
        print("Path:", url)
        patch = {
            "op": "update",
            "data": {
                "avatarUrl": "https://new/link/to_avatar.html",
                'nickName': "new_nickName",
                'tags': 5
            }
        }
        response = requests.patch(url, json=patch)
        self.assertEqual(200, response.status_code)
        result = response.json()
        self.print_JSON(result, title="test_upd_member_profile:")
        # fetch record again
        member = Member(id=new_id)
        upd_avatarUrl = member["avatar_url"]
        upd_username = member["username"]
        self.assertNotEqual(current_avatarUrl, upd_avatarUrl)
        self.assertNotEqual(current_username, upd_username)
        self.assertEqual("new_nickName", upd_username)
        if not keep_member: self.delete_member(new_id)


    def test_upd_unknown_member_profile(self, keep_member=False):
        """Negative Test: try to update an unknown Member"""
        # call update API
        unk_openid="unknown_openid_____"
        url = "{}/member/openid/{}".format(self.base_url, unk_openid)
        print("Path:", url)
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
        self.print_JSON(result, title="test_upd_unknown_member_profile:")
        self.assertEqual(1999, int(result['errno']))
        self.assertEqual(unk_openid, result['data']['id'])

    def test_upd_unknown_field_member(self, keep_member=False):
        """
        Positive Test: try to update an unknown field for a given Member
        The fields not declared in Member_Api.API_MAPPING_TO_DB are ignored
        """
        # create a member
        new_id = self.test_add_new_member(keep_member=True)
        member = Member(id=new_id)
        # call update API
        url = "{}/member/openid/{}".format(self.base_url, member["openid"])
        print("Path:", url)
        patch = {
            "op": "update",
            "data": {
                "avatarUrl": "https://new/link/to_avatar.html",
                'nickName': "new_nickName",
                "unknow_field___": "incorrect field"
            }
        }
        response = requests.patch(url, json=patch)
        self.assertEqual(200, response.status_code)
        result = response.json()
        self.print_JSON(result, title="test_upd_unknown_field_member:")
        self.assertEqual(1000, int(result['errno']))
        # self.assertEqual(new_id, result['data']['id'])
        if not keep_member: self.delete_member(new_id)

    def test_add_payment(self, keep_member=False):
        """Positive test: add a payment to a new Member"""
        # create a member
        new_id = self.test_add_new_member(keep_member=True)
        member = Member(id=new_id)
        current_avatarUrl = member["avatar_url"]
        current_username = member["username"]
        # call update API
        url = "{}/member/openid/{}".format(self.base_url, member["openid"])
        print("Path:", url)
        patch = {
            "op": "add",
            "data": {
                'paidTime': datetime.now().strftime('%Y%m%d%H%M'), # '201803121929',
                'payIndex': 'this_is_craaaazy_____',
                'CNYAmount': 123.45,
                'payType': 'DONATION'
            }
        }
        response = requests.patch(url, json=patch)
        self.assertEqual(200, response.status_code)
        result = response.json()
        self.print_JSON(result, title="test_add_payment:")
        # fetch record again
        member = Member(id=new_id)
        print(member.transactions)
        if not keep_member: self.delete_member(new_id)

    def test_door_opening(self):
        """opens the door for 3 seconds"""
        url = "{}/open/seconds".format(self.base_url)
        print("Path:", url)
        msg = { 'seconds': 2 }
        response = requests.post(url, json=msg)
        self.assertEqual(200, response.status_code)
        result = response.json()
        self.print_JSON(result, title="test_door_opening:")
        msg = { 'seconds': "not good!" }
        response = requests.post(url, json=msg)
        self.assertEqual(200, response.status_code)
        result = response.json()
        self.print_JSON(result, title="test_door_opening:")

    def delete_member(self, id):
        m = Member(id)
        for t in m.transactions:
            trec = Transaction(t['id'])
            trec.delete()
        m.delete()
        print("deleted row", id)

if __name__ == '__main__':
    unittest.main()

