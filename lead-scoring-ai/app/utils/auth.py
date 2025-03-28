from flask_jwt_extended import JWTManager, create_access_token, verify_jwt_in_request
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask import jsonify
import os

jwt = JWTManager()

# In a real application, this would be in a database
users = {
    "admin": {
        "password": generate_password_hash(os.getenv("ADMIN_PASSWORD", "securepassword")),
        "roles": ["admin"]
    },
    "analyst": {
        "password": generate_password_hash("analyst123"),
        "roles": ["analyst"]
    }
}

def admin_required(fn):
    """Decorator to require admin role"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        current_user = get_jwt_identity()
        if current_user not in users or "admin" not in users[current_user]["roles"]:
            return jsonify({"error": "Admin access required"}), 403
        return fn(*args, **kwargs)
    return wrapper

def analyst_required(fn):
    """Decorator to require analyst role"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        current_user = get_jwt_identity()
        if current_user not in users:
            return jsonify({"error": "Invalid user"}), 403
        return fn(*args, **kwargs)
    return wrapper

def setup_auth(app):
    """Configure authentication for the application"""
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET", "super-secret-key")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600  # 1 hour
    jwt.init_app(app)