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
import pymysql
from json import dumps
from member_db import Member
from transaction_db import Transaction


class Member_Api(Member):
    """Surclass Member to add JSON facilities to interact with John's WeCHap app"""
    def __int__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def from_json(self, data):
        """Fill the user's field from a JSON object and INSERT in database"""
        try:
            d = {
                # mandatory fields
                "openid": data['openid'],
                "avatar_url": data['avatarUrl'],
                'username': data['basicInfo']['nickName'],
                # optional fields
                'city': data['basicInfo'].get('city', ''),
                'country': data['basicInfo'].get('country', ''),
                'gender': data['basicInfo'].get('gender', 0),
                'language': data['basicInfo'].get('language', ''),
                'province': data['basicInfo'].get('province', ''),
                # set by this function
                'birthdate': '1970-01-01',
                'passwd': "*A0F874BC7F54EE086FCE60A37CE7887D8B31086B",  # password123
                'status': 'OK',
                'role': 1,
                'create_time': datetime.now(),
                'last_update': datetime.now(),
            }
            new_id = self.insert(table='users', **d)
            # do we have a payment record to insert?
            if 'paymentInfo' in data:
                payment = Transaction(member_id=new_id)
                data = {
                    'member_id': new_id,
                    'type':'1M MEMBERSHIP',
                    'description': data['paymentInfo']['payIndex'],
                    'amount': data['paymentInfo']['CNYAmount'], 'currency':'CNY',
                    'valid_from': datetime.strptime(data['paymentInfo']['paidTime'], '%Y%m%d%H%M'),
                    'valid_until': date.today()+timedelta(days=31),
                    'created_on': datetime.now()
                }
                payment.insert('transactions', **data)
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
                'data': {'new_id': new_id}   # // you may put data at here,in json format.
            }
        return dumps(dico)


    def to_json(self):
        """return the JSON representation of the member object"""
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
                'openid': self.data['openid'],           #  "ozckH0TkSadGgyeAb5Bn390qQMa8",   // the only and unique ID of a member.
                'avatarUrl': self.data['avatar_url'],      # "https://wx.qlogo.cn/mmopen/vi_32/GPm0HkJtcIsWkZmVNaxJP19ibl1g2YJTEibglP0UibOZstaRN1lbuMavu1a1Y795p6J1vHz0bM27icibCiat9ERricyng/0",    // member`s PICTURE
                'basicInfo':
                    {
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
                        'lastActiveType': 'tbd',  # ''Open the door/ paid for membership',    // lastest action type: opened the door or paid the membership or bought a drink from xcj
                        'expireTime': '999912312359',       #// membership expire date and time
                        'tags': tags,  # ['member', 'staff', 'manager', 'teacher', 'admin', 'cooperater', 'visiter'],       // member`s tag, to decide the priviledge of a member
                        'memo': ''         # for admin use: take extra notes, e.g:this member asked for refund.
                    },
                'paymentInfo':
                    {
                        'paidTime': last_payment['created_on'].strftime('%Y%m%d%H%M'),  #'201803121929',     // last payment date and time
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