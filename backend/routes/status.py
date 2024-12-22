from flask import Blueprint, jsonify
from ._shared import read_shared_memory

# Create a Blueprint for status routes
status_bp = Blueprint("status", __name__)
    
@status_bp.route("/status", methods=["GET"])
def status():
    """GET /api/status - Fetch status from shared memory."""
    try:
        return jsonify(read_shared_memory())
    except Exception as e:
        return jsonify({"error": str(e)}), 500