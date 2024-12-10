import time
import sys

def ringer():
    while True:
        print("Ringer sleeping")
        time.sleep(1)

if __name__ == '__main__':
    try:
        ringer()
    except KeyboardInterrupt:
        print('Exiting...')
        sys.exit(0)