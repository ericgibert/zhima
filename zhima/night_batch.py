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
import os
from shutil import copy2
from datetime import date
from member import Member
from send_email import send_email
from make_qrcode import make_qrcode

db = Member(debug=False)
images_path = os.path.dirname(os.path.realpath(__file__)) + "/images"
XCJ_LOGO = images_path + "/XCJ.png"
NOT_HAPPY = images_path + "/emoji-not-happy.jpg"
for m in db.select(columns="id", one_only=False, order_by="id"):
    member = Member(id=m['id'])
    print(member, member['status'])
    # if member's status is not OK then overwrite its QR code image else generate a new one
    qr_file = "{}/XCJ_{}.png".format(images_path, member.id)
    if member['status'] != "OK":
        copy2(NOT_HAPPY, qr_file)
        continue
    # else....
    qrcode_text = member.encode_qrcode()
    img = make_qrcode(qrcode_text)
    img.save(qr_file)
    if member["role"] == member.ROLE["GROUP"]: continue
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
                [XCJ_LOGO],
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
                [XCJ_LOGO],
                db.mailbox["server"], db.mailbox['port'],
                db.mailbox["username"], db.mailbox['password'],
                debug=0
            )
