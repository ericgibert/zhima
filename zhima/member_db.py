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
from subprocess import check_output
import json
from datetime import datetime, timedelta, date
from binascii import hexlify, unhexlify
from Crypto.Cipher import DES
try:
    import pymysql
    _simulation = False
except ImportError:
    _simulation = True

SIMULATION = {
    123456: { "name": "Eric Gibert", "status": "OK", "date_of_birth": "1967-12-01"},
    55555: { "name": "Not OK", "status": "NOT OK", "date_of_birth": "1967-12-01"},
}


class Member(object):
    """
    A member record in the member database - SELECT mode only supported
    """
    def __init__(self, member_id=None, qrcode=None):
        """
        Select a record from the database based on a member table id or the id found in a QR code
        :param member_id: int for member tbale key
        :param qrcode: string read in a qrcode
        """
        self.id, self.name, self.date_of_birth, self.status = None, None, None, None
        # MySQL database parameters
        db_access = json.load(open("../Private/db_access.data"))
        my_IP = check_output(['hostname', '-I']).decode("utf-8").strip()
        print("My IP:", my_IP)
        ip_3 = '.'.join(my_IP.split('.')[:3])
        try:
            self.dbname = db_access[ip_3]["dbname"]
            self.login = db_access[ip_3]["login"]
            self.passwd = db_access[ip_3]["passwd"]
            self.server_ip = "localhost" if my_IP==db_access[ip_3]["server_ip"] else db_access[ip_3]["server_ip"]
            self.key = db_access["key"].encode("utf-8")
        except KeyError:
            print("Cannot find entry {} in db_access.data".format(ip_3))
            exit(1)
        # create a member based on an ID or QR Code
        if member_id:
            self.get_from_db(member_id)
        elif qrcode:
            self.decode_qrcode(qrcode)

    def get_from_db(self, member_id):
        """Connects to the database to fetch a member table record or simulation"""
        if not isinstance(member_id, int):
            member_id = int(member_id)

        if _simulation:
            try:
                m = SIMULATION[member_id]
            except KeyError:
                self.id = None
            else:
                self.id = member_id
                self.name = m["name"]
                self.status = m["status"]
                self.date_of_birth = m["date_of_birth"]
        else:
            with pymysql.connect(self.server_ip, self.login, self.passwd, self.dbname) as cursor:
                cursor.execute("SELECT id, username, birthdate, status from users where id=%s", (member_id,))
                data = cursor.fetchone()
            self.id, self.name, self.date_of_birth, self.status = data or (None, None, None, None)
            print(self.date_of_birth, type(self.date_of_birth))
            if self.date_of_birth and not isinstance(self.date_of_birth, (datetime, date)):
                self.date_of_birth = datetime.strptime(self.date_of_birth, "%Y-%m-%d")
            print(self.date_of_birth, type(self.date_of_birth))

    def decode_qrcode(self, qrcode):
        """Decode/explode a QR code in its component based on its version number"""
        if isinstance(qrcode, bytes) or isinstance(qrcode, bytearray):
            qrcode = qrcode.decode("utf-8")
        # QR Code Version 1
        if qrcode.startswith("XCJ1"):
            try:
                fields = qrcode.split('#')  #     10  XCJ1#123456#My Name
            except ValueError:
                return
            self.get_from_db(fields[1])
        else:
            des = DES.new(self.key, DES.MODE_ECB)
            print(qrcode)
            clear_qrcode = des.decrypt(unhexlify(qrcode)).decode("utf-8").strip()
            print(clear_qrcode)


    def encode_qrcode(self, version=1):
        """Encode this member's data into a QR Code string/payload"""
        if version==1:
            return "XCJ{}#{}#{}".format(version, self.id, self.name)
        elif version==2:
            dob = self.date_of_birth
            crc = dob.year ^ (dob.day*100 + dob.month)
            validity = '{0:%Y-%m-%d}'.format(datetime.today() + timedelta(days=180)) # 6 months validity
            qrcode = "XCJ{}#{}#{}#{}".format(version, self.id, crc, validity)
            des = DES.new(self.key, DES.MODE_ECB)
            # pad qrcode to multiple of 8 characters and turn into bytes
            qrcode = qrcode.encode("utf-8")
            # print(qrcode, len(qrcode), (((len(qrcode)+7) // 8) * 8) - len(qrcode))
            qrcode += ((((len(qrcode)+7) // 8) * 8) - len(qrcode)) * b' '
            encrypted_qrcode = hexlify(des.encrypt(qrcode))
            print(qrcode, encrypted_qrcode)
            return encrypted_qrcode
        else:
            return "Unknown Encoding Version{}".format(version)


    def __str__(self):
        return "{} ({})".format(self.name, self.id)

if __name__ == "__main__":
    m = Member(123456)
    print("Found in db:", m.name, m.date_of_birth, m.status)
    print("Make QR Code:", m.encode_qrcode())
    n = Member(qrcode=m.encode_qrcode())
    print("__str__:", n)
    #
    qr = m.encode_qrcode(version=2)
    m.decode_qrcode(qr)
    # failure expected --> None (None)
    # not_good=Member(qrcode="ahahah")
    # print(not_good)
    # not_good=Member(member_id=-1)
    # print(not_good)
    # not_good = Member(qrcode="XCJ1#-1#ahahah")
    # print(not_good)
