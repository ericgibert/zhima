#!/usr/bin/env python3
""" Manage the I/O on the Raspi GPIO or simulate them
"""
__author__ = "Eric Gibert"
__version__ = "1.0.20170113"
__email__ =  "ericgibert@yahoo.fr"
__license__ = "MIT"
import threading
import binascii
try:
    import pigpio           # reference at  http://abyz.me.uk/rpi/pigpio/python.html
    _simulation = False
except ImportError:
    _simulation = True
    class pigpio():
        INPUT=1
        OUTPUT=0
        PUD_DOWN=0
        PUD_UP=1
        RISING_EDGE=1
        def __init__(self):
            """create a representation in memory of the buffers"""
            self.buffer = {} # key: pin number --> value: [mode, pin value]
            print("pigpio simulation")

        def set_mode(self,pin, mode):
            """
            add an entry in the memory buffer
            :param pin: integer for pin number
            :param mode: pigpio.INPUT/OUTPUT
            :return:
            """
            self.buffer[pin] = [mode, 0]

        def read(self, pin):
            return self.buffer[pin][1]

        def write(self, pin, value):
            self.buffer[pin][1] = value
            return value

        def set_pull_up_down(self, pin, up_or_down):
            pass

        def stop(self):
            pass

from zPN532 import PN532

class Led(object):
    """
    Manage a LED for flashing
    """
    def __init__(self, rpi, pin):
        self.rpi, self.pin = rpi, pin
        self.rpi.set_pin_as_output(pin)
        self._timer = None
        self.state = self.OFF()

    def set(self, value):
        if self._timer: self.cancel_timer()
        self.state = self.rpi.write(self.pin, value)
        return self.state

    def ON(self):
        if self._timer: self.cancel_timer()
        self.state = self.rpi.write(self.pin, 1)
        return self.state

    def OFF(self):
        if self._timer: self.cancel_timer()
        self.state = self.rpi.write(self.pin, 0)
        return self.state

    def flash(self, action, on_duration=0.5, off_duration=0):
        """
        Set/Stop the flashing effect of a LED
        :param action: SET/STOP
        :param on_duration: float for sleep
        :param off_duration: float for sleep ; if 'off_duration' is 0 then do not submit the timer again i.e. one time ON only
        :return: current state
        """
        if action=="SET":
            self.on_duration, self.off_duration = on_duration, off_duration
            state = self.ON()
            self._timer = threading.Timer(on_duration, self._ontimer)
            self._timer.start()
            return state
        elif action=="STOP":
            if self._timer: self.cancel_timer()
            return self.state
        elif action=="ON":
            return self.ON()
        elif action=="OFF":
            return self.OFF()
        else:
            print("Unknown action:", action)

    def _ontimer(self):
        if self.state==1: # from ON to OFF  --- if off_duration > 0
            self.OFF()
            if self.off_duration > 0:
                self._timer = threading.Timer(self.off_duration, self._ontimer)
                self._timer.start()
        else:
            self.ON()
            self._timer = threading.Timer(self.on_duration, self._ontimer)
            self._timer.start()

    def cancel_timer(self):
        if self._timer:
            self._timer.cancel()
            self._timer = None

class E18_D80nk(object):
    """
    Class to manage an IR distance switch e18-d80nk
    https://www.14core.com/wiring-the-e18-d80nk-infrared-distance-ranging-sensor/

    Wiring:
    Type 1      Type 2      Function
    red         brown       Vcc  (+5V)
    black       bleu        Gnd
    Yellow      black       Signal   need to insert a 4.7kO to 10kO resitor before the pin
    """
    def __init__(self, rpi, pin):
        self.rpi, self.pin = rpi, pin
        rpi.pig.set_mode(pin, pigpio.INPUT)
        rpi.pig.set_pull_up_down(pin, pigpio.PUD_UP)

    @property
    def state(self):
        return int(not self.rpi.read(self.pin))

    def reset(self):
        self.rpi.write(self.pin, 1)


