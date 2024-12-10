from multiprocessing.shared_memory import SharedMemory
import struct
import time
from global_state import GlobalState

def global_state_changed(key, old_value, new_value):
    print(f"GlobalState changed: {key} from {old_value} to {new_value}")
    try:
        # Attach to the shared memory block
        shm = SharedMemory(name="ringring", create=True, size=3)
        globals = GlobalState()

        # Prepare data to write to shared memory
        registered_with_sip = globals.get("registered_with_sip") or False
        call_active = globals.get("call_active") or False
        ringing = globals.get("ringing") or False

        # Pack the data into shared memory
        data = struct.pack("???", registered_with_sip, call_active, ringing)
        shm.buf[:3] = data
        print(f"Shared memory updated: {registered_with_sip}, {call_active}, {ringing}")
    except FileNotFoundError:
        print("Shared memory block not found. Could not update shared memory.")


def shared_memory():
    shm = None
    globals = GlobalState()
    globals.add_listener(global_state_changed)

    # Store previous to watch for changes
    previous = None

    while True:
        if shm is None:
            try:
                shm = SharedMemory(name="ringring", create=False)
            except FileNotFoundError:
                # Do nothing
                pass

        if shm is not None:
            data = bytes(shm.buf[:3])  # Copy data from the buffer
            current = struct.unpack("???", data)

            if current != previous:
                previous = current

                globals.set("registered_with_sip", current[0], suppress=[global_state_changed])
                globals.set("call_active", current[1], suppress=[global_state_changed])
                globals.set("ringing", current[2], suppress=[global_state_changed])

        time.sleep(1)