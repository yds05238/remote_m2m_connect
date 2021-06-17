# remote_m2m_connect
Disjointly connect 2 MacBook to each other using a Linux machine supporting bluetooth (Raspberry Pi) as relay.

## Components

### Work MacBook Pro

- Connect to simulated bluetooth devices from Raspberry Pi

### Raspberry Pi

- Bluetooth Server App
- Input Clients/Handler (Mouse/keyboard/mic/yubikey)
- Webcam = usb camera attached to the raspberry pi aimed at the laptop screen

### Personal MacBook Pro

- GUI of the Work Laptop screen

  - Receives webcam data --> display on GUI

- Device Clients/Handler (Mouse,keyboard,webcam,mic,yubikey)

  - Sense inputs data from physical/real devices on the laptop --> transmit data to Raspberry Pi



## Final Configurations

- dockerize the program
- reset the raspberry pi to headless version 
- add ssh from pi to personal laptop
- allow for program restart (in case of error/failure)
