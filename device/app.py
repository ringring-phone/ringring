import time
import sys

def app():
    while True:
        print("App sleeping")
        time.sleep(1)

if __name__ == '__main__':
    try:
        app()
    except KeyboardInterrupt:
        print('Exiting...')
        sys.exit(0)