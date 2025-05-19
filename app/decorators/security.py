import logging
import hashlib
import hmac

from functools import wraps
from flask import (
    current_app,
    jsonify,
    request,
)
logger = logging.getLogger(__name__)

def validate_signature(payload, signature):
    expected_signature = hmac.new(
        bytes(current_app.config["APP_SECRET"], "latin-1"),
        msg=payload.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected_signature, signature)


def signature_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        signature = request.headers.get("X-Hub-Signature-256", "")[7:]
        if not validate_signature(payload=request.data.decode("utf-8"), signature=signature):
            logger.info("Signature verification failed!")
            return jsonify({"status": "error", "message": "Invalid signature"}), 403
        return f(*args, **kwargs)

    return decorated_function


def required_authorization(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        token = None
        if 'Authorization' in request.headers:
            bearer = request.headers['Authorization']
            token = bearer.replace('Bearer ', '')

        if not token:
            return jsonify({'mensagem': 'Token ausente'}), 401

        try:
            payload = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=['HS256'])
            request.user_id = payload['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'mensagem': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'mensagem': 'Token inválido'}), 401

        return f(*args, **kwargs)

    return decorated_function
