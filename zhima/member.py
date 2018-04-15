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

"""
__author__ = "Eric Gibert"
__version__ = "1.0.20170113"
__email__ =  "ericgibert@yahoo.fr"
__license__ = "MIT"
from datetime import datetime, timedelta, date
from binascii import hexlify, unhexlify, Error as binascii_error
from Crypto.Cipher import DES
from model_db import Database


class Member(Database):
    """
    A member record in the member database
    - Database is super class to connect to the db itself and perform all SQL queries
    - Member (db.users) is master table to Transactions (db.transactions)
    """
    ROLE = {
        'VISITOR': 0,
        'MEMBER': 1,
        'MASTER': 2,
        'GROUP': 4,
        'STAFF': 5,
        'ADMIN': 10
    }

    STATUS = {
        "OK": "OK",
        "NOT_OK": "Not OK",
        "INVALID": "Invalid"
    }

    def __init__(self, id=None, qrcode=None, *args, **kwargs):
        """
        Select a record from the database based on a member table id or the id found in a QR code
        :param id: int for member tbale key
        :param qrcode: string read in a qrcode
        """
        super().__init__(table="users", *args, **kwargs)
        self.id, self.name, self.birthdate, self.status, self.data = None, None, None, None, {}
        # create a member based on an ID or QR Code
        self.qrcode_version, self.qrcode_is_valid = '?', False
        self.transactions = []
        if id:
            self.get_from_db(id)
        elif qrcode:
            self.decode_qrcode(qrcode)  # which calls get_from_db if the QR code is valid
        elif 'openid' in kwargs:
            result = self.select(columns='id', openid=kwargs['openid'])
            try:
                self.get_from_db(result['id'])
                self.id = result['id']
            except TypeError:
                self.data = {}

    def get_max_valid_until(self):
        """
        Check among the member's transactions if any transaction ends with 'MEMBERSHIP'.
        Return the max(valid_until) of these memberships transactions or None
        """
        try:
            row = self.fetch("""SELECT max(valid_until) as max_valid from transactions 
                                where member_id=%s and RIGHT(type, 10)='MEMBERSHIP'""", (self.id,))
            # print("- Valid until", row['max_valid'])
            self.validity = '{0:%Y-%m-%d}'.format(row['max_valid'])
        except (AttributeError, TypeError):
            # if no membership found then validity==yesterday!
            self.validity = '{0:%Y-%m-%d}'.format(datetime.today() - timedelta(days=1))

    def get_from_db(self, member_id):
        """Connects to the database to fetch a member table record or simulation"""
        self.data = self.select(id=member_id)
        try:
            self.id, self.name = self.data['id'], self.data['username']
            self.status = self.data['status']
            if isinstance(self.data['birthdate'], (datetime, date)):
                self.birthdate = self.data['birthdate']
            else:
                self.birthdate = datetime.strptime(self.data['birthdate'], "%Y-%m-%d")
            # fetch this member's transactions
            self.transactions = self.select('transactions',
                                               columns="""id, type, description, 
                                                       CONCAT(FORMAT(amount, 2), ' ', currency) as amount,
                                                       valid_from, valid_until, created_on""",
                                               one_only=False,
                                               order_by="created_on DESC",
                                               member_id=self.id)
            self.get_max_valid_until()
            if self.validity >= '{0:%Y-%m-%d}'.format(datetime.today()):
                self.qrcode_is_valid = True
        except (TypeError, KeyError):
            print("error assigning member information")
            self.id, self.name, self.birthdate, self.status = (None, None, None, None)
        return self.id

    def decode_qrcode(self, qrcode):
        """Decode a QR code in its component based on its version number"""
        if isinstance(qrcode, bytes) or isinstance(qrcode, bytearray):
            qrcode = qrcode.decode("utf-8")
        print("Read QR code:", qrcode)
        self.qrcode_is_valid, member_id = False, None
        # QR Code Version 1
        if qrcode.startswith("XCJ1"):
            try:
                self.clear_qrcode = qrcode.split('#')  #     10  XCJ1#123456#My Name
                member_id = self.clear_qrcode[1]
                self.qrcode_version = '1'
                print("Decoded QR Code V{}: {}".format(self.qrcode_version, self.clear_qrcode))
            except ValueError:
                return None
        else: #  QR Code Version > 1
            des = DES.new(self.key, DES.MODE_ECB)
            try:
                self.clear_qrcode = des.decrypt(unhexlify(qrcode)).decode("utf-8").strip().split('#') # XCJ2#123456#2015#2018-07-17
                self.qrcode_version = self.clear_qrcode[0][3:]
                print("Decoded QR Code V{}: {}".format(self.qrcode_version, self.clear_qrcode))
            except (binascii_error, UnicodeDecodeError):
                return None
            else:
                member_id = self.clear_qrcode[1]
        #
        # Validation of the decoded QR Code
        #
        if member_id and self.get_from_db(member_id):
            self.qrcode_is_valid = True  # benefice of doubt...
            if self.qrcode_version == '2' and self.birthdate:
                crc = self.birthdate.year ^ (self.birthdate.day*100 + self.birthdate.month)
                if int(self.clear_qrcode[2]) != crc:
                    print("Incorrect CRC based on birthdate", crc)
                    self.qrcode_is_valid = False
                validity = datetime.strptime(self.clear_qrcode[3], "%Y-%m-%d" if len(self.clear_qrcode[3]) == 10 else "%Y-%m-%d %H:%M:%S")
                print("QR code valid until", validity)
                if datetime.now() > validity:
                    print("QR Code has expired.")
                    self.qrcode_is_valid = False
            elif self.qrcode_version == '3':
                from_date, to_date = self.clear_qrcode[2], self.clear_qrcode[3]  #  'yyyy-mm-dd' strings
                today = '{0:%Y-%m-%d}'.format(date.today())
                self.qrcode_is_valid = ( from_date <= today <= to_date )

    def encrypt_qrcode(self, qrcode):
        """turn qrcode string into bytes and pad to multiple of 8 bytes"""
        des = DES.new(self.key, DES.MODE_ECB)
        qrcode = qrcode.encode("utf-8")
        qrcode += ((((len(qrcode)+7) // 8) * 8) - len(qrcode)) * b' '
        encrypted_qrcode = hexlify(des.encrypt(qrcode))
        return encrypted_qrcode

    def encode_qrcode(self, version=2):
        """Encode this member's data into a QR Code string/payload
        :param version: defaulted to the latest version
        """
        if version==1:
            return "XCJ{}#{}#{}".format(version, self.id, self.name)
        elif version==2:
            # XCJ2#123456#2015#2018-07-17
            crc = self.birthdate.year ^ (self.birthdate.day*100 + self.birthdate.month)
            self.get_max_valid_until()
            qrcode = "XCJ{}#{}#{}#{}".format(version, self.id, crc, self.validity)
            return self.encrypt_qrcode(qrcode)
        elif version==3:
            #  XCJ3#123456#YYYYMMDD#YYYYMMDD    --> From/To dates of validity
            from_date = '{0:%Y-%m-%d}'.format(self.birthdate)
            to_date = self.validity if isinstance(self.validity, str) else '{0:%Y-%m-%d}'.format(self.validity)
            qrcode = "XCJ{}#{}#{}#{}".format(version, self.id, from_date, to_date)
            return self.encrypt_qrcode(qrcode)
        else:
            return "Unknown Encoding Version {}".format(version)

    def __str__(self):
        return "{} ({})".format(self.name, self.id)


if __name__ == "__main__":
    m = Member(id=123456)
    print("Found in db:", m.name, m.birthdate, m.status)
    print("Make QR Code:", m.encode_qrcode())
    n = Member(qrcode=m.encode_qrcode(version=1))
    assert(str(m) == str(n))
    print("m==n:", str(m) == str(n))
    print("Index on 'username':", n["username"])
    assert(m.name == n["username"])
    print("Index on 'unknown':", n["unknown"])
    assert(n["unknown"] is None)

    print('-' * 20)
    qr_v2 = m.encode_qrcode(version=2)
    o = Member(qrcode=qr_v2)
    assert(str(m) == str(o))
    print("m==o:", str(m) == str(o))

    print('-' * 20)
    print("# failure expected --> None (None)")
    not_good=Member(qrcode="ahahah")
    print("Fail 1", not_good)
    not_good=Member(id=-1)
    print("Fail 2", not_good)
    not_good = Member(qrcode="XCJ1#-1#ahahah")
    print("Fail 3", not_good)
    # alter a byte in the read code....
    qr_v2=qr_v2[:6] + b'e' + qr_v2[7:]
    not_good=Member(qrcode=qr_v2)
    print("Fail 4", not_good)

    print('-' * 20)
    print("# test the validity duration")
    m = Member(id=123459)  # no membership transaction record
    print("Found in db:", m.name, m.birthdate, m.status)
    print("Make QR Code:", m.encode_qrcode())
    n = Member(qrcode=m.encode_qrcode())
    assert(str(m) == str(n))
    print("m==n:", str(m) == str(n))

    print('-' * 20)
    print("test QR code Version 3")
    m = Member(id=123457)
    print(m.transactions)
    m.validity = date.today()
    print(m.birthdate, m.validity)
    qr_code3 = m.encode_qrcode(version=3)
    print(qr_code3)
    m = Member(qrcode=qr_code3)
    print(m["username"], m["gender"], m.qrcode_is_valid)
    assert(m["gender"] == 5)