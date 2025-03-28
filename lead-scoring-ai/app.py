from flask import Flask, render_template
from app.api.routes import api_blueprint
from app.utils.logging import configure_logging
from app.utils.auth import jwt
from app.core.model_training import ModelTrainer
from app.core.data_processing import DataProcessor

def create_app():
    app = Flask(__name__, static_folder='app/static')
    app.config.from_pyfile('config.py')
    
    # Initialize extensions
    configure_logging(app)
    jwt.init_app(app)
    
    # Initialize core components
    with app.app_context():
        data_processor = DataProcessor()
        model_trainer = ModelTrainer()
        
        # Load or train model
        try:
            X, y = model_trainer.load_data('data/leads.csv')
            model_trainer.train_models(X, y)
        except Exception as e:
            app.logger.error(f"Model training failed: {e}")

    # Register blueprints
    app.register_blueprint(api_blueprint, url_prefix='/api')
    
    # Web routes
    @app.route('/')
    def dashboard():
        return render_template('dashboard.html')
        
    @app.route('/feedback')
    def feedback():
        return render_template('feedback.html')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404
        
    @app.errorhandler(500)
    def server_error(error):
        return render_template('500.html'), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)