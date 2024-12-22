from flask import Blueprint, jsonify
from ._shared import get_busy_state, set_busy_state

# Create a Blueprint for status routes
busy_bp = Blueprint("busy", __name__)
    
@busy_bp.route("/busy/on", methods=["POST"])
def on():
    """Turn busy on."""
    try:
        set_busy_state(True)
        return jsonify({"message": "Busy on"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 500

@busy_bp.route("/busy/off", methods=["POST"])
def off():
    """Turn busy off."""
    try:
        set_busy_state(False)
        return jsonify({"message": "Busy off"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 500

@busy_bp.route("/busy/status", methods=["GET"])
def ringer_status():
    """Get the current busy state."""
    try:
        state = get_busy_state()
        return jsonify({"status": state}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 500