#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Simple member database access

    Connects to the database or emulate a connection
    Check the existence of a member
    If a member is found then check that he paid his due

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


class Member(object):
    """
    A member record in the member database - SELECT mode only supported
    """
    def __init__(self, database, member_id=None, qrcode=None):
        """
        Select a record from the database based on a member table id or the id found in a QR code
        :param member_id: int for member tbale key
        :param qrcode: string read in a qrcode
        """
        self.id, self.name, self.birthdate, self.status = None, None, None, None
        self.db = database
        # create a member based on an ID or QR Code
        self.qrcode_version = '?'
        if member_id:
            self.get_from_db(member_id)
        elif qrcode:
            self.decode_qrcode(qrcode)

    def get_from_db(self, member_id):
        """Connects to the database to fetch a member table record or simulation"""
        data = self.db.fetch("SELECT id, username, birthdate, status from users where id=%s", (member_id,))
        self.id, self.name, self.birthdate, self.status = data or (None, None, None, None)
        if self.birthdate and not isinstance(self.birthdate, (datetime, date)):
            self.birthdate = datetime.strptime(self.birthdate, "%Y-%m-%d")

    def decode_qrcode(self, qrcode):
        """Decode a QR code in its component based on its version number"""
        if isinstance(qrcode, bytes) or isinstance(qrcode, bytearray):
            qrcode = qrcode.decode("utf-8")
        print("Read QR code:", qrcode)
        # QR Code Version 1
        if qrcode.startswith("XCJ1"):
            try:
                clear_qrcode = qrcode.split('#')  #     10  XCJ1#123456#My Name
                member_id = clear_qrcode[1]
                self.qrcode_version = '1'
            except ValueError:
                return
        else: #  QR Code Version > 1
            des = DES.new(self.db.key, DES.MODE_ECB)
            try:
                clear_qrcode = des.decrypt(unhexlify(qrcode)).decode("utf-8").strip().split('#') # XCJ2#123456#2015#2018-07-17
                self.qrcode_version = '2'
            except (binascii_error, UnicodeDecodeError):
                return
            member_id = clear_qrcode[1]
        self.get_from_db(member_id)
        #
        # Validation of the decoded QR Code
        #
        if self.qrcode_version >= '2':
            crc = self.birthdate.year ^ (self.birthdate.day*100 + self.birthdate.month)
            if int(clear_qrcode[2]) != crc:
                print("Incorrect CRC based on birthdate", crc)
            validity = datetime.strptime(clear_qrcode[3], "%Y-%m-%d" if len(clear_qrcode[3]) == 10 else "%Y-%m-%d %H:%M:%S")
            print("QR code valid until", validity)
            if datetime.now() > validity:
                print("QR Code has expired.")
        print("Decoded QR Code:", clear_qrcode)


    def encode_qrcode(self, version=1):
        """Encode this member's data into a QR Code string/payload"""
        if version==1:
            return "XCJ{}#{}#{}".format(version, self.id, self.name)
        elif version==2:
            crc = self.birthdate.year ^ (self.birthdate.day*100 + self.birthdate.month)
            validity = '{0:%Y-%m-%d}'.format(datetime.today() + timedelta(days=180))    # 6 months validity
            qrcode = "XCJ{}#{}#{}#{}".format(version, self.id, crc, validity)           # XCJ2#123456#2015#2018-07-17
            des = DES.new(self.db.key, DES.MODE_ECB)
            # turn qrcode into bytes and pad to multiple of 8 bytes
            qrcode = qrcode.encode("utf-8")
            qrcode += ((((len(qrcode)+7) // 8) * 8) - len(qrcode)) * b' '
            encrypted_qrcode = hexlify(des.encrypt(qrcode))
            # print(qrcode, encrypted_qrcode)
            return encrypted_qrcode
        else:
            return "Unknown Encoding Version{}".format(version)


    def __str__(self):
        return "{} ({})".format(self.name, self.id)

if __name__ == "__main__":
    from model_db import Database
    db = Database()
    m = Member(database=db, member_id=123456)
    print("Found in db:", m.name, m.birthdate, m.status)
    print("Make QR Code:", m.encode_qrcode())
    n = Member(database=db, qrcode=m.encode_qrcode())
    assert(str(m) == str(n))
    print("m==n:", str(m) == str(n))

    print('-' * 20)
    qr_v2 = m.encode_qrcode(version=2)
    o = Member(database=db, qrcode=qr_v2)
    assert(str(m) == str(o))
    print("m==o:", str(m) == str(o))

    # failure expected --> None (None)
    print('-' * 20)
    not_good=Member(database=db, qrcode="ahahah")
    print("Fail 1", not_good)
    not_good=Member(database=db, member_id=-1)
    print("Fail 2", not_good)
    not_good = Member(database=db, qrcode="XCJ1#-1#ahahah")
    print("Fail 3", not_good)
    # alter a byte in the read code....
    qr_v2=qr_v2[:6] + b'e' + qr_v2[7:]
    not_good=Member(database=db, qrcode=qr_v2)
    print("Fail 4", not_good)
