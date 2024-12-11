# This message will appear if the resource_tracker isn't patched.
#
# /usr/lib/python3.11/multiprocessing/resource_tracker.py:224: UserWarning:
# resource_tracker: There appear to be 1 leaked shared_memory objects to clean
# up at shutdown warnings.warn('resource_tracker: There appear to be %d '
# 

from multiprocessing import resource_tracker

def patched_register(name, rtype):
    if rtype == 'shared_memory':
        print(f"Register ignored for {name} ({rtype})")
        return
    original_register(name, rtype)

original_register = resource_tracker.register
resource_tracker.register = patched_register

from multiprocessing.shared_memory import SharedMemory
import struct

def write_shared_memory(registered_with_sip, call_active, ringing):
    # Attempt to connect to an existing shared memory block first
    shm = SharedMemory(name="ringring", create=False)
    print("Connected to existing shared memory block.")

    # Pack the booleans into two bytes
    data = struct.pack("???", registered_with_sip, call_active, ringing)
    shm.buf[:3] = data  # Write to shared memory
    shm.close()

    print(f"Written to shared memory: registeredWithSIP={registered_with_sip}, callActive={call_active}, ringing={ringing}")

if __name__ == "__main__":
    # Example usage
    registered_with_sip = True
    call_active = False
    ringing = False
    write_shared_memory(registered_with_sip, call_active, ringing)