#!/usr/bin/env python3
"""
Open the TOKYDOOR by sending a command on Bluetooth

#  sudo pip3 install gatt
#  sudo apt-get install python3-dbus
#
# https://github.com/getsenic/gatt-python

# all AT commands for Bluetooth 4.0:
# http://fab.cba.mit.edu/classes/863.15/doc/tutorials/programming/bluetooth/bluetooth40_en.pdf
# try: AT+PIO....    no \n at the end! The + sign is part of the command
"""
__author__ = "Eric Gibert"
__version__ = "1.0.20170119"
__email__ =  "ericgibert@yahoo.fr"
__license__ = "MIT"
from dbus.exceptions import DBusException
import gatt
import argparse

TOKYDOOR = '50:8C:B1:69:A2:F1'
TOKYUUID = "0000ffe1-0000-1000-8000-00805f9b34fb"
TOKYCOMMAND = "ONCE"

class AnyDevice(gatt.Device):
    def connect_succeeded(self):
        super().connect_succeeded()
        print("[%s] Connected" % (self.mac_address))

    def connect_failed(self, error):
        super().connect_failed(error)
        print("[%s] Connection failed: %s" % (self.mac_address, str(error)))

    def disconnect_succeeded(self):
        super().disconnect_succeeded()
        print("[%s] Disconnected" % (self.mac_address))

    def services_resolved(self):
        super().services_resolved()
        print("[%s] Resolved services" % (self.mac_address))
        for service in self.services:
            print("[%s]  Service [%s]" % (self.mac_address, service.uuid))
            for characteristic in service.characteristics:
                print("[%s]    Characteristic [%s]" % (self.mac_address, characteristic.uuid))

    def write_characteristic(self, uuid, value):
        for service in self.services:
            for characteristic in service.characteristics:
                if characteristic.uuid==uuid:
                    characteristic.write_value(value.encode("utf-8"))
                    return
        print("Unknow characteristic {}. Try services_resolved".format(uuid))

    def characteristic_write_value_succeeded(self, characteristic):
        """Callback after the 'write_characteristic' call uis completed on success"""
        print("Door is open!")
        self.manager.stop()

    def characteristic_write_value_failed(self, characteristic, error):
        """Callback after the 'write_characteristic' call uis completed on failure"""
        print("Failed to open the door:", error)
        self.manager.stop()

class TokyDoor():
    """Define the parameters to communicate with the TOKYDOOR BLE"""
    def __init__(self, mac_address=TOKYDOOR, adapter_name='hci0', command="ONCE", uuid=""):
        """
        Prepare the access to the door's BLE
        :param mac_address: the BLE mac address
        :param adapter_name: the Raspberry Pi's Bluettoth device name (check with 'hciconfig')
        :param command: the coomand to send to the BLE on the characteristic uuid
        :param uuid: characteristic to use to send the commad. Must be 'writable'.
        """
        self.mac_address = mac_address
        self.door_characteristic = uuid or TOKYUUID
        self.command = command
        self.adapter_name = adapter_name
        self.manager = gatt.DeviceManager(adapter_name=self.adapter_name)

    def open(self):
        device = AnyDevice(mac_address=self.mac_address, manager=self.manager)
        device.connect()
        try:
            if not device.is_connected():
                raise ValueError("Connection to {} failed. Try using 'hciconfig' and 'hcitool'".format(self.mac_address))
        except DBusException:
            raise ValueError("Connection to {} by '{}' failed. Check using 'hciconfig' and 'hcitool'.".format(self.mac_address, self.adapter_name))
        #device.services_resolved()
        device.write_characteristic(self.door_characteristic, self.command)
        try:
            self.manager.run()
        finally:
            device.disconnect()
        # this run() loop will stop by the callback after the writing on uuid has been completed


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Utility to send a commad to a BLE device')
    parser.add_argument("-m", "--mac_address", dest="mac_address",
                        help="Device Macc Address (default: {})".format(TOKYDOOR), default=TOKYDOOR)
    parser.add_argument("-a", "--adapter", dest="adapter",
                        help="Bluetooth local adapter name to use (default: hci0). Use 'hciconfig'", default='hci0')
    parser.add_argument("-c", "--command", dest="command",
                        help="Command to send to the BLE device (default: {}".format(TOKYCOMMAND), default=TOKYCOMMAND)
    parser.add_argument("-u", "--uuid", dest="uuid", default=TOKYUUID,
                        help="BLE characteristic to use to write the command to (default: {}".format(TOKYUUID))
    args, unk = parser.parse_known_args()
    if unk:
        # consider to be a command - overwrite the default command
        args.command = unk

    tokydoor = TokyDoor(mac_address=args.mac_address, adapter_name=args.adapter,
                        command=args.command, uuid=args.uuid)
    try:
        tokydoor.open()
    except ValueError as err:
        print(err)

