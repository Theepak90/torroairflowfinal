from flask import Flask
from flask_cors import CORS
from app.config import config
from app.api.routes.discovery import discovery_bp
from app.database import init_db_pool
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
    
    # Initialize database connection pool
    init_db_pool(app)
    
    app.register_blueprint(discovery_bp)
    
    @app.route('/health', methods=['GET'])
    def health_check():
        return {'status': 'healthy'}, 200
    
    @app.route('/api/health', methods=['GET'])
    def api_health_check():
        return {'status': 'healthy'}, 200
    
    @app.teardown_appcontext
    def close_db(error):
        # Connections are automatically returned to pool via contextmanager
        pass
    
    logger.info('FN:create_app config_name:{}'.format(config_name))
    return app


if __name__ == '__main__':
    app = create_app('development')
    from app.config import config
    port = config['development'].BACKEND_PORT
    app.run(host='0.0.0.0', port=port, debug=True)
