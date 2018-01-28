#!/usr/bin/env python3
""" Take a photo with the attached camera on the Raspi
# or emulate the raspi library with OpenCV and the webcam
#
# http://picamera.readthedocs.io/en/release-1.13/recipes1.html
#
# Author: Eric Gibert, QR codes: [b'https://u.wechat.com/IMuRawb-1GPWRTXrg_EVEuc']
"""
__author__ = "Eric Gibert"
__version__ = "1.0.20170113"
__email__ =  "ericgibert@yahoo.fr"
__license__ = "MIT"

from time import sleep
from tempfile import mkstemp
from PIL import Image
import zbarlight
import cv2
try:
    import picamera
    import picamera.array
    has_picamera = True
except ImportError:
    has_picamera = False

class Camera():
    """take a photo and keep it in memory for processing"""
    def __init__(self, database=None):
        """open the camera hardware"""
        self.db = database
        self.camera = picamera.PiCamera() if has_picamera else cv2.VideoCapture(0)
        # self.camera.set(3, 640*2)
        # self.camera.set(4, 480 * 2)
        # # self.camera.resolution = (640*2, 480*2)
        self.qr_codes = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """release the hardware"""
        if has_picamera:
            pass
        else:
            self.camera.release()
        del(self.camera)

    def save_photo(self, file_path=None):
        """save the current image"""
        _, self.file_path = mkstemp(prefix="QR-",suffix=".png", text=False) if file_path is None else (None, file_path) #open(file_path, mode="wb"))
        cv2.imwrite(self.file_path, self.cv2_img)
        return self.file_path

    def get_QRcode(self, max_photos=20, debug=False):
        """take max_photos until a QR code is found else returns []"""
        self.qr_codes = []  # reset any previous QR code found
        self.image = None
        for i in range(max_photos):
            print("Taking photo", i, end="\r")
            sleep(0.1)
            if has_picamera:
                with picamera.array.PiRGBArray(self.camera) as stream:
                    self.camera.capture(stream, format='bgr')
                    # At this point the image is available as stream.array
                    self.cv2_img = stream.array
            else:
                try:
                    cv2_return_code, self.cv2_img = self.camera.read()
                except cv2.error as cv2_err:
                    msg = "Error with the camera: {}".format(cv2_err)
                    if self.db:
                        self.db.log("ERROR", 3000, msg, debug=debug)
                    else:
                        print(msg)
                    return None

            try:
                self.image = Image.fromarray(self.cv2_img)
                self.qr_codes = zbarlight.scan_codes('qrcode', self.image)
            except AttributeError as err:
                msg = "Photo not taken properly: {}".format(err)
                if self.db:
                    self.db.log("WARNING", 3001, msg, debug=debug)
                else:
                    print(msg)
                # self.close()
                # self.camera = cv2.VideoCapture(0)
                return None
            if self.qr_codes:
                if debug: self.image.show()
                print("\n")
                return self.qr_codes

        else:
            if debug:self.image.show()
            print("\n")
            return []


if __name__ == "__main__":
    with Camera() as my_camera:
        qr_codes = my_camera.get_QRcode(debug=True)
        print("QR codes:", qr_codes)
        print(my_camera.save_photo())
