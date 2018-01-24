#
# https://github.com/peplin/pygatt
# check out the gattttool as well:
#  Interaction session:  gatttool -b <BLE ADDRESS> -I
# examples: https://github.com/pcborenstein/bluezDoc/wiki/hcitool-and-gatttool-example

# https://stackoverflow.com/questions/15657007/bluetooth-low-energy-listening-for-notifications-indications-in-linux
# hcitool lescan
# hcitool lecc
# gatttool -b <Mac Address> --primary
# gatttool -b <MAC Address> --characteristics
# gatttool -b <MAC Address> --char-read
# gatttool -b <MAC Address> --char-desc
# gatttool -b <MAC Address> --interactive
# gatttool -b <MAC Address> --char-write-req --handle=0x0031 --value=0100 --listen
#!/usr/bin/python
# -*- mode: python; coding: utf-8 -*-

# Copyright (C) 2014, Oscar Acena <oscaracena@gmail.com>
# This software is under the terms of GPLv3 or later.

from __future__ import print_function

import sys
from bluetooth.ble import GATTRequester


class Reader(object):
    def __init__(self, address):
        self.requester = GATTRequester(address, False)
        self.connect()
        self.request_data()

    def connect(self):
        print("Connecting...", end=' ')
        sys.stdout.flush()

        self.requester.connect(True)
        print("OK!")

    def request_data(self):
        data = self.requester.read_by_uuid(
                "00002a00-0000-1000-8000-00805f9b34fb")[0]
        try:
            print("Device name: " + data.decode("utf-8"))
        except AttributeError:
            print("Device name: " + data)


if __name__ == '__main__':
    # if len(sys.argv) < 2:
    #     print("Usage: {} <addr>".format(sys.argv[0]))
    #     sys.exit(1)
    #
    # Reader(sys.argv[1])
    Reader("50:8C:B1:69:A2:F1")
    print("Done.")