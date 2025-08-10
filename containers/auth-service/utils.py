from functools import wraps
from flask import request, jsonify
from config import API_KEY

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('x-api-key')
        if not api_key or api_key != API_KEY:
            return jsonify({"message": "Invalid or missing API Key"}), 403
        return f(*args, **kwargs)
    return decorated_function
