import json
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
    async def decorated_function(*args, **kwargs):
        request: Request = kwargs.get("request")
        if request is None:
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

        if request is None:
            return JSONResponse(status_code=400, content={"status": "error", "message": "Missing request object"})

        signature = request.headers.get("X-Hub-Signature-256", "")[7:]
        body_bytes = await request.body()
        payload = body_bytes.decode("utf-8")

        if not validate_signature(payload=payload, signature=signature):
            logger.info("Signature verification failed!")
            return JSONResponse(status_code=403, content={"status": "error", "message": "Invalid signature"})

        return await f(*args, **kwargs)

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
