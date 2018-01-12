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