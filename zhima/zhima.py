#!/usr/bin/env python3
""" Controller module

- Waits for the proximity detector to trigger the photo taking.
- Photos are scanned for QR Code
- QR code is match against a database of members
- if the member is OK then the door open else an email is triggered

Error Code for the LED:
Green1: proximity
Green 2: camera/photo taking & processing
Red: Error
Gr1 Gr2 Red
 -   -   O  Barcode not recognized (3 seconds)
 O   -   O  State 6:  XCJ Barcode for an unknown member (fails to decode the barcode to atch a db record)
 -   O   O  State 5:  XCJ Barcode for a "bad status" member (finds a db record but the member is not OK)
 O   O   O  State 99: Panic Mode: camera is malfunctioning, ...

"""
__author__ = "Eric Gibert"
__version__ = "1.0.20180204"
__email__ =  "ericgibert@yahoo.fr"
__license__ = "MIT"
import sys, os
import signal
import threading
import argparse
from time import sleep
from camera import Camera
from rpi_gpio import Rpi_Gpio, _simulation as rpi_simulation
from member_db import Member
from tokydoor import TokyDoor
from model_db import Database
# from http_view import http_view, stop as bottle_stop


class Controller(object):
    def __init__(self, bottle_ip=None):
        self.bottle_ip = bottle_ip or '127.0.0.1'
        self.gpio = Rpi_Gpio()
        self.db = Database()
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
           99: self.panic_mode,
        }
        self.camera = Camera(self.db)

    def insert_log(self, log_type, code, msg, member_id=-1, qrcode_version='?'):
        """
        Insert a log record in the database for tracking and print a message on terminal
        :param log_type: OPEN / ERROR / NOT_OK
        :param msg: a free message
        :param qrcode_version: if QR Code is found then record its version (tracking old QR Codes)
        :param member_id: if the QR Code matches a Member Id
        """
        self.db.log(log_type, code, msg, debug=True)

    def run(self):
        """
        Main loop to move from one state to the next
        :return:
        """
        with open("zhima.pid", "wt") as fpid:
            print(os.getpid(), file=fpid)
        def stop_handler(signum, frame):
            """ allow:   kill -10 `cat ponicwatch.pid`   """
            self.stop()
            sys.exit()
        signal.signal(signal.SIGUSR1, stop_handler)
        current_state = 1  # initial state: waiting for proximity detection
        # http_view.controller = self
        #thread.start_new_thread(http_view.run, (, ))
        # t = threading.Thread(target=http_view.run, kwargs={'host':self.bottle_ip})
        # t.start()
        try:
            while current_state:  # can be stopped by program by return a next state as 0
                task = self.TASKS[current_state]
                current_state = task()
        finally:
            # clean up before stop
            self.camera.close()
            # bottle_stop()

    def wait_for_proximity(self):
        """State 1: Use GPIO to wait for a person to present a mobile phone to the camera"""
        self.gpio.green1.flash("SET", on_duration=0.25, off_duration=1)
        self.gpio.green2.OFF()
        self.gpio.red.OFF()
        self.gpio.relay.OFF()
        points, max_pts = 1, 10
        while not self.gpio.check_proximity():
            print("Waiting for proximity", '.' * points, " " * max_pts, end="\r")
            sleep(1)
            points = 1 if points==max_pts else points+1
        return 2

    def capture_qrcode(self):
        """State 2: take photos until a QR code is detected"""
        self.gpio.green1.ON()
        self.gpio.green2.flash("SET", on_duration=0.5, off_duration=0.5)
        self.gpio.red.OFF()
        self.qr_codes = self.camera.get_QRcode()
        if self.qr_codes is None:  # webcam is not working: panic mode: all LED flashing!
            return 99
        next_state = 3 if self.qr_codes else 1  # qr_codes is a list, might be an empty one...
        return next_state

    def check_member(self):
        """State 3: a QR Code is found: check it against the member database"""
        self.gpio.green1.ON()
        self.gpio.green2.ON()
        self.gpio.red.OFF()
        # print("QR code:", self.qr_codes, type(self.qr_codes[0]))
        # try finding a member from the database based on the first QR code found on the image
        self.member = Member(self.db, qrcode=self.qr_codes[0])
        if self.member.id and self.member.qrcode_is_valid:
            if self.member.status.upper() in ("OK", "ACTIVE", "ENROLLED"):
                self.insert_log("OPEN", self.member.id, "Welcome {} - QR V{}".format(self.member.name, self.member.qrcode_version))
                print()
                return 4
            else:
                self.insert_log("NOT_OK", self.member.id,
                                "{}, please fix your status: {} - QR V{}".format(self.member.name, self.member.status,self.member.qrcode_version))
                return 5
        else:
            self.insert_log("ERROR", 1000, "Non XCJ QR Code or No member found for: {}".format(self.qr_codes[0].decode("utf-8")))
            return 6

    def open_the_door(self):
        """State 4: Proceed to open the door"""
        # Open the door using the electric relay
        self.gpio.relay.ON()  
        # Happy flashing
        val = 0
        for i in range(10):
            self.gpio.green1.set(val)
            val = int(not val)
            self.gpio.green2.set(val)
            sleep(0.3)  # 0.3 x 10 = 3 seconds == ONCE BLE command duration
        self.gpio.relay.OFF()
        return 1          
          
    def open_the_door_BLE(self):
        """State 4: Proceed to open the door"""
        # Open the door using Bluetooth - all BLE parameters are defaulted for the TOKYDOOR BLE @ XCJ
        tokydoor = TokyDoor(database=self.db)
        try:
            tokydoor.open()
        except ValueError as err:
            self.insert_log("ERROR", 1001, "Cannot connect to TOKYDOOR: {}".format(err))
            return 99 # cannot reach the BLE!!! Panic Mode!! 
        # Happy flashing
        val = 0
        for i in range(10):
            self.gpio.green1.set(val)
            val = int(not val)
            self.gpio.green2.set(val)
            sleep(0.3)  # 0.3 x 10 = 3 seconds == ONCE BLE command duration
        return 1

    def bad_member_status(self):
        """State 5: Member "bad status", email the member to warn about the status"""
        self.gpio.green1.OFF()
        self.gpio.green2.ON()
        self.gpio.red.ON()
        print("Email to", self.member.name)
        sleep(3)
        return 1

    def unknown_qr_code(self):
        """State 6: A QR code was read but does not match our known pattern OR no member found"""
        self.gpio.green1.ON()
        self.gpio.green2.OFF()
        self.gpio.red.ON()
        sleep(3)
        return 1

    def panic_mode(self):
        """State 99: major erro, flash the lights for 3 seconds"""
        self.gpio.green1.flash("SET", on_duration=0.3, off_duration=0.3)
        self.gpio.green2.flash("SET", on_duration=0.3, off_duration=0.3)
        self.gpio.red.flash("SET", on_duration=0.3, off_duration=0.3)
        sleep(3)
        self.gpio.green1.OFF()
        self.gpio.green1.OFF()
        self.gpio.green1.OFF()
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--bottle", dest="bottle_ip", help="Optional: Raspberry Pi IP address to allow remote connections", required=False,  default="127.0.0.1")
    parser.add_argument('-v', '--version', action='version', version=__version__)
    # parser.add_argument('config_file', nargs='?', default='')
    args, unk = parser.parse_known_args()
    ctrl = Controller(bottle_ip=args.bottle_ip)
    ctrl.run()
