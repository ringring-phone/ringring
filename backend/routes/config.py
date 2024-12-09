import os
import json
from flask import Blueprint, jsonify, request

CONFIG_FILE_PATH = "../config.json"
REQUIRED_KEYS = ["phoneNumber", "password", "sipIP"]

# Create a Blueprint for config routes
config_bp = Blueprint("config", __name__)

def validate_config(config):
    """Validate that the configuration contains all required keys."""
    return all(key in config for key in REQUIRED_KEYS)

def load_config():
    """Load the configuration from the JSON file."""
    if os.path.exists(CONFIG_FILE_PATH):
        with open(CONFIG_FILE_PATH, "r") as file:
            config = json.load(file)
            if validate_config(config):
                return config
            else:
                return {"error": "Invalid configuration in file. Missing required keys."}
    # Default config if file doesn't exist
    return {"phoneNumber": "", "password": "", "sipIP": ""}

def save_config(data):
    """Save the configuration to the JSON file."""
    with open(CONFIG_FILE_PATH, "w") as file:
        json.dump(data, file, indent=4)

@config_bp.route("/config", methods=["GET", "POST"])
def config():
    if request.method == "GET":
        config_data = load_config()
        if "error" in config_data:
            return jsonify(config_data), 400
        return jsonify(config_data)

    if request.method == "POST":
        try:
            # Parse incoming JSON data
            new_config = request.json
            if not validate_config(new_config):
                return jsonify({"error": "Missing required fields: phoneNumber, password, and sipIP"}), 400
            
            # Save new configuration to file
            save_config(new_config)
            return jsonify({"message": "Configuration updated successfully"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500