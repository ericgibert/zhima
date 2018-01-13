#!/usr/bin/env python3
""" Manage the I/O on the Raspi GPIO or simulate them
"""
__author__ = "Eric Gibert"
__version__ = "1.0.20170113"
__email__ =  "ericgibert@yahoo.fr"
__license__ = "MIT"
import threading
try:
    import pigpio
    _simulation = False
except ImportError:
    _simulation = True
    class pigpio():
        INPUT=1
        OUTPUT=0
        PUD_DOWN=0
        RISING_EDGE=1
        def __init__(self):
            """create a representation in memory of the buffers"""
            self.buffer = {} # key: pin number --> value: [mode, pin value]

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

class Led(object):
    """
    Manage a LED for flashing
    """
    def __init__(self, pig, pin):
        self.pig, self.pin = pig, pin
        self.pig.set_pin_as_output(pin)
        self.state = self.OFF()

    def ON(self):
        self.state = self.pig.write(self.pin, 1)
        return self.state

    def OFF(self):
        self.state = self.pig.write(self.pin, 0)
        return self.state

    def flash(self, action, on_duration=0.5, off_duration=0.5):
        """
        Set/Stop the flashing effect of a LED
        :param action: SET/STOP
        :param on_duration: float for sleep
        :param off_duration: float for sleep
        :return: current state
        """
        if action=="SET":
            self.on_duration, self.off_duration = on_duration, off_duration
            state = self.ON()
            self._timer = threading.Timer(off_duration, self._ontimer)
            self._timer.start()
            return state
        elif action=="STOP":
            self._timer.cancel()
            return self.state
        elif action=="ON":
            self._timer.cancel()
            return self.ON()
        elif action=="OFF":
            self._timer.cancel()
            return self.OFF()
        else:
            print("Unknown action:", action)

    def _ontimer(self):
        if self.state==1: # ON
            self.OFF()
            self._timer = threading.Timer(self.off_duration, self._ontimer)
        else:
            self.ON()
            self._timer = threading.Timer(self.on_duration, self._ontimer)
        self._timer.start()


class Rpi_Gpio(object):
    def __init__(self, pigpio_host="", pigpio_port=8888):
        """
        Either connects to the PGPIO daemon or simulte it
        Need to execute 'sudo pigpiod' to get that daemon running if it is not automatically started at boot time
        """
        self.pig = pigpio.pi(pigpio_host, pigpio_port) if not _simulation else pigpio()
        self.proximity_pin = self.set_pin_as_input(17)  # PROXIMITY_PIN
        self.green1 = Led(self, 20)                     # GREEN LED 1 on GPIO20
        self.green2 = Led(self, 21)                     # GREEN LED 2 on GPIO21
        self.red = Led(self, 16)                        # RED LED on GPIO16


    def check_proximity(self):
        if _simulation:
            self.write(self.proximity_pin, 1)
        return self.read(self.proximity_pin)

    def read(self, pin):
        if _simulation:
            print(self.pig.buffer)
        return self.pig.read(pin)

    def write(self, pin, value):
        self.pig.write(pin, value)
        if _simulation:
            print(self.pig.buffer)
        return self.pig.read(pin)

    def set_pin_as_input(self, pin):
        self.pig.set_mode(pin, pigpio.INPUT)
        return pin

    def set_pin_as_output(self, pin):
        self.pig.set_mode(pin, pigpio.OUTPUT)
        return pin


if __name__ == "__main__":
    my_pig = Rpi_Gpio()
    my_pig.green1.ON()
    my_pig.red.ON()
    if _simulation:
        print(my_pig.pig.buffer)

    # flash testing
    from time import sleep
    my_pig.green2.flash("SET", on_duration=0.2, off_duration=1)
    try:
        while True:
            print("Proximity:", my_pig.check_proximity())
            sleep(1)
    finally:
        my_pig.green2.flash("STOP")