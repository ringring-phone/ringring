import threading
import time
from ringer import ringer
from dialer import dialer
from hook import hook
from shared_memory import shared_memory
from sip import sip

if __name__ == '__main__':
    # Create and start threads
    threads = [
        threading.Thread(target=ringer, daemon=True),
        threading.Thread(target=dialer, daemon=True),
        threading.Thread(target=hook, daemon=True),
        threading.Thread(target=shared_memory, daemon=True),
        threading.Thread(target=sip, daemon=True)
    ]

    for thread in threads:
        thread.start()

    # Keep the main thread alive
    try:
        while True:
            # print("Main sleeping")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting program")