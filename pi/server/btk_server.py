# ---------------------------------------------------
# btk_server.py
# 
# Code to set up the Bluetooth Hub Device Emulator 
# DBUS Service Serve on Raspberry Pi
# ----------------------------------------------------

import logging
import os
from pi.server.update_device_config import MY_ADDRESS
import socket
import sys
import json 

from bluetooth import *
import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

# from __future__ import absolute_import, print_function
# import os
# import sys
# import uuid
# import dbus
# import dbus.service
# import dbus.mainloop.glib
# import time
# import socket
# from gi.repository import GLib
# from dbus.mainloop.glib import DBusGMainLoop
# import logging
# from logging import debug, info, warning, error
# import bluetooth
# from bluetooth import *

logging.basicConfig(level=logging.DEBUG)

CURR_PATH = os.path.dirname(os.path.abspath(__file__))


class BTKbDevice():
    # Bluetooth Hub Device
    MY_ADDRESS = "00:00:00:00:00:00"
    MY_DEV_NAME = "ConnectHub"
    UUID = ""

    P_CTRL = 17 # service port
    P_INTR = 19 # interrupt port
    SDP_RECORD_PATH = os.path.join(CURR_PATH, "sdp_record.xml")

    def __init__(self, maddr:str, dvname: str, uid: str) -> None:
        """
        Initialize a bluetooth hub device.
        
        Args:
            maddr: value for device's MY_ADDRESS
            dvname: value for device's MY_DEV_NAME 
            uid: value for device's UUID
        """
        print("Updating device config...")
        self.MY_ADDRESS, self.MY_DEV_NAME, self.UUID = maddr, dvname, uid
 
        print("Setting up Bluetooth device...")
        self.init_bt_device()
        self.init_bluez_profile()

    def init_bt_device(self, dvname: str) -> None:
        """
        Set up a bluetooth hardware device with the specified name.

        Args:
            dvname: value for device's name 
        """
        print(f"Configuring device name {dvname}...")
        os.system("hciconfig hci0 up") # set device class to keyboard 
        os.system(f"hciconfig hci0 name {dvname}") # set device name 
        os.system("hciconfig hci0 piscan") # pi bluetooth set to discoverable 

    def init_bluez_profile(self, uid: str) -> None:
        """
        Set up bluez profile to advertise device capabilities from record.

        Args:
            uid: value for device's UUID
        """
        print("Configuring Bluez Profile...")
        profile_options = {
            "AutoConnect": True,
            "ServiceRecord": self.read_sdp_service_record()
        }
        # Retrieve proxy for bluez prof. interface
        bus = dbus.SystemBus()
        manager = dbus.Interface(bus.get_object("org.bluez", "/org/bluez"), 
                                "org.bluez.ProfileManager1")
        manager.RegisterProfile("/org/bluez/hci0", uid, profile_options)
        
        print("Profile registered...")
        os.system("hciconfig hci0 class 0x0025C0")

    def read_sdp_service_record(self):
        """ Retrieve sdp record from file """
        print("Reading service record...")
        try:
            with open(self.SDP_RECORD_PATH, "r") as f:
                return f.read()
        except:
            sys.exit("Error reading from sdp record file!")

    def listen(self): 
        """ Listen for incoming client connections """
        print("\033[0;33m7. Waiting for connections\033[0m")
        self.scontrol = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_SEQPACKET, socket.BTPROTO_L2CAP) 
        self.sinterrupt = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_SEQPACKET, socket.BTPROTO_L2CAP) 
        self.scontrol.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sinterrupt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Bind sockets to a port
        self.scontrol.bind((socket.BDADDR_ANY, self.P_CTRL))
        self.sinterrupt.bind((socket.BDADDR_ANY, self.P_INTR))

        # Listen on sockets
        self.scontrol.listen(5)
        self.sinterrupt.listen(5)

        self.ccontrol, cinfo = self.scontrol.accept()
        print("\033[0;32mGot a connection on the control channel from %s \033[0m" % cinfo[0])
        self.cinterrupt, cinfo = self.sinterrupt.accept()
        print("\033[0;32mGot a connection on the interrupt channel from %s \033[0m" % cinfo[0])

    def send_string(self, message: str):
        """
        Send a string to the bluetooth host machine.

        Args:
            message: string to be sent out
        """
        try:
            self.cinterrupt.send(bytes(message))
        except OSError as e:
            logging.error(e)
        except ... as e:
            logging.error(e)
    
class BTKbService(dbus.service.Object):

    def __init__(self, maddr:str, dvname: str, uid: str) -> None:
        """
        Initialize a new bluetooth hub service.      
        
        Args:
            maddr: value for device's MY_ADDRESS
            dvname: value for device's MY_DEV_NAME 
            uid: value for device's UUID
        """
        print("Setting up service...")
        
        # Set up dbus service and device 
        bus_name = dbus.service.BusName("org.connectpi.btkbservice", bus = dbus.SystemBus())
        dbus.service.Object.__init__(self, bus_name, "/org/connectpi/btkbservice")
        
        self.device = BTKbDevice(maddr, dvname, uid)
        self.device.listen()

    @dbus.service.method('org.connectpi.btkbservice', in_signature='yay')
    def send_keys(self, modifier_byte, keys):
        # Send keyboard key press info
        print("Get send_keys request through dbus")
        print("key msg: ", keys)

        state = [0xA1, 1, 0, 0, 0, 0, 0, 0, 0, 0]
        state[2] = int(modifier_byte)
        count = 4
        for key_code in keys:
            if (count < 10):
                state[count] = int(key_code)
            count+=1
        self.device.send_string(state)

    @dbus.service.method('org.connectpi.btkbservice', in_signature='yay')
    def send_mouse(self, modifier_byte, keys):
        # Send mouse input info
        state = [0xA1, 2, 0, 0, 0, 0]
        count = 2
        for key_code in keys:
            if (count < 6):
                state[count] = int(key_code)
            count+=1
        self.device.send_string(state)


# Helpers
def handle_config():
    # check for config file
    cfilepath = os.path.join(CURR_PATH, 'device_config.json')
    if not os.path.isfile(cfilepath):
        sys.exit("First run update_device_config.py")

    with open(cfilepath) as f:
        data = json.load(f)
    macaddr = data.get('MY_ADDRESS', "")
    devname = data.get('MY_DEV_NAME', "")
    uid = data.get('UUID', "")
    if len(macaddr) == 0:
        sys.exit("Missing MY_ADDRESS valu in device_config.json")
    elif len(devname) == 0:
        sys.exit("Missing MY_DEV_NAME valu in device_config.json")
    elif len(uid) == 0:
        sys.exit("Missing UUID valu in device_config.json")
    
    macaddrlist = macaddr.split(':')
    if len(macaddr) != 17 or macaddr.count(':') != 5:
        sys.exit("Invalid MY_ADDRESS in device_config.json")
    for ad in macaddrlist:
        if len(ad) != 2:
            sys.exit("Invalid MY_ADDRESS in device_config.json")

    # TODO: restrict device name and UUID values
    return str(macaddr), str(devname), str(uid)


if __name__ == "__main__":
    try:
        if not os.geteuid() == 0:
            sys.exit("Only root can run this")
        
        macaddr, devname, uid = handle_config()
        DBusGMainLoop(set_as_default=True)
        myservice = BTKbService(macaddr, devname, uid)
        loop = GLib.MainLoop()
        loop.run()
    except KeyboardInterrupt:
        sys.exit()



    





