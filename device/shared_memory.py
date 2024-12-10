from multiprocessing.shared_memory import SharedMemory
import struct
import time
import sys
from global_state import GlobalState, REGISTERED_WITH_SIP, CALL_ACTIVE, RINGING

SHARED_MEMORY_SIZE = 3
SHARED_MEMORY_NAME = "ringring"
SHARED_MEMORY_STRUCT = "???"

def build_shared_memory():
    globals = GlobalState()

    registered_with_sip = globals.get(REGISTERED_WITH_SIP) or False
    call_active = globals.get(CALL_ACTIVE) or False
    ringing = globals.get(RINGING) or False

    # Pack the data into shared memory
    return struct.pack(SHARED_MEMORY_STRUCT, registered_with_sip, call_active, ringing)

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
                    print(f"Shared memory updated: {globals.get(REGISTERED_WITH_SIP)}, {globals.get(CALL_ACTIVE)}, {globals.get(RINGING)}")
                elif current_shared != previous:
                    current = struct.unpack(SHARED_MEMORY_STRUCT, current_shared)

                    globals.set(REGISTERED_WITH_SIP, current[0])
                    globals.set(CALL_ACTIVE, current[1])
                    globals.set(RINGING, current[2])

                    previous = current_shared
                    print(f"Globals updated: {globals.get(REGISTERED_WITH_SIP)}, {globals.get(CALL_ACTIVE)}, {globals.get(RINGING)}")

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