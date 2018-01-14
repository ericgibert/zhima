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
    123456: { "name": "Eric Gibert", "status": "ok"},
}

DB_LOGIN="xcj_root"
DB_PASSWD="xcj09root"
DB_NAME="xcj_members"

class Member(object):
    """
    A member record in the member database - SELECT mode only supported
    """
    def __init__(self, member_id):
        """
        Select a record from the database
        :param member_id: longint for member key
        """
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
        else:
            with pymysql.connect("localhost", DB_LOGIN, DB_PASSWD, DB_NAME) as cursor:
                cursor.execute("SELECT * from tb_users where id=%s", (member_id,))
                data = cursor.fetchone()
            self.id, self.name, self.date_of_birth, self.status = data or (None, None, None, None)



if __name__ == "__main__":
    m = Member(123456)
    print(m.name, m.date_of_birth, m.status)