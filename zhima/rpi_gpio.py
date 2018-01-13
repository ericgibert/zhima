#!/usr/bin/env python3
""" Manage the I/O on the Raspi GPIO or simulate them
"""
__author__ = "Eric Gibert"
__version__ = "1.20170113"
__email__ =  "ericgibert@yahoo.fr"
__license__ = "MIT"
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

    def ON(self):
        self.pig.write(self.pin, 1)

    def OFF(self):
        self.pig.write(self.pin, 0)


class Rpi_Gpio(object):
    def __init__(self, pigpio_host="", pigpio_port=8888):
        """
        Either connects to the PGPIO daemon or simulte it
        Need to execute 'sudo pigpiod' to get that daemon running if it is not automatically started at boot time
        """
        self.pig = pigpio.pi(pigpio_host, pigpio_port) if not _simulation else pigpio()
        self.proximity_pin = self.set_pin_as_input(17)   #  PROXIMITY_PIN
        self.green1 = Led(self, 18)   #  GREEN LED 1
        self.green2 = Led(self, 19)  # GREEN LED 2
        self.red = Led(self, 20)  # RED LED


    def detect_proximity(self):
        if _simulation:
            self.write(self.proximity_pin, 1)
        return self.read(self.proximity_pin)

    def read(self, pin):
        return self.pig.read(pin)

    def write(self, pin, value):
        self.pig.write(pin, value)
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
    print(my_pig.pig.buffer)