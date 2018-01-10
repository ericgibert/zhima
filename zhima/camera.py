# Take a photo with the attached camera on the Raspi
# or emulate the raspi library with OpenCV and the webcam
#
# http://picamera.readthedocs.io/en/release-1.13/recipes1.html
#
# Author: Eric Gibert, QR codes: [b'https://u.wechat.com/IMuRawb-1GPWRTXrg_EVEuc']
import json
import requests
from tempfile import mkstemp
from PIL import Image
import zbarlight
try:
    import picamera     # only on the Raspi
    has_picam = True
except ImportError:
    import cv2
    has_picam = False

who_is_who = {
    "https://u.wechat.com/MELUOLu3h0BAxtYZavZp_i4": "Remy Gibert",
    "https://u.wechat.com/IMuRawb-1GPWRTXrg_EVEuc": "Eric Gibert"
    # QR codes: [b'https://u.wechat.com/IK24sHIRPvy7ujeXYFKKCRs']
}


class Camera():
    """take a photo and keep it in memory for processing"""
    def __init__(self):
        """open the camera hardware"""
        self.camera = picamera.PiCamera() if has_picam else cv2.VideoCapture(0)
        # camera.resolution = (1024, 768)  to try later...

    def close(self):
        """release the hardware"""
        del(self.camera)

    def take_photo(self, file_path=None):
        """take a photo"""
        _, self.file_path = mkstemp(prefix="QR-",suffix=".png", text=False) if file_path is None else (None, file_path) #open(file_path, mode="wb"))
        if has_picam:
            self.camera.capture(self.file_path, 'png')
        else:
            return_value, img = self.camera.read()
            cv2.imwrite(self.file_path, img)

    def get_QRcode(self):
        """Get the QR code from the photo taken"""
        with open(self.file_path, 'rb') as image_file:
            image = Image.open(image_file)
            image.load()
        self.qr_codes = zbarlight.scan_codes('qrcode', image)
        return self.qr_codes

    def get_ids(self):
        """
        Rules to extract a unique ID from the QR code
        wechat: b"https://u.wechat.com/IMuRawb-1GPWRTXrg_EVEuc" --> "IMuRawb-1GPWRTXrg_EVEuc"

        """
        self.ids = []
        for qrc in self.qr_codes:
            parts = qrc.decode().split('/')
            self.ids.append(parts[-1])

    def wechat_id(self):
        api_token = 'IK24sHIRPvy7ujeXYFKKCRs'
        api_url_base = 'https://u.wechat.com/'
        headers = {'Content-Type': 'application/json'}
                   # 'Authorization': 'Bearer {0}'.format(api_token)}
        response = requests.get(api_url_base+api_token, headers=headers)
        if response.status_code == 200:
            print("response", response)
            return json.loads(response.content.decode('utf-8'))
        else:
            return None

if __name__ == "__main__":
    my_camera = Camera()
    my_camera.take_photo()
    print("Photo taken:", my_camera.file_path)
    my_camera.close()
    qr_codes = my_camera.get_QRcode()
    print("QR codes:", qr_codes)
    ids = my_camera.get_ids()
    print("Hello", who_is_who[ids[0]])