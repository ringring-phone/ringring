import time
import sys

def dialer():
    while True:
        print("Dialer sleeping")
        time.sleep(1)

if __name__ == '__main__':
    try:
        dialer()
    except KeyboardInterrupt:
        print('Exiting...')
        sys.exit(0)