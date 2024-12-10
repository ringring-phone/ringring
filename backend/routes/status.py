from flask import Blueprint, jsonify
from multiprocessing.shared_memory import SharedMemory
import struct

# Create a Blueprint for status routes
status_bp = Blueprint("status", __name__)

def read_shared_memory():
    """Read booleans from shared memory."""
    try:
        # Connect to the shared memory block
        shm = SharedMemory(name="ringring", create=False)
        # Read the two booleans (assuming they are stored as two bytes)
        data = bytes(shm.buf[:3])  # Copy data from the buffer
        registered_with_sip, call_active, ringing = struct.unpack("???", data)
        return {"registeredWithSIP": registered_with_sip, "callActive": call_active, "ringing": ringing}
    except FileNotFoundError:
        return {"error": "Shared memory not found. Is the application running?"}
    except Exception as e:
        return {"error": str(e)}
    finally:
        # Ensure the shared memory is properly closed
        if 'shm' in locals():
            shm.close()
    
@status_bp.route("/status", methods=["GET"])
def status():
    """GET /api/status - Fetch status from shared memory."""
    try:
        return jsonify(read_shared_memory())
    except Exception as e:
        return jsonify({"error": str(e)}), 500