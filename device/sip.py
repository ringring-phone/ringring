import time
import json
import sys
from global_state import GlobalState, State

CONFIG_PATH = "../config.json"
PHONE_NUMBER = "phoneNumber"
PASSWORD = "password"
SIP_IP = "sipIP"

def sip():
    config = {
        PHONE_NUMBER: "",
        PASSWORD: "",
        SIP_IP: ""
    }

    while True:
        try:
            with open(CONFIG_PATH, "r") as file:
                data = json.load(file)
            print("Config file loaded successfully!")
            config[PHONE_NUMBER] = data[PHONE_NUMBER]
            config[PASSWORD] = data[PASSWORD]
            config[SIP_IP] = data[SIP_IP]
            break
        except FileNotFoundError:
            print(f"File {CONFIG_PATH} not found. Retrying in 5 seconds...")
        except json.JSONDecodeError:
            print(f"File {CONFIG_PATH} is not a valid JSON file. Retrying in 5 seconds...")
        except Exception as e:
            print(f"An unexpected error occurred: {e}. Retrying in 5 seconds...")

        time.sleep(5)

    while True:
        print("App sleeping")
        time.sleep(1)

if __name__ == "__main__":
    try:
        sip()
    except KeyboardInterrupt:
        print("Exiting...")
        sys.exit(0)