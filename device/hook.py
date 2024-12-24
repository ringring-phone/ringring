import RPi.GPIO as GPIO
import time
import sys
import logging
from global_state import GlobalState, State

PIN = 33

def hook():
    globals = GlobalState()

    GPIO.setup(PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    while True:
        current_state = GPIO.input(PIN)
        if current_state == GPIO.HIGH and globals.get(State.ON_THE_HOOK):
            logging.debug("Hook is Disconnected!")
            globals.set(State.ON_THE_HOOK, False)
        elif current_state == GPIO.LOW and not globals.get(State.ON_THE_HOOK):
            logging.debug("Hook is Connected!")
            globals.set(State.ON_THE_HOOK, True)

        time.sleep(0.2)

if __name__ == '__main__':
    try:
        hook()
    except KeyboardInterrupt:
        logging.warning("Exiting program.")
    except Exception as e:
        logging.error(e)
    finally:
        sys.exit(0)