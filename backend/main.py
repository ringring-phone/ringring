from flask import Flask
from flask_cors import CORS
from routes.config import config_bp
from routes.status import status_bp

app = Flask(__name__)
cors = CORS(app, origins="*")

app.register_blueprint(config_bp, url_prefix='/api')
app.register_blueprint(status_bp, url_prefix='/api')

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)