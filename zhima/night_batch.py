#!/usr/bin/env python3
"""
Executed every night at 0:01AM

- for each user:
    - check if we need a reminder 7 days before expiration
    - check if we need a reminder when expiration is reached + change status to NOT_OK

"""
__author__ = "Eric Gibert"
__version__ = "1.0.20180520 Dong Bei"
__email__ =  "ericgibert@yahoo.fr"
__license__ = "MIT"

from datetime import date
from member import Member
from send_email import send_email

db = Member(debug=True)

for m in db.select(columns="id", one_only=False):
    member = Member(id=m['id'])
    print(member, member['status'])
    if member["role"] == member.ROLE["GROUP"]: continue
    if member['status'] != "OK": continue
    if (member['validity'] - date.today()).days == 7:
        print("7 days!")
        if member['email']:
            send_email(
                "Your membership to Xin Che Jian will expire in one week",
                db.mailbox["username"],
                (member['email'], ),
                """
Dear {},

This message to inform you that we noticed that your membership to Xin Che Jian hackerspace will expire on {}.

Please approach one of our staff during your next visit to renew it.

Looking forward seeing you @ XCJ!
                """.format(member['username'], member['validity']),
                """
<h3>Dear {},</h3>
<p>
This message to inform you that we noticed that your membership to Xin Che Jian hackerspace will expire on <b>{}</b>.
<br>
Please approach one of our staff during your next visit to renew it.
<br>
Looking forward seeing you @ XCJ!
</p>
    """.format(member['username'], member['validity']),
                ["images/XCJ.png"],
                db.mailbox["server"], db.mailbox['port'],
                db.mailbox["username"], db.mailbox['password'],
                debug=0
        )
    elif date.today() > member['validity']:
        print("Expired!")
        member.update(id=member.id, status="NOT_OK")
        if member['email']:
            send_email(
                "Your membership to Xin Che Jian has expired",
                db.mailbox["username"],
                (member['email'], ),
                """
Dear {},

This message to inform you that your membership to Xin Che Jian hackerspace has expired today.

Please approach one of our staff during your next visit to renew it.

Looking forward seeing you @ XCJ!""".format(member['username']),
                """
<h3>Dear {},</h3>
<p>
This message to inform you that your membership to Xin Che Jian hackerspace has expired today.
<br>
Please approach one of our staff during your next visit to renew it.
<br>
Looking forward seeing you @ XCJ!
</p>""".format(member['username']),
                #["images/XCJ.png"],
                db.mailbox["server"], db.mailbox['port'],
                db.mailbox["username"], db.mailbox['password'],
                debug=0
            )