class Dfrobot_Pir_v1_0(object):
    """
    Class to manage an IR distance switch from DFROBOT PIR Sensor V1.0
    https://www.dfrobot.com/wiki/index.php/PIR_Motion_Sensor_V1.0_SKU:SEN0171
    """
    def __init__(self, rpi, pin):
        self.rpi, self.pin = rpi, pin
        rpi.pig.set_mode(pin, pigpio.INPUT)
        # rpi.pig.set_pull_up_down(pin, pigpio.PUD_UP)

    @property
    def state(self):
        return int(not self.rpi.read(self.pin))


class Rpi_Gpio(object):
    def __init__(self, pigpio_host="", pigpio_port=8888):
        """
        Either connects to the PGPIO daemon or simulte it
        Need to execute 'sudo pigpiod' to get that daemon running if it is not automatically started at boot time
        """
        self.pig = pigpio.pi(pigpio_host, pigpio_port) if not _simulation else pigpio()

                                                        # nothing on pin 2 --> leave it empty
                                                        # 5V            on pin 4
                                                        # GND           on pin 6
        self.green1 = Led(self, 14)                     # GREEN LED 1   on pin 8
        self.green2 = Led(self, 15)                     # GREEN LED 2   on pin 10
        self.red = Led(self, 18)                        # RED LED       on pin 12
                                                        # GND (again)   on pin 14
        self.proximity = E18_D80nk(self, 23)            # PROXIMITY     on pin 16
        self.relay = Led(self, 24)                      # RELAY         on pin 18

        CS   = 22                                       #  pin 15
                                                        #  3.3V on pin 17
        MOSI = 10                                       #  pin 19
        MISO = 9                                        #  pin 21
        SCLK = 11                                       #  pin 23
                                                        #  GND on pin 25
        self.pn532 = PN532(cs=CS, sclk=SCLK, mosi=MOSI, miso=MISO, gpio=self.pig)
        # Call begin to initialize communication with the PN532.  Must be done before
        # any other calls to the PN532!
        self.pn532.begin()
        # Configure PN532 to communicate with MiFare cards.
        self.pn532.SAM_configuration()

    def check_proximity(self):
        return 1 if _simulation else self.proximity.state

    def read(self, pin):
        if _simulation:
            # print(self.pig.buffer)
            pass
        return self.pig.read(pin)

    def write(self, pin, value):
        self.pig.write(pin, value)
        if _simulation:
            # print(self.pig.buffer)
            pass
        return self.pig.read(pin)

    def set_pin_as_input(self, pin):
        self.pig.set_mode(pin, pigpio.INPUT)
        return pin

    def set_pin_as_output(self, pin):
        self.pig.set_mode(pin, pigpio.OUTPUT)
        return pin


if __name__ == "__main__":
    from time import sleep, time
    my_pig = Rpi_Gpio()
    my_pig.green1.ON()
    my_pig.red.ON()
    my_pig.green2.flash("SET", on_duration=0.5, off_duration=0.5)

    # Get the firmware version from the chip and print(it out.)
    ic, ver, rev, support = my_pig.pn532.get_firmware_version()
    print('Found PN532 with firmware version: {0}.{1}'.format(ver, rev))

    def three_seconds():
        """pause for 3 seconds while checking for RFID card"""
        start = time()
        while time() - start <= 3:
            # Check if a card is available to read.
            uid = my_pig.pn532.read_passive_target()
            # Try again if no card is available.
            if uid:
                print('Found card with UID: 0x{0}'.format(binascii.hexlify(uid)))
            sleep(0.2)
    try:
        while True:
            print("ON")
            my_pig.relay.ON()
            three_seconds()
            print("OFF")
            my_pig.relay.OFF()
            three_seconds()
    #        print("Proximity:", my_pig.check_proximity())
    #        sleep(1)
    finally:
        my_pig.red.OFF()
        my_pig.green1.OFF()
        my_pig.green2.OFF()
        my_pig.relay.OFF()
