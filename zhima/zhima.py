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
__version__ = "1.0.20180415 Hyderabad"
__email__ =  "ericgibert@yahoo.fr"
__license__ = "MIT"

import sys, os
from datetime import datetime
import signal
import argparse
from time import sleep
from camera import Camera
from rpi_gpio import Rpi_Gpio, _simulation as rpi_simulation
from member import Member
from tokydoor import TokyDoor
from model_db import Database
from send_email import send_email
# from http_view import http_view, stop as bottle_stop

class myQ(list):
    """Simple queue implementation to keep track of the member's entries"""
    def __init__(self, size=4):
        super().__init__()
        self.size = size

    def add(self, o):
        self.insert(0, o)
        try:
            del self[self.size]
        except IndexError:
            pass

class Controller(object):
    def __init__(self, bottle_ip='127.0.0.1', port=8080, debug=False):
        self.bottle_ip, self.port = bottle_ip, port
        self.db = Database()
        self.gpio = Rpi_Gpio(has_PN532=self.db.access["has_RFID"])
        self.debug = debug
        if rpi_simulation:
            print("PGIO simulation active")
        self.member = None
        self.TASKS = {
            1: self.wait_for_proximity,
            2: self.capture_qrcode,
            3: self.check_member,
            4: self.open_the_door_BOTH,   # coose the function to call: _RELAY, _BLE, _BOTH
            5: self.bad_member_status,
            6: self.unknown_qr_code,
           99: self.panic_mode,
        }
        self.camera = Camera(self.db) if self.db.access["has_camera"] else None
        self.last_entries = myQ()

    def insert_log(self, log_type, code, msg):
        """
        Insert a log record in the database for tracking and print a message on terminal
        :param log_type: OPEN / ERROR / NOT_OK
        :param msg: a free message
        """
        self.db.log(log_type, code, msg, debug=self.debug)

    def stop(self):
        """Clean up before stopping"""
        self.gpio.stop()
        if self.camera: self.camera.close()
        # bottle_stop()

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
        self.current_state = 1  # initial state: waiting for proximity detection
        # http_view.controller = self
        #thread.start_new_thread(http_view.run, (, ))
        # t = threading.Thread(target=http_view.run, kwargs={'host':self.bottle_ip, 'port': self.port})
        # t.start()
        try:
            while self.current_state:  # can be stopped by program by return a next state as 0
                task = self.TASKS[self.current_state]
                self.current_state = task()
        finally:
            self.stop()

    def wait_for_proximity(self):
        """State 1: Use GPIO to wait for a person to present
        - a mobile phone to the camera by checking the proximity detector
        - a RFID card by attempting to read a UID"""
        if self.debug: print("Entering state", self.current_state, self.TASKS[self.current_state].__name__)
        self.gpio.green1.flash("SET", on_duration=0.25, off_duration=1)
        self.gpio.green2.OFF()
        self.gpio.red.OFF()
        self.gpio.relay.OFF()
        self.gpio.proximity.reset()
        # display the waiting message
        points, max_pts = 1, 10
        next_state = 1
        self.qr_codes, self.uid = [], None
        while next_state == 1:
            if self.debug: print("Waiting for proximity", '.' * points, " " * max_pts, end="\r")
            sleep(0.2)
            points = (points + 1) % max_pts
            if self.db.access["has_camera"] and self.gpio.check_proximity():
                next_state = 2
            # Check if a card is available to read.
            if self.db.access["has_RFID"]:
                self.uid = self.gpio.pn532.read_passive_target(as_hex=True)
                if self.uid:
                    if self.debug: print("Read RFID UID", self.uid)
                    next_state = 3

        # while not self.gpio.check_proximity():
        #     if self.debug: print("Waiting for proximity", '.' * points, " " * max_pts, end="\r")
        #     sleep(0.2)
        #     points = (points + 1) % max_pts
        return next_state

    def capture_qrcode(self):
        """State 2: take photos until a QR code is detected"""
        if self.debug: print("Entering state", self.current_state, self.TASKS[self.current_state].__name__)
        self.gpio.green1.ON()
        self.gpio.green2.flash("SET", on_duration=0.5, off_duration=0.5)
        self.gpio.red.OFF()
        self.qr_codes = self.camera.get_QRcode(debug=self.debug) if self.camera else []
        if self.qr_codes is None:  # webcam is not working: panic mode: all LED flashing!
            return 99
        return 3 if self.qr_codes else 1  # qr_codes is a list --> 3, might be an empty one --> back to 1

    def double_sandwich(self):
        """Check if we need to give 6 months registration"""
        try:
            m1, m2, m3, m4 = [m for t,m in self.last_entries[:4]]
        except ValueError:
            return False
        if m1.id==m3.id==m4.id and m1.id!=m2.id and m1.is_staff():
            return (datetime.now() - self.last_entries[3][0]).seconds <= 20
        else:
            return False

    def single_sandwich(self):
        """Check if we need to give 6 months registration"""
        try:
            m1, m2, m3 = [m for t,m in self.last_entries[:3]]
        except ValueError:
            return False
        if m1.id==m3.id and m1.id!=m2.id and m1.is_staff():
            return (datetime.now() - self.last_entries[2][0]).seconds <= 15
        else:
            return False

    def check_member(self):
        """State 3: a QR Code is found: check it against the member database"""
        if self.debug: print("Entering state", self.current_state, self.TASKS[self.current_state].__name__)
        self.gpio.green1.ON()
        self.gpio.green2.ON()
        self.gpio.red.OFF()
        if self.qr_codes:
            # try finding a member from the database based on the first QR code found on the image
            # print("QR code:", self.qr_codes, type(self.qr_codes[0]))
            self.member = Member(qrcode=self.qr_codes[0])
            if self.member.id is None:
                self.insert_log("ERROR", -1000, "Non XCJ QR Code or No member found for: {}".format(self.qr_codes[0].decode("utf-8")))
        else:
            # try by RFID UID
            self.member = Member(openid=self.uid)
            if self.member.id is None:
                self.insert_log("ERROR", -1010, "Non XCJ registered RFID card: {}".format(self.uid))
        # if we have a member, let's check its status to open the door
        if self.member.id:
            self.last_entries.add( (datetime.now(), self.member) )  # stack for sandwich checking
            if self.double_sandwich():
                print("double sandwich")
            elif self.single_sandwich():
                print("single sandwich")
            else:
                print("no sandwich")
            if self.uid or self.member.qrcode_is_valid:
                if self.member['status'].upper() in ("OK", "ACTIVE", "ENROLLED"):
                    msg = "Welcome {} - {}".format(self.member['username'],
                                                   "RFID {}".format(self.uid) if self.uid else "QR v{}".format(self.member.qrcode_version))
                    self.insert_log("OPEN", self.member.id, msg)
                    return 4
                else:
                    self.insert_log("NOT_OK", self.member.id,
                                    "{}, please fix your status: {}".format(self.member['username'], self.member['status']))
                    return 5
        return 6

    def happy_flashing(self, duration):
        """Flash alternatively the green lights for 'duration' seconds"""
        on_off = 0
        for i in range(duration * 4):
            self.gpio.green1.set(on_off)
            on_off = int(not on_off)
            self.gpio.green2.set(on_off)
            sleep(0.25)

    def open_the_door_RELAY(self):
        """State 4: Proceed to open the door
            Open the door using the electric relay
        """
        if self.debug: print("Entering state", self.current_state, self.TASKS[self.current_state].__name__)
        self.gpio.relay.ON()
        self.happy_flashing(3)
        self.gpio.relay.OFF()
        return 1

    def open_the_door_BLE(self):
        """State 4: Proceed to open the door
        # Open the door using Bluetooth - all BLE parameters are defaulted for the TOKYDOOR BLE @ XCJ
        """
        if self.debug: print("Entering state", self.current_state, self.TASKS[self.current_state].__name__)
        tokydoor = TokyDoor(database=self.db)
        try:
            tokydoor.open()
        except ValueError as err:
            self.insert_log("ERROR", -1001, "Cannot connect to TOKYDOOR: {}".format(err))
            return 99 # cannot reach the BLE!!! Panic Mode!! 
        self.happy_flashing(3)
        return 1

    def open_the_door_BOTH(self):
        """State 4: Proceed to open the door
        Open the door using both Bluetooth - all BLE parameters are defaulted for the TOKYDOOR BLE @ XCJ
        and the electric relay
        """
        if self.debug: print("Entering state", self.current_state, self.TASKS[self.current_state].__name__)
        self.gpio.relay.ON()
        tokydoor = TokyDoor(database=self.db)
        try:
            tokydoor.open()
        except ValueError as err:
            self.insert_log("ERROR", -1001, "Cannot connect to TOKYDOOR: {}".format(err))
            return 99 # cannot reach the BLE!!! Panic Mode!!
        self.happy_flashing(3)
        self.gpio.relay.OFF()
        return 1

    def bad_member_status(self):
        """State 5: Member "bad status", email the member to warn about the status"""
        if self.debug: print("Entering state", self.current_state, self.TASKS[self.current_state].__name__)
        self.gpio.green1.OFF()
        self.gpio.green2.ON()
        self.gpio.red.ON()
        if self.member["email"]:
            print("Email to", self.member['username'])
            send_email(
                "Sorry, XCJ doorman cannot open the door for you",
                from_=self.member.mailbox["username"],
                to_=(self.member["email"],),
                message_HTML = """
                    <P>Your status in the XCJ database is set to: {}</P>
                    <p>You membership expiration date is {}</p>
                    <p></p>
                    """.format(self.member["status"], self.member.validity),
                images=[r"images/emoji-not-happy.jpg"],
                server=self.member.mailbox["server"], port=self.member.mailbox["port"],
                login=self.member.mailbox["username"], passwd=self.member.mailbox["password"]
            )
            sleep(1)  # let's say it takes 2 seconds to send the email already
        else:
            sleep(3)
        return 1

    def unknown_qr_code(self):
        """State 6: A QR code or RFID UID was read but does not match our known pattern OR no member found"""
        if self.debug: print("Entering state", self.current_state, self.TASKS[self.current_state].__name__)
        self.gpio.green1.ON()
        self.gpio.green2.OFF()
        self.gpio.red.ON()
        sleep(3)
        return 1

    def panic_mode(self):
        """State 99: major erro, flash the lights for 3 seconds"""
        if self.debug: print("Entering state", self.current_state, self.TASKS[self.current_state].__name__)
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
    parser.add_argument("-p", "--port", dest="port", help="Optional: port for HTTP (8080: test / 80: PROD)", required=False,  default=8080, type=int)
    parser.add_argument('-v', '--version', action='version', version=__version__)
    parser.add_argument('-d', '--debug', dest='debug', help='debug mode - kep photos', action='store_true', default=False)
    # parser.add_argument('config_file', nargs='?', default='')
    args, unk = parser.parse_known_args()
    ctrl = Controller(bottle_ip=args.bottle_ip, port=args.port, debug=args.debug)
    ctrl.run()
