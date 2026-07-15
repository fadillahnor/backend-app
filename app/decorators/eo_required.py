from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt

def eo_required():

    def wrapper(fn):

        @wraps(fn)
        def decorator(*args, **kwargs):

            claims = get_jwt()

            if claims.get("role") != 2:
                return jsonify({
                    "msg": "Hanya EO"
                }), 403

            return fn(*args, **kwargs)

        return decorator

    return wrapper