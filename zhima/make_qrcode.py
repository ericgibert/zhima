#!/usr/bin/env python3
""" Utility to generate the XCJ QR codes
"""
__author__ = "Eric Gibert"
__version__ = "1.0.20170113"
__email__ =  "ericgibert@yahoo.fr"
__license__ = "MIT"
import os
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
    img_size = img.pixel_size // 2  # 410x410px for H quality
    LOGO_SIZE = 100 // 2            # logo on 100x100px
    box =  (img_size - LOGO_SIZE, img_size - LOGO_SIZE, img_size + LOGO_SIZE, img_size + LOGO_SIZE) #(135, 135, 235, 235)
    xcj = Image.open(logo)
    region = xcj.resize((box[2] - box[0], box[3] - box[1]))
    img.paste(region, box)
    return img

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Utility to generate the XCJ Member QR Code with logo included')
    arg_id = parser.add_argument("-m", "--member_id", dest="member_id", help="Member ID in the database", default=None, type=int)
    arg_name = parser.add_argument("-n", "--member_name", dest="member_name", help="Member name", default=None)
    parser.add_argument("-o", "--output", dest="output", help="Output file (.png)", default="")
    parser.add_argument("-d", "--directory", dest="directory", help="Output directory", default="/tmp")
    parser.add_argument("-l", "--logo", dest="logo", help="XCJ logo file (.png)", default=XCJ_LOGO)
    parser.add_argument("-q", "--quality", dest="quality", help="QR Code quality [M,Q,H]", default='H')
    parser.add_argument("-v", "--version", dest="qrcode_version", help="QR Code version", default=1, type=int)
    args, unk = parser.parse_known_args()
    # a member ID must be provided either after the -m option or as free argument
    if args.member_id is None:
        if unk:
            args.member_id = int(unk[0])
        else:
            raise argparse.ArgumentError(arg_id, message="Missing Member ID")
    # optional: if no member's name is given then fetch record from DB else create a QR Code without DB record
    if args.member_name is None:  # if only the member ID is given then fetch in the database
        current_member = Member(args.member_id)
        if current_member.id is None:
            raise argparse.ArgumentError(arg_id, message="Unknown Member ID {}".format(args.member_id))
    else: # both given: make it directly without DB selection
        current_member = Member()
        current_member.id, current_member.name = args.member_id, args.member_name

    qrcode_text = current_member.encode_qrcode()
    qr_file = args.output or os.path.join(args.directory, "XCJ_{}.png".format(current_member.id))
    img = make_qrcode(qrcode_text, QR_CODE_QUALITY[args.quality], logo=args.logo)
    img.save(qr_file)
    # test that the QR Code is valid
    qrc = find_qrcode(qr_file)
    print("QR Code {} generated with {} quality and controlled:\n".format(qr_file, args.quality), qrc)
