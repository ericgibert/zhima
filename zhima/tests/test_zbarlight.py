import sys
from PIL import Image
import zbarlight

def find_qrcode(file_path):
    with open(file_path, 'rb') as image_file:
        image = Image.open(image_file)
        image.load()
    codes = zbarlight.scan_codes('qrcode', image)
    print('QR codes in {}: {}'.format(file_path, codes))
    return codes

if __name__ == "__main__":
    for f in sys.argv[1:]:
        find_qrcode(f)



