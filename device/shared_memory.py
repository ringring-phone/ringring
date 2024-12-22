from multiprocessing.shared_memory import SharedMemory
import struct
import time
import sys
import logging
from global_state import GlobalState, State

SHARED_MEMORY_SIZE = 5
SHARED_MEMORY_NAME = "ringring"

def build_shared_memory():
    globals = GlobalState()

    registered_with_sip = globals.get(State.REGISTERED_WITH_SIP) or False
    call_active = globals.get(State.CALL_ACTIVE) or False
    ringing = globals.get(State.RINGING) or False
    on_the_hook = globals.get(State.ON_THE_HOOK) or False
    busy = globals.get(State.BUSY) or False

    # Pack the data into shared memory
    return struct.pack("?" * SHARED_MEMORY_SIZE, registered_with_sip, on_the_hook, call_active, ringing, busy)

def shared_memory():
    shm = None
    globals = GlobalState()

    # Store previous to watch for changes
    previous = None

    try:
        while True:
            if shm is None:
                # First time through, write out the global state
                try:
                    shm = SharedMemory(name=SHARED_MEMORY_NAME, create=True, size=SHARED_MEMORY_SIZE)
                    previous = build_shared_memory()
                    shm.buf[:SHARED_MEMORY_SIZE] = previous
                except FileNotFoundError:
                    # Do nothing
                    pass

            if shm is not None:
                current_globals = build_shared_memory()
                current_shared = bytes(shm.buf[:SHARED_MEMORY_SIZE])

                if current_globals != previous:
                    previous = build_shared_memory()
                    shm.buf[:SHARED_MEMORY_SIZE] = previous
                    logging.debug(f"Shared memory updated: {globals.get(State.REGISTERED_WITH_SIP)}, {globals.get(State.ON_THE_HOOK)}, {globals.get(State.CALL_ACTIVE)}, {globals.get(State.RINGING)}, {globals.get(State.BUSY)}")
                elif current_shared != previous:
                    current = struct.unpack("?" * SHARED_MEMORY_SIZE, current_shared)

                    globals.set(State.REGISTERED_WITH_SIP, current[0])
                    globals.set(State.ON_THE_HOOK, current[1])
                    globals.set(State.CALL_ACTIVE, current[2])
                    globals.set(State.RINGING, current[3])
                    globals.set(State.BUSY, current[4])

                    previous = current_shared
                    logging.debug(f"Globals updated: {globals.get(State.REGISTERED_WITH_SIP)}, {globals.get(State.ON_THE_HOOK)}, {globals.get(State.CALL_ACTIVE)}, {globals.get(State.RINGING)}, {globals.get(State.BUSY)}")

            time.sleep(1)
    finally:
        if shm is not None:
            shm.close()
            shm.unlink()

if __name__ == '__main__':
    try:
        shared_memory()
    except KeyboardInterrupt:
        print('Exiting...')
        sys.exit(0)