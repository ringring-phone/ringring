import RPi.GPIO as GPIO
import time
import sys
from multiprocessing import Process
import logging
from global_state import GlobalState, State

# Pin definitions
RING1 = 29
RING2 = 31

def ringing():
    while True:
        logging.debug("Ringing...")
        for _ in range(20):
            GPIO.output(RING1, GPIO.HIGH)
            GPIO.output(RING2, GPIO.LOW)
            time.sleep(0.05)
            GPIO.output(RING1, GPIO.LOW)
            GPIO.output(RING2, GPIO.HIGH)
            time.sleep(0.05)

        GPIO.output(RING2, GPIO.LOW)
        GPIO.output(RING1, GPIO.LOW)
        logging.debug("Pause ringing...")
        time.sleep(1.5)

def ringer():
    globals = GlobalState()
    process = None

    # GPIO setup
    GPIO.setup(RING1, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(RING2, GPIO.OUT, initial=GPIO.LOW)
    
    while True:
        if globals.get(State.RINGING) and process == None:
            process = Process(target=ringing)
            process.start()
        elif not globals.get(State.RINGING) and process != None:
            process.terminate()
            process = None

            GPIO.output(RING2, GPIO.LOW)
            GPIO.output(RING1, GPIO.LOW)

        time.sleep(0.5)

if __name__ == '__main__':
    try:
        ringer()
    except KeyboardInterrupt:
        logging.warning("Exiting program via keyboard interrupt.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        GPIO.cleanup()  # Clean up GPIO settings
        sys.exit(0)