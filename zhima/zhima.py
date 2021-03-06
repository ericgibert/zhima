#!/usr/bin/env python3
""" Controller module

- Waits for the proximity detector to trigger the photo taking.
- Photos are scanned for QR Code
- QR code is match against a database of members
- if the member is OK then the door open else an email is triggered

Normal LED flashing:
Green 1: flash while waiting for proximity or RFID
Green 1+2: camera/photo taking & processing/RFID recognized
Happy Flashing G1&2: Access granted/Door open

Error Code for the LED:
Gr1 Gr2 Red
 -   -   O  Barcode not recognized (3 seconds)
 O   -   O  State 6:  XCJ Barcode for an unknown member (fails to decode the barcode)
 -   O   O  State 5:  XCJ Barcode/RFID for a "bad status" member (finds a db record but the member is not OK)
 O   O   O  State 99: Panic Mode: camera is malfunctioning, database unavailable...

"""
__author__ = "Eric Gibert"
__version__ = "1.0.20180602 Dong Bei - RFID"
__email__ =  "ericgibert@yahoo.fr"
__license__ = "MIT"

import sys, os
from datetime import datetime, timedelta
import requests
import signal
import argparse
from time import sleep
from camera import Camera
from rpi_gpio import Rpi_Gpio
from member_api import Member_Api
from tokydoor import TokyDoor
from model_db import Database
from send_email import send_email

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
    def __init__(self, bottle_ip=None, port=8080, debug=False):
        self.bottle_ip, self.port = bottle_ip, port
        self.debug = debug
        # init local attributes
        self.db = Database()
        if debug:
            print("has_RFID:", self.db.access["has_RFID"])
            print("has_camera:", self.db.access["has_camera"])
            print("open_with:", self.db.access["open_with"])
            print("wait_to_close:", self.db.access["wait_to_close"])
        self.base_api_url = "http://{}:8080/api/v1.0".format(bottle_ip or Database.server_ip)
        self.gpio = Rpi_Gpio(has_PN532=self.db.access["has_RFID"])
        self.member = None
        _OPEN_WITH = {
            "BLE": self.open_the_door_BLE,
            "RELAY": self.open_the_door_RELAY,
            "BOTH": self.open_the_door_BOTH,
            "API": self.open_the_door_API,
        }
        self.TASKS = {
            1: self.wait_for_proximity,
            2: self.capture_qrcode,
            3: self.check_member,
            4: _OPEN_WITH[self.db.access["open_with"]],  # choose the function to call: _RELAY, _BLE, _BOTH, _API
            5: self.bad_member_status,
            6: self.unknown_qr_code,
            7: self.wait_to_close_the_door,  #  self.db.access["wait_to_close"] is 0 or 1 (False/True)
           98: self.panic_no_db,
           99: self.panic_mode,
        }
        self.camera = Camera(self.db) if self.db.access["has_camera"] else None
        self.last_entries = myQ()
        # veifies that the database is accessible
        url = "{}/member/{}".format(self.base_api_url, 1)
        try:
            response = requests.get(url)
            print("Connected and member fetched:", response)
        except requests.ConnectionError as conn_err:
            print("Cannot start due to", conn_err)
            exit(98)


    def insert_log(self, log_type, code, msg):
        """
        Insert a log record in the database for tracking and print a message on terminal
        :param log_type: OPEN / ERROR / NOT_OK
        :param msg: a free message
        """
        # self.db.log(log_type, code, msg, debug=self.debug)
        url = "{}/log/add".format(self.base_api_url)
        payload={
            "log_type": log_type,
            "code": code,
            "msg": msg,
            "debug": self.debug
        }
        try:
            response = requests.post(url, json=payload)
        except requests.ConnectionError as conn_err:
            self.panic_no_db()
            return 98
        if response.status_code == 201:
            if self.debug:
                print(payload)
                print(response.text)
        else:
            print("Cannot create Log entry with response.status_code:", response.status_code)


    def stop(self):
        """Clean up before stopping"""
        self.gpio.pig.stop()
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
            # sleep(0.2)
            if self.debug:
                print("Waiting for proximity", '.' * points, " " * max_pts, end="\r")
                points = (points + 1) % max_pts
            if self.gpio.check_proximity():
                next_state = 2 if self.db.access["has_camera"] else 4 # take QR Code photo / open the door immediately
                break
            # Check if a card is available to read.
            if self.db.access["has_RFID"]:
                try:
                    self.uid = self.gpio.pn532.read_passive_target(as_hex=True)
                except RuntimeError as err:
                    print(err)
                    return 99
                if self.uid:
                    if self.debug: print("Read RFID UID", self.uid)
                    next_state = 3
                else:
                    sleep(0.2)  # to prevent over heating the RFID card reader
        return next_state

    def capture_qrcode(self):
        """State 2: take photos until a QR code is detected"""
        if self.debug: print("Entering state", self.current_state, self.TASKS[self.current_state].__name__)
        self.gpio.green1.ON()
        self.gpio.green2.flash("SET", on_duration=0.5, off_duration=0.5)
        self.gpio.red.OFF()
        self.qr_codes = self.camera.get_QRcode(max_photos=2, debug=self.debug) if self.camera else []
        if self.qr_codes is None:  # webcam is not working: panic mode: all LED flashing!
            return 99
        return 3 if self.qr_codes else 1  # qr_codes is a list --> 3, might be an empty one --> back to 1

    def double_sandwich(self):
        """Check if we need to give 6 months membership registration"""
        try:
            m1, m2, m3, m4 = [m for t,m in self.last_entries[:4]]
        except ValueError:
            return False
        if m1.id==m3.id==m4.id and m1.id!=m2.id and m1.is_staff:
            return (datetime.now() - self.last_entries[3][0]).seconds <= 20
        else:
            return False

    def single_sandwich(self):
        """Check if we need to give 1 month membership registration"""
        try:
            m1, m2, m3 = [m for t,m in self.last_entries[:3]]
        except ValueError:
            return False
        if m1.id==m3.id and m1.id!=m2.id and m1.is_staff:
            return (datetime.now() - self.last_entries[2][0]).seconds <= 15
        else:
            return False

    def eat_sandwich(self, size):
        """Execute the posting of a payment transaction
        - size = 1 (1 mth) or 2 (6 mths)  for single or double sandwich
            +31 days for single
            +181 days for double
        """
        msg = "** Double Sandwich ** " if size == 2 else "* Single Sandwich * "
        timestamp1, member_to_upd = self.last_entries[1]
        timestamp0, staff_member = self.last_entries[0]
        membership = Member_Api.MEMBERSHIP[size - 1]  #  list starts at 0
        amount = membership[2]
        until_days = membership[3]
        new_validity = member_to_upd['validity'] + timedelta(days=until_days)
        msg += "{}CNY received from {} until {:%Y-%m-%d} (staff {})".format(amount, member_to_upd['username'], new_validity, staff_member['username'])
        # Add Transaction by API using the 'openid' as PATCH is only implemented on that table key
        url = "{}/member/openid/{}".format(self.base_api_url, member_to_upd["openid"])
        patch = {
            "op": "add",
            "data": {
                'paidTime': datetime.now().strftime('%Y%m%d%H%M'), # '201803121929',
                'payIndex': msg,
                'CNYAmount': amount,
                'payType': membership[0],
                'until_days': until_days
            }
        }
        try:
            response = requests.patch(url, json=patch)  # PATCH API call to add a transaction record
        except requests.ConnectionError as conn_err:
            return 98
        if response.status_code == 200:
            result = response.json()
            print(result)
            if int(result['errno']) == 1000:
                # Perform the confirmation flashing
                self.gpio.green1.flash("SET", on_duration=1, off_duration=1)
                self.gpio.green2.flash("SET", on_duration=1, off_duration=1)
                self.gpio.red.flash("SET", on_duration=1, off_duration=1)
                for i in range(size * 2):
                        sleep(1)
                # Log payment
                self.insert_log("PAY", 100 + size, msg)
                return 1
            else:
                self.insert_log("PAY", -100 - size, "Failed record payment: {} ({})".format(msg, result['errmsg']))
        else:
            self.insert_log("PAY", -100 - size, "Failed record payment: {} ({})".format(msg, response.status_code))
        return 99 

    def check_member(self):
        """State 3: a QR Code is found: check it against the member database"""
        if self.debug: print("Entering state", self.current_state, self.TASKS[self.current_state].__name__)
        self.gpio.green1.ON()
        self.gpio.green2.ON()
        self.gpio.red.OFF()
        self.member = Member_Api()
        if self.qr_codes:
            # try finding a member from the database based on the first QR code found on the image
            # print("QR code:", self.qr_codes, type(self.qr_codes[0]))
            # self.member = Member(qrcode=self.qr_codes[0])
            self.member.id = self.member.decode_qrcode(self.qr_codes[0])
            if self.member.id:
                if self.member.qrcode_is_valid:
                    url = "{}/member/{}".format(self.base_api_url, self.member.id)
                    try:
                        response = requests.get(url)
                    except requests.ConnectionError as conn_err:
                        print(conn_err)
                        return 98
                    if response.status_code == 200:
                        self.member.from_json(response.json())
                        if self.debug: print(self.member)
                    else:
                        self.insert_log("ERROR", -1399, "response: {} for {}".format(response.status_code, url))
                else:
                    self.insert_log("ERROR", -1001, "Invalid XCJ QR code: {}".format(self.member.clear_qrcode))
            else:
                self.insert_log("ERROR", -1000, "Non XCJ QR Code or No member found for: {}".format(self.qr_codes[0].decode("utf-8")))
        elif self.uid:
            # try by RFID UID
            url = "{}/member/rfid/{}".format(self.base_api_url, self.uid)
            try:
                response = requests.get(url)
            except requests.ConnectionError as conn_err:
                print(conn_err)
                return 98
            if response.status_code == 200:
                self.member.from_json(response.json())
                if self.debug: print(self.member)
            else:
                self.insert_log("ERROR", -1398, "response: {} for {}".format(response.status_code, url))
            if self.member.id is None:
                self.insert_log("ERROR", -1010, "Non XCJ registered RFID card: {}".format(self.uid))
        # if we have a member, let's check its status to open the door
        if self.member.id:
            self.last_entries.add( (datetime.now(), self.member) )  # stack for sandwich checking
            if self.double_sandwich():
                return self.eat_sandwich(size=2)
            elif self.single_sandwich():
                return self.eat_sandwich(size=1)
            elif self.uid or self.member.qrcode_is_valid:
                if self.member['status'].upper() in ("OK", "ACTIVE", "ENROLLED"):
                    msg = "Welcome {} - {}".format(self.member['username'],
                                    "RFID {}".format(self.uid) if self.uid \
                                    else "QR v{} {}".format(self.member.qrcode_version, ":".join(self.member.clear_qrcode[2:])))
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


    def open_the_door_API(self):
        """State 4: Proceed to open the door by calling the API --> open main door ; RPI does not control a door directly
            Calls the Master Raspi to open the door by API"""
        if self.debug: print("Entering state", self.current_state, self.TASKS[self.current_state].__name__)
        url = "{}/open/seconds".format(self.base_api_url)
        payload = { 'seconds': 3 }
        try:
            response = requests.post(url, json=payload)
        except requests.ConnectionError as conn_err:
            return 98
        if response.status_code == 200:
            result = response.json()
            if result["errno"] == 1000: # no error
                self.happy_flashing(3)
                return 7 if self.db.access["wait_to_close"] else 1
            else:
                self.insert_log("ERROR", -1002, "Cannot open door by API: {} {}".format(result["errno"], result["errmsg"]))
        else:
            self.insert_log("ERROR", -1003, "Cannot open door by API: response.status_code = {}".format(response.status_code))
        return 6


    def open_the_door_RELAY(self):
        """State 4: Proceed to open the door
            Open the door using the electric relay
        """
        if self.debug: print("Entering state", self.current_state, self.TASKS[self.current_state].__name__)
        self.gpio.relay.ON()
        self.happy_flashing(3)
        return 7 if self.db.access["wait_to_close"] else 1

    def open_the_door_BLE(self):
        """State 4: Proceed to open the door
            Open the door using Bluetooth - all BLE parameters are defaulted for the TOKYDOOR BLE @ XCJ
        """
        if self.debug: print("Entering state", self.current_state, self.TASKS[self.current_state].__name__)
        tokydoor = TokyDoor(database=self.db)
        try:
            tokydoor.open()
        except ValueError as err:
            self.insert_log("ERROR", -1001, "Cannot connect to TOKYDOOR: {}".format(err))
            return 99 # cannot reach the BLE!!! Panic Mode!! 
        self.happy_flashing(3)
        return 7 if self.db.access["wait_to_close"] else 1

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
        return 7 if self.db.access["wait_to_close"] else 1

    def wait_to_close_the_door(self):
        """State 7: Wait for the door to be closed
            Verifies that the door has been closed physically before returning to State 1 where the relay set OFF"""
        if self.debug: print("Entering state", self.current_state, self.TASKS[self.current_state].__name__)
        while self.gpio.door_check.is_open:
            self.happy_flashing(1)
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
                from_=self.db.mailbox["username"],
                to_=(self.member["email"],),
                message_HTML = """
                    <P>Your status in the XCJ database is set to: {}</P>
                    <p>You membership expiration date is {}</p>
                    <p></p>
                    """.format(self.member["status"], self.member.validity.strftime('%Y-%m-%d')),
                images=[r"images/emoji-not-happy.jpg"],
                server=self.db.mailbox["server"], port=self.db.mailbox["port"],
                login=self.db.mailbox["username"], passwd=self.db.mailbox["password"]
            )
            sleep(1.5)  # let's say it takes 1.5 seconds to send the email already
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

    def panic_no_db(self):
        """State 98: no database acces, flash the lights for 3 seconds"""
        if self.debug: print("Entering state", self.current_state, self.TASKS[self.current_state].__name__)
        self.gpio.green1.flash("SET", on_duration=0.3, off_duration=0.3)
        self.gpio.green2.flash("SET", on_duration=0.3, off_duration=0.3)
        self.gpio.red.ON()
        sleep(3)
        return 1

    def panic_mode(self):
        """State 99: major error, flash the lights for 3 seconds"""
        if self.debug: print("Entering state", self.current_state, self.TASKS[self.current_state].__name__)
        self.gpio.green1.flash("SET", on_duration=0.3, off_duration=0.3)
        self.gpio.green2.flash("SET", on_duration=0.3, off_duration=0.3)
        self.gpio.red.flash("SET", on_duration=0.3, off_duration=0.3)
        sleep(3)
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--bottle", dest="bottle_ip", help="Optional: Raspberry Pi IP address to allow remote connections", required=False,  default=None)
    parser.add_argument("-p", "--port", dest="port", help="Optional: port for HTTP (8080: test / 80: PROD)", required=False,  default=8080, type=int)
    parser.add_argument('-v', '--version', action='version', version=__version__)
    parser.add_argument('-d', '--debug', dest='debug', help='debug mode - kep photos', action='store_true', default=False)
    # parser.add_argument('config_file', nargs='?', default='')
    args, unk = parser.parse_known_args()
    ctrl = Controller(bottle_ip=args.bottle_ip, port=args.port, debug=args.debug)
    ctrl.run()
