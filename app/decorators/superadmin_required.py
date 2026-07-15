from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt

def superadmin_required():

    def wrapper(fn):

        @wraps(fn)
        def decorator(*args, **kwargs):

            claims = get_jwt()

            if claims.get("role") != 3:
                return jsonify({
                    "msg": "Akses ditolak. Hanya Super Admin."
                }), 403

            return fn(*args, **kwargs)

        return decorator

    return wrapper
