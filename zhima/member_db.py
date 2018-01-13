#!/usr/bin/env python3
""" Simple member database access

    Connects to the database or emulate a connection
    Check the existence of a member
    If a member is found then check that he paid his due
"""
__author__ = "Eric Gibert"
__version__ = "1.0.20170113"
__email__ =  "ericgibert@yahoo.fr"
__license__ = "MIT"

try:
    import pigpio
    _simulation = False
except ImportError:
    _simulation = True

SIMULATION = {
    123456: { "name": "Eric Gibert", "status": "ok"},
}

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
