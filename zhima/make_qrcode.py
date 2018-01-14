#!/usr/bin/env python3
""" Utility to generate the XCJ QR codes
"""
__author__ = "Eric Gibert"
__version__ = "1.0.20170113"
__email__ =  "ericgibert@yahoo.fr"
__license__ = "MIT"
import argparse
import qrcode
from PIL import Image
from tests.test_zbarlight import find_qrcode

XCJ_LOGO = "./Private/XCJ.png"

def make_qrcode(text, error_correct = qrcode.constants.ERROR_CORRECT_H, logo=XCJ_LOGO):
    qr = qrcode.QRCode(
        version=3,
        error_correction=error_correct,  #  qrcode.constants.ERROR_CORRECT_Q,  #  or _H
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image()
    xcj = Image.open(logo)
    box = (135,135,235,235)
    region = xcj.resize((box[2] - box[0], box[3] - box[1]))
    img.paste(region, box)
    return img

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Utility to generate the XCJ Member QR Code with logo included')
    parser.add_argument("-m", "--member_id", dest="member_id", help="Member ID in the database")
    parser.add_argument("-n", "--member_name", dest="member_name", help="Member name")
    parser.add_argument("-o", "--output", dest="output", help="Output file (.png)")
    parser.add_argument("-l", "--logo", dest="logo", help="XCJ logo file (.png)", default=XCJ_LOGO)
    args, unk = parser.parse_known_args()

    # if only the member ID is given then fetch in the database


    txt = 'Eric Gibert @ XCJ #123456'
    qr_file = "/tmp/eric_gibert_xcj.png"
    for err in (qrcode.constants.ERROR_CORRECT_M, qrcode.constants.ERROR_CORRECT_Q, qrcode.constants.ERROR_CORRECT_H):
        img = make_qrcode(txt, err)
        img.save(qr_file)
        qrc = find_qrcode(qr_file)
        print(err, qrc)
        # if qrc: break