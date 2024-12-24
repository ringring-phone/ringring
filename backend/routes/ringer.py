from flask import Blueprint, jsonify
from ._shared import get_ringer_state, set_ringer_state

# Create a Blueprint for status routes
ringer_bp = Blueprint("ringer", __name__)
    
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