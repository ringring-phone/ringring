import time
import sys

def hook():
    while True:
        print("Hook sleeping")
        time.sleep(1)

if __name__ == '__main__':
    try:
        hook()
    except KeyboardInterrupt:
        print('Exiting...')
        sys.exit(0)