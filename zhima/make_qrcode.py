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
import zbarlight
from member_db import Member

XCJ_LOGO = "../Private/XCJ.png"
QR_CODE_QUALITY = {
    'M': qrcode.constants.ERROR_CORRECT_M,
    'Q': qrcode.constants.ERROR_CORRECT_Q,
    'H': qrcode.constants.ERROR_CORRECT_H,
}

def find_qrcode(file_path):
    with open(file_path, 'rb') as image_file:
        image = Image.open(image_file)
        image.load()
    codes = zbarlight.scan_codes('qrcode', image)
    # print('QR codes in {}: {}'.format(file_path, codes))
    return codes

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
    arg_id = parser.add_argument("-m", "--member_id", dest="member_id", help="Member ID in the database", default=None, required=True)
    arg_name = parser.add_argument("-n", "--member_name", dest="member_name", help="Member name", default=None)
    parser.add_argument("-o", "--output", dest="output", help="Output file (.png)", default="")
    parser.add_argument("-l", "--logo", dest="logo", help="XCJ logo file (.png)", default=XCJ_LOGO)
    parser.add_argument("-q", "--quality", dest="quality", help="QR Code quality [M,Q,H]", default='H')
    args, unk = parser.parse_known_args()

    if args.member_name is None:  # if only the member ID is given then fetch in the database
        current_member = Member(args.member_id)
        if current_member.id is None:
            raise argparse.ArgumentError(arg_id, message="Unknown Member ID {}".format(args.member_id))
        qrcode_text = "{} @ XCJ #{}".format(current_member.name, current_member.id)
    else: # both given: make it directly
        qrcode_text = "{} @ XCJ #{}".format(args.member_name, args.member_id)
    qr_file = args.output or "/tmp/{}_xcj.png".format(args.member_name or current_member.name)

    img = make_qrcode(qrcode_text, QR_CODE_QUALITY[args.quality], logo=args.logo)
    img.save(qr_file)
    qrc = find_qrcode(qr_file)
    print("QR Code {} generated with {} quality and controlled:\n".format(qr_file, args.quality), qrc)

    # for err in (qrcode.constants.ERROR_CORRECT_M, qrcode.constants.ERROR_CORRECT_Q, qrcode.constants.ERROR_CORRECT_H):
    #     img = make_qrcode(txt, err)
    #     img.save(qr_file)
    #     qrc = find_qrcode(qr_file)
    #     print(err, qrc)
    #     # if qrc: break