# TO USE - WORK PERFECTLY!
#  sudo pip3 install gatt
#  sudo apt-get install python3-dbus
#
# https://github.com/getsenic/gatt-python

# all AT commands for Bluetooth 4.0:
# http://fab.cba.mit.edu/classes/863.15/doc/tutorials/programming/bluetooth/bluetooth40_en.pdf
# try: AT+PIO....    no \n at the end! The + sign is part of the command
import gatt

manager = gatt.DeviceManager(adapter_name='hci0')

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
        print("Door is open!")
        self.manager.stop()

    def characteristic_write_value_failed(self, characteristic, error):
        print("Failed to open the door:", error)
        self.manager.stop()

device = AnyDevice(mac_address='50:8C:B1:69:A2:F1', manager=manager)
device.connect()
device.services_resolved()
door_characteristic="0000ffe1-0000-1000-8000-00805f9b34fb"
device.write_characteristic(door_characteristic, "ONCE")
try:
    manager.run()
finally:
    device.disconnect()



