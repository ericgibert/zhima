#!/usr/bin/env python3
""" Take a photo with the attached camera on the Raspi
# or emulate the raspi library with OpenCV and the webcam
#
# http://picamera.readthedocs.io/en/release-1.13/recipes1.html
#
# Author: Eric Gibert, QR codes: [b'https://u.wechat.com/IMuRawb-1GPWRTXrg_EVEuc']
"""
__author__ = "Eric Gibert"
__version__ = "1.20170113"
__email__ =  "ericgibert@yahoo.fr"
__license__ = "MIT"

from time import sleep
from tempfile import mkstemp
from PIL import Image
import zbarlight
import cv2

class Camera():
    """take a photo and keep it in memory for processing"""
    def __init__(self):
        """open the camera hardware"""
        self.camera = cv2.VideoCapture(0)
        # self.camera.set(3, 640*2)
        # self.camera.set(4, 480 * 2)
        # # self.camera.resolution = (640*2, 480*2)

    def close(self):
        """release the hardware"""
        self.camera.release()
        del(self.camera)

    def save_photo(self, file_path=None):
        """save the current image"""
        _, self.file_path = mkstemp(prefix="QR-",suffix=".png", text=False) if file_path is None else (None, file_path) #open(file_path, mode="wb"))
        cv2.imwrite(self.file_path, self.image)

    def get_QRcode(self, max_photos=20):
        """take max_photos until a QR code is found else returns []"""
        for i in range(max_photos):
            print("Taking photo", i)
            try:
                cv2_return_code, cv2_im = self.camera.read()
            except cv2.error as cv2_err:
                print("Error with the camera:", cv2_err)
                self.close()
                self.camera = cv2.VideoCapture(0)
            else:
                # # img = cv2.cvtColor(cv2_im, cv2.COLOR_BGR2GRAY);
                # # img = cv2.equalizeHist(cv2_im)  #cv2.cvtColor(cv2_im, cv2.COLOR_BGR2RGB)
                # img_yuv = cv2.cvtColor(cv2_im, cv2.COLOR_BGR2YUV)
                # # equalize the histogram of the Y channel
                # img_yuv[:, :, 0] = cv2.equalizeHist(img_yuv[:, :, 0])
                # # convert the YUV image back to RGB format
                # img = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)
                self.image = Image.fromarray(cv2_im)
                self.qr_codes = zbarlight.scan_codes('qrcode', self.image)
                if self.qr_codes:
                    # self.image.show()
                    return self.qr_codes
                # else:
                    sleep(0.4)
        else:
            # self.image.show()
            return []


if __name__ == "__main__":
    my_camera = Camera()
    # my_camera.take_photo()
    # print("Photo taken:", my_camera.file_path)
    # my_camera.close()
    qr_codes = my_camera.get_QRcode()
    print("QR codes:", qr_codes)
    # ids = my_camera.get_ids()
    # print("Hello", who_is_who[ids[0]])
    my_camera.close()