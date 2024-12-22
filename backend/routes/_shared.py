from multiprocessing import resource_tracker
from multiprocessing.shared_memory import SharedMemory
import struct

SHARED_MEMORY_SIZE = 5
SHARED_MEMORY_NAME = "ringring"

def patched_register(name, rtype):
    if rtype == 'shared_memory':
        print(f"Register ignored for {name} ({rtype})")
        return
    original_register(name, rtype)

original_register = resource_tracker.register
resource_tracker.register = patched_register

def read_shared_memory():
    """Read booleans from shared memory."""
    try:
        # Connect to the shared memory block
        shm = SharedMemory(name=SHARED_MEMORY_NAME, create=False)

        # Read the two booleans (assuming they are stored as two bytes)
        data = bytes(shm.buf[:SHARED_MEMORY_SIZE])  # Copy data from the buffer
        registered_with_sip, on_the_hook, call_active, ringing, busy = struct.unpack("?" * SHARED_MEMORY_SIZE, data)
        shm.close()

        return {
            "registeredWithSIP": registered_with_sip,
            "onTheHook": on_the_hook,
            "callActive": call_active,
            "ringing": ringing,
            "busy": busy
        }
    except FileNotFoundError:
        return {"error": "Shared memory not found. Is the application running?"}
    except Exception as e:
        return {"error": str(e)}
    finally:
        # Ensure the shared memory is properly closed
        if 'shm' in locals():
            shm.close()


def set_busy_state(active):
    """Set the busy state in shared memory."""
    try:
        shm = SharedMemory(name=SHARED_MEMORY_NAME, create=False)
        shm.buf[SHARED_MEMORY_SIZE - 1:SHARED_MEMORY_SIZE] = struct.pack("?", active)
        print(f"Ringer state set to: {'active' if active else 'inactive'}")
    except FileNotFoundError:
        raise ValueError("Shared memory not found. Ensure it is created first.")
    finally:
        if 'shm' in locals():
            shm.close()

def get_busy_state():
    """Get the current ringer state from shared memory."""
    return read_shared_memory()["busy"]