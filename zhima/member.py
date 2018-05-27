#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Simple member database access

    Connects to the database or emulate a connection
    Table 'users' expected
    Check the existence of a member
    If a member is found then check that he paid his due
    Manage the coding and decoding of QR Codes (various versions)

    pre-requisite:
        sudo pip3 install PyMySQL
        sudo pip3 install pycryptodome  (https://www.blog.pythonlibrary.org/2016/05/18/python-3-an-intro-to-encryption/)

    m = Member()                                --> m.data === {}
    m = Member(12345) | m = Member(id=12345)    --> fetch record id == '12345' in 'users' table into m.data dictionary
    m = Member(qrcode="string for a qr code")   --> decode the qr code and, if valid, fetch the record based on user Id
    m = Member(openid="1234567qwertyuiop")      --> fetch record having secondary key 'openid' as provided

    note: m["username"]  ===  m.data["username"]

"""
__author__ = "Eric Gibert"
__version__ = "1.0.20170113"
__email__ =  "ericgibert@yahoo.fr"
__license__ = "MIT"
from datetime import datetime, timedelta, date
from binascii import hexlify, unhexlify, Error as binascii_error
from Crypto.Cipher import DES
from model_db import Database
import base64
from send_email import send_email


class Member(Database):
    """
    A member record in the member database
    - Database is super class to connect to the db itself and perform all SQL queries
    - Member (db.users) is master table to Transactions (db.transactions)
    """
    MEMBERSHIP = [
        ("1M MEMBERSHIP", "1 Month Membership", 200.00, 31),
        ("6M MEMBERSHIP", "6 Months Membership", 900.00, 181),
        ("DONATION", "Donation", 0.00, -1),
        ("EVENT", "Event", 0.00, 1),
        ("TOOL", "Tool Usage", 50.00, 181),
        ("CROWD FUNDING", "Crowd Funding", 0.00, -1),
    ]

    ROLE = {
        'VISITOR': 0,
        'MEMBER': 1,
        'MASTER': 2,
        'GROUP': 4,
        'STAFF': 5,
        'ADMIN': 10
    }

    STATUS = {
        "OK": "OK",             #  expected status :-)
        "NOT_OK": "Not OK",     #  used when member has not paid its due
        "INVALID": "Invalid"    #  to use instead of deleting the record for transaction traceability
    }

    def __init__(self, id=None, qrcode=None, *args, **kwargs):
        """
        Select a record from the database based on a member table id or the id found in a QR code
        :param id: int for member tbale key
        :param qrcode: string read in a qrcode
        """
        super().__init__(table="users", *args, **kwargs)
        self.id, self.data, self.transactions = None, {}, []
        self.qrcode_version, self.qrcode_is_valid = '?', False
        # try fetching a database record based on given parameters
        if id:
            self.get_from_db(id)
        elif qrcode:
            id = self.decode_qrcode(qrcode)
            self.get_from_db(id)
        elif 'openid' in kwargs:
            self.get_from_db(openid=kwargs['openid'])

    def get_from_db(self, id=None, **where):
        """Connects to the database to fetch a member table record or simulation
            - expects 'users.id' as parameter only
            - fetch matching record in 'users' table into the self.data dictionary
            - some other attributes are set for convenience:
                - self.id == self.data['id'] == self['id']
                - self.transactions --> fetch all records (0..N) from slave table 'transactions' (list)
                - self.validity --> calculated: max(transaction.valid until) or yesterday (date)
        """
        self.data = self.select(id=id) if id else self.select(**where)
        try:
            self.id = self.data['id']
            # fetch all its transactions
            self.transactions = self.select('transactions',
                                               columns="""id, type, description, 
                                                       CONCAT(FORMAT(amount, 2), ' ', currency) as amount,
                                                       valid_from, valid_until, created_on""",
                                               one_only=False,
                                               order_by="created_on DESC",
                                               member_id=self.id)
            # calculate the validity
            row = self.fetch("""SELECT max(valid_until) as max_valid from transactions 
                                    where member_id=%s and RIGHT(type, 10)='MEMBERSHIP'""", (self.id,))
            self.data['validity'] = row['max_valid'] or (date.today() - timedelta(days=1)) # if no membership found then validity==yesterday!
            self.qrcode_is_valid = self['validity'] >= date.today()
        except (TypeError, KeyError) as err:
            print("error assigning member information")
            print(err)
            self.id, self.data = None, {}
        return self.id

    @property
    def is_staff(self):
        return self['role'] >= self.ROLE['STAFF'] and self['status'] == 'OK'

    @property
    def is_admin(self):
        return self['role'] == self.ROLE['ADMIN'] and self['status'] == 'OK'

    def decode_qrcode(self, qrcode):
        """Decode a QR code in its component based on its version number"""
        if isinstance(qrcode, bytes) or isinstance(qrcode, bytearray):
            qrcode = qrcode.decode("utf-8")
        print("Read QR code:", qrcode)
        self.qrcode_is_valid, member_id = False, None
        #   QR Code Version 1  -  no encryption
        #       XCJ1#123456#username
        if qrcode.startswith("XCJ1"):
            try:
                self.clear_qrcode = qrcode.split('#')
                self.qrcode_version = int(self.clear_qrcode[0][3:])
                member_id = int(self.clear_qrcode[1])
            except ValueError:
                member_id = None
            print("Decoded QR Code V{}: {}".format(self.qrcode_version, self.clear_qrcode))
        else:
            #
            #  QR Code Version > 1 ; encrypted
            #
            des = DES.new(self.key, DES.MODE_ECB)
            try:
                # self.clear_qrcode = des.decrypt(unhexlify(qrcode)).decode("utf-8").strip().split('#')
                bcode = base64.decodebytes(qrcode.encode('utf-8'))
                self.clear_qrcode = des.decrypt(bcode).decode('utf-8').strip(' ').split('#')
            except (binascii_error, UnicodeDecodeError, ValueError):
                return None
            try:
                self.qrcode_version = int(self.clear_qrcode[0])
                member_id = int(self.clear_qrcode[1])
            except ValueError:
                member_id = None
            print("Decoded QR Code V{}: {}".format(self.qrcode_version, self.clear_qrcode))
        #
        # Validation of the decoded QR Code
        #
        if member_id:  #  NO MORE CALL -->   and self.get_from_db(member_id):
            self.qrcode_is_valid = True  # benefice of doubt...
            if self.qrcode_version == 2:
                validity = datetime.strptime(self.clear_qrcode[2], "%y%m%d")
                print("QR code valid until", validity)
                if datetime.today() > validity:
                    print("QR Code has expired.")
                    self.qrcode_is_valid = False
            elif self.qrcode_version == 3:
                from_date, to_date = self.clear_qrcode[2], self.clear_qrcode[3]  #  'YYMMDD' strings
                print("QR code valid from {} until {}".format(from_date, to_date))
                today = '{0:%y%m%d}'.format(date.today())
                self.qrcode_is_valid = ( from_date <= today <= to_date )
        return member_id #  if self.qrcode_is_valid else None

    def encrypt_qrcode(self, qrcode):
        """turn qrcode string into bytes and pad to multiple of 8 bytes"""
        des = DES.new(self.key, DES.MODE_ECB)
        qrcode = qrcode.encode("utf-8")                                 # str --> bytearray using UTF-8
        qrcode += ((((len(qrcode)+7) // 8) * 8) - len(qrcode)) * b' '   # pad with necessary number of b' '
        # print("to encrypt:", des.encrypt(qrcode))
        # encrypted_qrcode = hexlify(des.encrypt(qrcode))                 # crypto into a hexadecimal string
        # print("helexify", encrypted_qrcode)
        encrypted_qrcode = base64.encodebytes(des.encrypt(qrcode))
        # print("base64  ", encrypted_qrcode)
        return encrypted_qrcode

    def encode_qrcode(self, version=2, from_date = None, until_date=None):
        """Encode this member's data into a QR Code string/payload
        :param version: defaulted to the latest version
        :from_date: type datetime.date or compatible
        :until_date: type datetime.date or compatible
        """
        if version == 1:
            #   XCJ1#123456#username
            return "XCJ{}#{}#{}".format(version, self.id, self['username'])
        elif version == 2:
            #   2#123456#YYMMDD
            qrcode = "{}#{}#{}".format(version, self.id, '{0:%y%m%d}'.format(self["validity"]))
            return self.encrypt_qrcode(qrcode)
        elif version == 3:
            #   3#123456#YYMMDD#YYMMDD    --> From/To dates of validity
            from_date = '{0:%y%m%d}'.format(from_date or date.today())
            to_date = '{0:%y%m%d}'.format(until_date or self["validity"])
            qrcode = "{}#{}#{}#{}".format(version, self.id, from_date, to_date)
            return self.encrypt_qrcode(qrcode)
        else:
            return "Unknown Encoding Version {}".format(version)

    def email_qrcode(self, qr_code_png=None, validity_msg="", email_to=""):
        """
        Sends the QR by email to a member
        The PNG should be already generated
        :return:
        """
        png = qr_code_png or "images/XCJ_{}.png".format(self.id)
        validity = validity_msg or "until {}".format(self["validity"])
        msg = "Please find attached your XCJ QR code. It is valid {}.".format(validity)
        send_email(
            "Your Xin Che Jian QR Code",
            from_=self.mailbox["username"],
            to_ = (email_to or self['email']).split(";"),
            message_txt=msg, message_HTML="<p>" + msg + "</p>",
            images=[png],
            server=Database.mailbox["server"], port=Database.mailbox["port"],
            login=Database.mailbox["username"], passwd=Database.mailbox["password"],
            debug=0
        )

    def __str__(self):
        return "{} ({}) [{}]".format(self['username'], self.id, self['validity'])


if __name__ == "__main__":
    m = Member(id=123456)
    print("Found in db:", m['username'],  m['status'])  #m.birthdate,
    print("Make QR Code:", m.encode_qrcode())
    n = Member(qrcode=m.encode_qrcode(version=1))
    assert(str(m) == str(n))
    print("m==n:", str(m) == str(n))
    print("Index on 'username':", n["username"])
    assert(m['username'] == n["username"])
    print("Index on 'unknown':", n["unknown"])
    assert(n["unknown"] is None)

    print('-' * 20)
    qr_v2 = m.encode_qrcode(version=2)
    o = Member(qrcode=qr_v2)
    print(str(m) , str(o))
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
    print("Found in db:", m['username'],  m['status'])
    print("Make QR Code:", m.encode_qrcode())
    n = Member(qrcode=m.encode_qrcode())
    assert(str(m) == str(n))
    print("m==n:", str(m) == str(n))

    print('-' * 20)
    print("test QR code Version 3")
    m = Member(id=123457)
    print(m.transactions)
    # m.validity = date.today()
    print("Validity:", m["validity"])  # m.birthdate,
    qr_code3 = m.encode_qrcode(version=3)
    print(qr_code3)
    m = Member(qrcode=qr_code3)
    print(m["username"], m["gender"], m.qrcode_is_valid)
    # assert(m["gender"] == 5)

    print('-' * 20)
    print("test by openid")
    m = Member(openid="a3c56532")
    print("Found in db:", m['username'], m['status'])