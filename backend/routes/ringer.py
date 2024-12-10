from flask import Blueprint, jsonify
from multiprocessing.shared_memory import SharedMemory
import struct

# Create a Blueprint for status routes
ringer_bp = Blueprint("ringer", __name__)

def set_ringer_state(active):
    """Set the ringer state (start/stop) in shared memory."""
    try:
        shm = SharedMemory(name="ringring", create=False)
        shm.buf[2:3] = struct.pack("?", active)  # Use 3rd byte for ringer state
        print(f"Ringer state set to: {'active' if active else 'inactive'}")
    except FileNotFoundError:
        raise ValueError("Shared memory not found. Ensure it is created first.")
    finally:
        if 'shm' in locals():
            shm.close()

def get_ringer_state():
    """Get the current ringer state from shared memory."""
    try:
        shm = SharedMemory(name="ringring", create=False)
        state = struct.unpack("?", bytes(shm.buf[2:3]))[0]  # Read 3rd byte
        return state
    except FileNotFoundError:
        raise ValueError("Shared memory not found. Ensure it is created first.")
    finally:
        if 'shm' in locals():
            shm.close()
    
@ringer_bp.route("/ringer/start", methods=["POST"])
def start():
    """Start the ringer."""
    try:
        set_ringer_state(True)  # Set ringer to active
        return jsonify({"message": "Ringer started"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 500

@ringer_bp.route("/ringer/stop", methods=["POST"])
def stop():
    """Stop the ringer."""
    try:
        set_ringer_state(False)  # Set ringer to inactive
        return jsonify({"message": "Ringer stopped"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 500

@ringer_bp.route("/ringer/status", methods=["GET"])
def ringer_status():
    """Get the current ringer state."""
    try:
        state = get_ringer_state()
        return jsonify({"status": state}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 500