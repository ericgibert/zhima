#!/usr/bin/env python3
""" Simple member database access

    Connects to the database or emulate a connection
    Check the existence of a member
    If a member is found then check that he paid his due

    pre-requisite:  sudo pip3 install PyMySQL
"""
__author__ = "Eric Gibert"
__version__ = "1.0.20170113"
__email__ =  "ericgibert@yahoo.fr"
__license__ = "MIT"
try:
    import pymysql
    _simulation = False
except ImportError:
    _simulation = True

SIMULATION = {
    123456: { "name": "Eric Gibert", "status": "OK", "date_of_birth": "1967-12-01"},
    55555: { "name": "Not OK", "status": "NOT OK", "date_of_birth": "1967-12-01"},
}

DB_LOGIN="xcj_root"
DB_PASSWD="xcj09root"
DB_NAME="xcj_members"

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
            with pymysql.connect("localhost", DB_LOGIN, DB_PASSWD, DB_NAME) as cursor:
                cursor.execute("SELECT * from tb_users where id=%s", (member_id,))
                data = cursor.fetchone()
            self.id, self.name, self.date_of_birth, self.status = data or (None, None, None, None)

    def decode_qrcode(self, qrcode):
        """Decode/explode a QR code in its component based on its version number"""
        if isinstance(qrcode, bytes) or isinstance(qrcode, bytearray):
            qrcode = qrcode.decode("utf-8")
        if qrcode.startswith("XCJ1"):   # QR Code Version 1
            try:
                fields = qrcode.split('#')  #       XCJ1#123456#My Name
            except ValueError:
                return
            self.get_from_db(fields[1])

    def encode_qrcode(self, version=1):
        """Encode this member's data into a QR Code string/payload"""
        if version==1:
            return "XCJ{}#{}#{}".format(version, self.id, self.name)
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
    # failure expected --> None (None)
    not_good=Member(qrcode="ahahah")
    print(not_good)
    not_good=Member(member_id=-1)
    print(not_good)
    not_good = Member(qrcode="XCJ1#-1#ahahah")
    print(not_good)