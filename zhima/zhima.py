#!/usr/bin/env python3
""" Controller module

- Waits for the proximity detector to trigger the photo taking.
- Photos are scanned for QR Code
- QR code is match against a database of members
- if the member is OK then the door open else an email is triggered

"""
__author__ = "Eric Gibert"
__version__ = "1.0.20170113"
__email__ =  "ericgibert@yahoo.fr"
__license__ = "MIT"
from time import sleep
from camera import Camera
from rpi_gpio import Rpi_Gpio, _simulation as rpi_simulation

class Controller(object):
    def __init__(self):
        self.camera = Camera()
        self.gpio = Rpi_Gpio()
        if rpi_simulation:
            print("PGIO simulation active")
        self.member = None
        self.TASKS = {
            1: self.wait_for_proximity,
            2: self.capture_qrcode,
            3: self.check_member
        }

    def run(self):
        """
        Main loop to move from one state to the next
        :return:
        """
        current_state = 1  # initial state: waiting for proximity detection
        try:
            while current_state:  # can be stopped by program by return a next state as 0
                task = self.TASKS[current_state]
                current_state = task()
        finally:
            self.camera.close()

    def wait_for_proximity(self):
        """Use GPIO to wait for a person to present a mobile phone to the camera"""
        while not self.gpio.check_proximity():
            sleep(0.5)
        return 2

    def capture_qrcode(self):
        """take photos until a qr code is detected"""
        next_state = 3 if self.camera.get_QRcode() else 1
        return next_state

    def check_member(self):
        """a QR Code is found: check it against the member database"""
        print("Member with QR code:", self.camera.qr_codes)
        return 0

    # def get_ids(self):
    #     """
    #     Rules to extract a unique ID from the QR code
    #     wechat: b"https://u.wechat.com/IMuRawb-1GPWRTXrg_EVEuc" --> "IMuRawb-1GPWRTXrg_EVEuc"
    #
    #     """
    #     self.ids = []
    #     for qrc in self.qr_codes:
    #         parts = qrc.decode().split('/')
    #         self.ids.append(parts[-1])
    #
    # def wechat_id(self):
    #     api_token = 'IK24sHIRPvy7ujeXYFKKCRs'
    #     api_url_base = 'https://u.wechat.com/'
    #     headers = {'Content-Type': 'application/json'}
    #     # 'Authorization': 'Bearer {0}'.format(api_token)}
    #     response = requests.get(api_url_base + api_token, headers=headers)
    #     if response.status_code == 200:
    #         print("response", response)
    #         return json.loads(response.content.decode('utf-8'))
    #     else:
    #         return None

if __name__ == "__main__":
    ctrl = Controller()
    ctrl.run()