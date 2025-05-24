import logging
import hashlib
import hmac
import os

from functools import wraps

import jwt
from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


def validate_signature(payload, signature):
    expected_signature = hmac.new(
        bytes(os.getenv("APP_SECRET"), "latin-1"),
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


# def required_authorization(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#
#         token = None
#         if 'Authorization' in request.headers:
#             bearer = request.headers['Authorization']
#             token = bearer.replace('Bearer ', '')
#
#         if not token:
#             return jsonify({'mensagem': 'Token ausente'}), 401
#
#         try:
#             payload = jwt.jwt.decode(token, os.getenv("SECRET_KEY", ""), algorithms=['HS256'])
#             request.user_id = payload['user_id']
#         except jwt.ExpiredSignatureError:
#             return JSONResponse(status_code=401, content={'mensagem': 'Token expirado'})
#         except jwt.InvalidTokenError:
#             return SONResponse(status_code=401, content={'mensagem': 'Token inválido'})
#
#         return f(*args, **kwargs)
#
#     return decorated_function
