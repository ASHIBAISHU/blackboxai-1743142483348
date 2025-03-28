import logging
from logging.handlers import RotatingFileHandler
from functools import wraps
from flask import request
import json
import time

def configure_logging(app):
    """Configure application logging"""
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    
    # File handler (rotating logs)
    file_handler = RotatingFileHandler(
        'logs/lead_scoring.log',
        maxBytes=1000000,
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)
    
    # Add handlers
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.DEBUG)

def log_request(f):
    """Decorator to log API requests"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        
        # Log request details
        app.logger.info(f"Request: {request.method} {request.path}")
        app.logger.debug(f"Headers: {dict(request.headers)}")
        app.logger.debug(f"Body: {request.get_json(silent=True) or {}}")
        
        # Process request
        response = f(*args, **kwargs)
        
        # Log response details
        duration = (time.time() - start_time) * 1000
        app.logger.info(
            f"Response: {response[1]} ({duration:.2f}ms) "
            f"Size: {len(response[0].data)} bytes"
        )
        
        return response
    return decorated_function