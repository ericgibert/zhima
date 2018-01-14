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
from member_db import Member

class Controller(object):
    def __init__(self):
        self.gpio = Rpi_Gpio()
        if rpi_simulation:
            print("PGIO simulation active")
        self.member = None
        self.TASKS = {
            1: self.wait_for_proximity,
            2: self.capture_qrcode,
            3: self.check_member,
            4: self.open_the_door,
            5: self.bad_member_status,
            6: self.unknown_qr_code,
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
            # clean up before stop
            pass

    def wait_for_proximity(self):
        """Use GPIO to wait for a person to present a mobile phone to the camera"""
        self.gpio.green1.flash("SET", on_duration=0.25, off_duration=1)
        self.gpio.green2.OFF()
        self.gpio.red.OFF()
        points, max_pts = 1, 10
        while not self.gpio.check_proximity():
            print("Waiting for proximity", '.' * points, " " * max_pts, "\r", end="")
            sleep(0.5)
            points = 1 if points==max_pts else points+1
        return 2

    def capture_qrcode(self):
        """take photos until a qr code is detected"""
        self.gpio.green1.ON()
        self.gpio.green2.flash("SET", on_duration=0.5, off_duration=0.5)
        self.gpio.red.OFF()
        with Camera() as cam:
            self.qr_codes = cam.get_QRcode()
        next_state = 3 if self.qr_codes else 1
        return next_state

    def check_member(self):
        """a QR Code is found: check it against the member database"""
        self.gpio.green1.ON()
        self.gpio.green2.ON()
        self.gpio.red.OFF()
        print("QR code:", self.qr_codes)
        # algo to split the member_if from the QR code
        qr_code = self.qr_codes[0].decode("utf-8")
        try:
            name, id = qr_code.split('#')
        except ValueError:
            return 6
        member = Member(id)
        if member.id:
            if member.status.upper()=="OK":
                print("Welcome", member.name, "!")
                return 4
            else:
                print(member.name, "please fix your status:", member.status)
                return 5
        else:
            print("Sorry, I do not know you", name)
        return 1

    def open_the_door(self):
        """Proceed to open the door"""
        val = 0
        for i in range(10):
            self.gpio.green1.set(val)
            val = int(not val)
            self.gpio.green2.set(val)
            sleep(0.3)
        return 1

    def bad_member_status(self):
        """Red LED and email the member to warn about the status"""
        self.gpio.red.ON()
        sleep(3)
        self.gpio.red.OFF()
        return 1

    def unknown_qr_code(self):
        """A QR code was read but does not match our known pattern"""
        self.gpio.green2.flash("SET", on_duration=0.5, off_duration=0.5)
        print("Unknown QR Code:", self.qr_codes[0].decode("utf-8"))
        self.gpio.red.ON()
        sleep(3)
        self.gpio.red.OFF()
        return 1

if __name__ == "__main__":
    ctrl = Controller()
    ctrl.run()