#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Simple member database access

    Connects to the database or emulate a connection
    Check the existence of a member
    If a member is found then check that he paid his due
fr_FR
    pre-requisite:
        sudo pip3 install PyMySQL
        sudo pip3 install pycryptodome  (https://www.blog.pythonlibrary.org/2016/05/18/python-3-an-intro-to-encryption/)



JSON structure from WeChat app:

UserInfo:
{
    openid: "ozckH0TkSadGgyeAb5Bn390qQMa8",   // the only and unique ID of a member.
    avatarUrl: "https://wx.qlogo.cn/mmopen/vi_32/GPm0HkJtcIsWkZmVNaxJP19ibl1g2YJTEibglP0UibOZstaRN1lbuMavu1a1Y795p6J1vHz0bM27icibCiat9ERricyng/0",    // member`s PICTURE
    basicInfo:
      {
        city: "",
        country: "South Korea",
        gender: 1,
        language: "zh_CN",
        nickName: "JOHN:",
        province: ""
      },
    memberInfo:
    {
        createTime: '201505011522'        // first time of member`s info creation in this system
        lastUpdate: '201801011420',       // last member information modification time
        lastActiveTime: '201803021530',   // last member active time (e.g: came to xinchejian and operate something)
        lastActiveType: 'Open the door/ paid for membership',    // lastest action type: opened the door or paid the membership or bought a drink from xcj
        expireTime: '201903111928',       // membership expire date and time
        tags: ['member', 'staff', 'manager', 'teacher', 'admin', 'cooperater', 'visiter'],       // member`s tag, to decide the priviledge of a member
        memo: ''            // for admin use: take extra notes, e.g:this member asked for refund.
    },
    paymentInfo:
    {
        paidTime: '201803121929',     // last payment date and time
        payIndex: '9cu293820xxjfiuewfdsfdse32',   // the lastest payment index number, this is a unique random codes generated by wechat pay and alipay system and our system.
        CNYAmount: '3200',            // how much is the last payment.
    }
}

"""
__author__ = "Eric Gibert"
__version__ = "1.0.20170113"
__email__ =  "ericgibert@yahoo.fr"
__license__ = "MIT"
from datetime import datetime, date, timedelta
from time import time
import pymysql
from json import dumps
from member import Member
from transaction import Transaction


class Member_Api(Member):
    """Surclass Member to add JSON facilities to interact with John's WeChat app"""
    API_MAPPING_TO_DB = {
        "openid": "openid",
        "rfid": "rfid",
        "avatarUrl": "avatar_url",
        "nickName": "username",
        "city": "city",
        "country": "country",
        "gender": "gender",
        "language": "language",
        "province": "province",
        "tags": "role",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.openid = kwargs.get("openid")
        self.rfid = kwargs.get("rfid")

    def update(self, **kwargs):
        last_row_id = super().update(**kwargs)
        if last_row_id:
            result = {'errno': '1000', 'errmsg': "Success", 'data': {'upd_fields:': list(kwargs.keys())} }
        else:
            result = {'errno': '1004', 'errmsg': "Update user record error", 'data': {'upd_fields:': list(kwargs.items())} }
        return dumps(result)

    def _add_payment(self, data, until_days=31):
        """Insert a transaction record based on the data received from API
        - normal transaction provides a 'paidTime'
        - extension of membership does not --> from_date = current member.validity
        """
        payment = Transaction(member_id=self.id)
        paidTime = datetime.strptime(data['paidTime'], '%Y%m%d%H%M')
        v = self['validity']
        from_date = max(paidTime, datetime(v.year, v.month, v.day)) if v else paidTime
        until_date = from_date + timedelta(days=until_days)
        data = {
            'member_id': self.id,
            'type': data.get('payType') or '1M MEMBERSHIP',
            'description': data['payIndex'],
            'amount': data['CNYAmount'], 'currency':'CNY',
            'valid_from': from_date,
            'valid_until': until_date,
            'created_on': datetime.now()
        }
        result = payment.insert('transactions', **data)
        if result:
            payment.update_member_status(self.id)
        return result


    def add_payment(self, data):
        last_row_id = self._add_payment(data, data.get("until_days", 31))
        if last_row_id:
            result = {'errno': '1000', 'errmsg': "Success", 'data': {'id': last_row_id, 'add_payment:': list(data.keys())} }
        else:
            result = {'errno': '1005', 'errmsg': "Add transaction record error", 'data': {'add_payment:': list(data.items())} }
        return dumps(result)

    def create_from_json(self, data):
        """
        Fill a empty member's field from a JSON object and INSERT in database 'users' table
        - Add a payment if present
        - to be used from WeChat app or other external App / minimal data available
        """
        try:
            role = self.ROLE[data['memberInfo']['tags'].upper()]
        except KeyError:
            role = 1
        try:
            d = {
                # mandatory fields
                "openid": data['openid'],
                "rfid": data.get('rfid', data['openid']), # if no RFID given then default to 'openid' / must be unique!
                "avatar_url": data['avatarUrl'],
                'username': data['basicInfo']['nickName'],
                # optional fields
                'city': data['basicInfo'].get('city', ''),
                'country': data['basicInfo'].get('country', ''),
                'gender': data['basicInfo'].get('gender', 0),
                'language': data['basicInfo'].get('language', ''),
                'province': data['basicInfo'].get('province', ''),
                # set by this function
                #'birthdate': '1970-01-01',
                'passwd': "*A0F874BC7F54EE086FCE60A37CE7887D8B31086B",  # password123
                'status': 'NOT_OK',
                'role': role,
                'create_time': datetime.now(),
                'last_update': datetime.now(),
            }
            new_id = self.insert(table='users', **d)
            # do we have a payment record to insert?
            if 'paymentInfo' in data:
                self.id = new_id
                self._add_payment(data['paymentInfo'])
        except (ValueError, TypeError, KeyError) as err:
                dico = {
                    'errno': '1002',  #// no error with 1000, error numbers for others
                    'errmsg': "Problem with the JSON object received by add_member(): {}".format(err),
                    'data': {'Error': str(err)}   # // you may put data at here,in json format.
                }
        except pymysql.err.IntegrityError as err_sql:
                dico = {
                    'errno': '1003',  #// no error with 1000, error numbers for others
                    'errmsg': "Problem with INSERT in add_member(): {}".format(err_sql),
                    'data': {'Error': str(err_sql)}   # // you may put data at here,in json format.
                }
        else:
            dico = {
                'errno': '1000',  #// no error with 1000, error numbers for others
                'errmsg': "Success",
                'data': {
                    'new_id': new_id,
                    'qrcode_url': "/images/XCJ_{}.png?{}".format(new_id, time())
                }   # // you may put data at here,in json format.
            }
        return dumps(dico)


    def to_json(self):
        """
        Return the JSON representation of the member object
        Member.data{} ==> JSON object
        """
        if self.id is None:
            return {
                'errno': '1999',  #// no error with 1000, error numbers for others
                'errmsg': "No member record found",
                'data': { "id": self.openid}   # // you may put data at here,in json format.
            }
        try:
            for k, v in Member.ROLE.items():
                if v==self.data['role']:
                    tags = k.capitalize()
                    break
            else:
                tags='Unknown'

            last_payment = self.transactions[-1] if self.transactions else {
                'created_on': '',
                'description': 'no payment received',
                'amount': 0.0 }
            # print('last_payment', last_payment)
            dico = {
                'id': self.data['id'],
                'openid': self.data['openid'],           #  "ozckH0TkSadGgyeAb5Bn390qQMa8",   // the only and unique ID of a member.
                'rfid': self.data['rfid'],
                'avatarUrl': self.data['avatar_url'],      # "https://wx.qlogo.cn/mmopen/vi_32/GPm0HkJtcIsWkZmVNaxJP19ibl1g2YJTEibglP0UibOZstaRN1lbuMavu1a1Y795p6J1vHz0bM27icibCiat9ERricyng/0",    // member`s PICTURE
                'basicInfo':
                    {
                        'status': self.data['status'],
                        'email': self.data['email'],
                        'city': self.data['city'],
                        'country': self.data['country'],
                        'gender': self.data['gender'],
                        'language': self.data['language'],    # "zh_CN",
                        'nickName': self.data['username'],
                        'province': self.data['province']
                    },
                'memberInfo':
                    {
                        'createTime': self.data['create_time'].strftime('%Y%m%d%H%M'), #'201505011522',        #// first time of member`s info creation in this system
                        'lastUpdate': self.data['last_update'].strftime('%Y%m%d%H%M'), #'201801011420',       #// last member information modification time
                        'lastActiveTime': self.data['last_active_time'].strftime('%Y%m%d%H%M') if self.data['last_active_time'] else "",  #"'201803021530',   #// last member active time (e.g: came to xinchejian and operate something)
                        'lastActiveType': self.data['last_active_type'],  # ''Open the door/ paid for membership',    // lastest action type: opened the door or paid the membership or bought a drink from xcj
                        'expireTime': self.data['validity'].strftime('%Y%m%d0000'),       #// membership expire date and time
                        'tags': tags,  # ['member', 'staff', 'manager', 'teacher', 'admin', 'cooperater', 'visiter'],       // member`s tag, to decide the priviledge of a member
                        'memo': ''         # for admin use: take extra notes, e.g:this member asked for refund.
                    },
                'paymentInfo':
                    {
                        'paidTime': last_payment['created_on'].strftime('%Y%m%d%H%M') if last_payment['created_on'] else "200001010000",  #'201803121929',     // last payment date and time
                        'payIndex': last_payment['description'],   #''9cu293820xxjfiuewfdsfdse32',   // the lastest payment index number, this is a unique random codes generated by wechat pay and alipay system and our system.
                        'CNYAmount': last_payment['amount']        #''3200',            // how much is the last payment.
                    }
            }
        except KeyError as err:
            dico = {
                'errno': '1001',  #// no error with 1000, error numbers for others
                'errmsg': "Error in Member.to_json(): missing key self.data['{}'] for id={}".format(err, self.id),
                'data': {'missing key': str(err)}   # // you may put data at here,in json format.
            }
        return dumps(dico)

    def from_json(self, json_data):
        """
        API call returned JSON Object ==> Member.data{}
        - move each attribute of the JSON object (1st or 2nd level) to the flat Member.data dictionary
        - assign some calculated field too
        """
        self.id = json_data.get('id')
        if self.id is None: return
        expireTime = datetime.strptime(json_data['memberInfo']['expireTime'], '%Y%m%d%H%M')
        # print("expireTime:", expireTime)
        self.data = {
            'id': self.id,
            'openid': json_data['openid'],
            'rfid': json_data['rfid'],
            'avatar_url': json_data['avatarUrl'],
            # 'basicInfo:
            'status': json_data['basicInfo']['status'],
            'email': json_data['basicInfo']['email'],
            'city': json_data['basicInfo']['city'],
            'country': json_data['basicInfo']['country'],
            'gender': json_data['basicInfo']['gender'],
            'language': json_data['basicInfo']['language'],    # "zh_CN",
            'username': json_data['basicInfo']['nickName'],
            'province': json_data['basicInfo']['province'],
            # 'memberInfo':
            'create_time': datetime.strptime(json_data['memberInfo']['createTime'], '%Y%m%d%H%M'), #'201505011522',        #// first time of member`s info creation in this system
            'last_update': datetime.strptime(json_data['memberInfo']['lastUpdate'], '%Y%m%d%H%M'), #'201801011420',       #// last member information modification time
            'last_active_time': datetime.strptime(json_data['memberInfo']['lastActiveTime'], '%Y%m%d%H%M') if json_data['memberInfo']['lastActiveTime'] else "",
            'role': self.ROLE[json_data['memberInfo']['tags'].upper()],
            'validity': date(year=expireTime.year, month=expireTime.month, day=expireTime.day)
            #'paymentInfo':
            # {
            #     'paidTime': '201803100956'
            #     'payIndex': 'bla bla bla'
            #     'CNYAmount': '100.00 CNY'
            # }
         }
        self.validity = self.data['validity']      #// membership expire date and time
