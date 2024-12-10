from multiprocessing.shared_memory import SharedMemory
import struct
import time

def write_shared_memory(registered_with_sip, call_active, ringing):
    try:
        # Attempt to connect to an existing shared memory block first
        try:
            shm = SharedMemory(name="ringring", create=False)
            print("Connected to existing shared memory block.")
        except FileNotFoundError:
            # If not found, create a new shared memory block
            shm = SharedMemory(name="ringring", create=True, size=3)
            print("Created new shared memory block.")

        # Pack the booleans into two bytes
        data = struct.pack("???", registered_with_sip, call_active, ringing)
        shm.buf[:3] = data  # Write to shared memory

        print(f"Written to shared memory: registeredWithSIP={registered_with_sip}, callActive={call_active}, ringing={ringing}")

        while True:
            time.sleep(5)
    except Exception as e:
        print(f"Error: {e}")        
    finally:
        if 'shm' in locals():
            shm.close()
            shm.unlink()  # Explicitly remove shared memory block
            print("Shared memory unlinked.")


if __name__ == "__main__":
    # Example usage
    registered_with_sip = True
    call_active = False
    ringing = False
    write_shared_memory(registered_with_sip, call_active, ringing)