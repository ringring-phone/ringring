from flask import Flask
from flask_cors import CORS
import logging
from logging.handlers import RotatingFileHandler
from routes.config import config_bp
from routes.status import status_bp
from routes.ringer import ringer_bp

def create_app():
  app = Flask(__name__)
  cors = CORS(app, origins="*")

  app.register_blueprint(config_bp, url_prefix='/api')
  app.register_blueprint(status_bp, url_prefix='/api')
  app.register_blueprint(ringer_bp, url_prefix='/api')

  # Create a rotating file handler
  log_handler = RotatingFileHandler('../flask.log', maxBytes=100000, backupCount=3)
  log_handler.setLevel(logging.INFO)
  formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
  log_handler.setFormatter(formatter)
  
  # Attach the handler to Flask's logger
  app.logger.addHandler(log_handler)

  return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=8080)