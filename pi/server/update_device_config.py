# ---------------------------------------------------
# update_device_config.py
# 
# Code to update the device config json values
# ----------------------------------------------------

import os 
import sys
import json 
import uuid

CURR_PATH = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(CURR_PATH, "device_config.json")

MY_ADDRESS = "" 
#"00:00:00:00:00:00"
MY_DEV_NAME = "" 
#"Device"


def handle_config():
    try:
        if not os.geteuid() == 0:
            sys.exit("Only root can run this")
        if len(MY_ADDRESS) == 0 or len(MY_DEV_NAME) == 0:
            sys.exit("Run update scripts first")
        UUID = str(uuid.uuid4())
        config_data = {
            "MY_ADDRESS": MY_ADDRESS,
            "MY_DEV_NAME": MY_DEV_NAME,
            "UUID": UUID 
        }
        config_json_data = json.dumps(config_data, indent=4)

    except ... as e:
        sys.exit(e)
    print("Cleaning up config json file")
    if os.path.exists(CONFIG_PATH):
        os.remove(CONFIG_PATH)
    
    print("Generating new config file")
    with open(CONFIG_PATH, "w") as cf:
        cf.write(config_json_data)

if __name__ == "__main__":
    handle_config()
    