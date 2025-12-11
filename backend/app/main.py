from flask import Flask
from flask_cors import CORS
from app.config import config
from app.api.routes.discovery import discovery_bp
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    app.register_blueprint(discovery_bp)
    
    @app.route('/health', methods=['GET'])
    def health_check():
        return {'status': 'healthy'}, 200
    
    logger.info("Flask application created successfully")
    return app


if __name__ == '__main__':
    app = create_app('development')
    app.run(host='0.0.0.0', port=5001, debug=True)
