import qrcode
from PIL import Image
from tests.test_zbarlight import find_qrcode


def make_qrcode(text, error_correct = qrcode.constants.ERROR_CORRECT_Q, logo="/tmp/XCJ.png"):
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
    txt = 'Eric Gibert @ XCJ #123456'
    qr_file = "/tmp/eric_gibert_xcj.png"
    for err in (qrcode.constants.ERROR_CORRECT_M, qrcode.constants.ERROR_CORRECT_Q, qrcode.constants.ERROR_CORRECT_H):
        img = make_qrcode(txt, err)
        img.save(qr_file)
        qrc = find_qrcode(qr_file)
        print(err, qrc)
        if qrc: break