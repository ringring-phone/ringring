import RPi.GPIO as GPIO
import time
import sys
import logging
from global_state import GlobalState

# Pin configuration
CLICKPIN = 35
STOPPIN = 37

def dialer():
    globals = GlobalState()

    # GPIO setup
    GPIO.setup(CLICKPIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(STOPPIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    clickPressed = False
    stopPressed = False
    clickCounter = 0

    # Sequence starts empty when the program runs
    sequence = ""

    # Track the time of the last recorded number
    last_recorded_time = time.time()

    while True:  # Run forever
        current_time = time.time()

        # Check if more than 2 seconds have passed since the last recorded number
        if current_time - last_recorded_time > 2 and sequence:
            globals.addCommand(sequence)
            sequence = ""

        # Check CLICKPIN
        if GPIO.input(CLICKPIN) == GPIO.HIGH and not clickPressed:
            clickPressed = True
            clickCounter += 1
        elif GPIO.input(CLICKPIN) == GPIO.LOW and clickPressed:
            clickPressed = False

        # Check STOPPIN
        if GPIO.input(STOPPIN) == GPIO.HIGH and not stopPressed:
            if clickCounter != 0:
                recorded_value = 0 if clickCounter == 10 else clickCounter

                if (recorded_value < 10):
                    sequence += str(recorded_value)
                    logging.debug(f'Recorded {recorded_value}')
                else:
                    logging.debug(f'Ignored {recorded_value}')

                last_recorded_time = time.time()

            stopPressed = True
            clickCounter = 0
        elif GPIO.input(STOPPIN) == GPIO.LOW and stopPressed:
            stopPressed = False

        time.sleep(0.005)


if __name__ == '__main__':
    try:
        dialer()
    except KeyboardInterrupt:
        logging.warning("Exiting program.")
    except Exception as e:
        logging.error(e)
    finally:
        GPIO.cleanup()
        sys.exit(0)
