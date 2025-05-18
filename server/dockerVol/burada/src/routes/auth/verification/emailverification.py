from flask import request, Response, jsonify, make_response, render_template, url_for
from urllib.parse import urlparse
import logging 

from modal.User import User
from routes.auth import auth_bp

from auth.authmiddleware import AuthMiddleware
from utils.JwtUtils import JwtUtils
from utils.EmailUtils import EmailUtils, EmailTemplates
from utils.redis.RedisUtils import AuthRedisClientUtils
from utils.redis.RedisUtils import VerificaitonRedisClientUtils

auth_middleware = AuthMiddleware()

_jwt_util = JwtUtils()
_email_utils = EmailUtils()

_verificaiton_redis_client_util = VerificaitonRedisClientUtils()
_auth_redis_client_util = AuthRedisClientUtils()

@auth_bp.route("/verify", methods=["GET"])
def verify_email():
    """ Taking JWT token from the URL parma and verifying the email."""
    jwtToken = request.args.get("token")
    if jwtToken:
    
        payload = _jwt_util.validate_token(jwtToken)
        if payload & payload.get("user_uuid"):

            # Check if the token waitng for walidation on redis
            if _verificaiton_redis_client_util.verify_email_verificaiton_token(payload["user_uuid"], jwtToken):
                user = User.get_user_by_uuid(payload["user_uuid"])
                if user:
                    # Update the user email verification status
                    user.isEmailVerified = True
                    # Remove the token from redis
                    return make_response(url_for('auth.login_get', redirectedFrom=request.path, verification=True), 302)
                
    return make_response(url_for('auth.auth_index', redirectedFrom=request.path, verification=False), 302)

@auth_bp.route("/verify/resend", methods=["POST"])
@auth_middleware.login_required
def resend_verification_email():
    """ Resend the email verification link to the user."""
    token = request.headers.get("Authorization").split(' ')[1]
    user = None
    if token:
        payload = _jwt_util.validate_token(token)
        is_whitelisted = _auth_redis_client_util.is_token_whitelisted(payload["user_uuid"], token)
        if payload and is_whitelisted:
            user = User.get_user_by_uniqueId(uniqueId=payload["user_uuid"])
    
    if not user:
        return make_response(jsonify({"error": "User not found"}), 404)
    
    # Check if the user email is already verified
    if user.isEmailVerified:
        return make_response(jsonify({"error": "Email already verified"}), 400)
    
    try:
        # Generate a new JWT token for email verification
        jwtToken = _email_utils.create_verification_token(user.uniqueID, user.username, user.email)
        # set the token to redis for email verification
        _verificaiton_redis_client_util.set_email_verificaiton_token(user.uniqueID, jwtToken)

        _email_utils.send_email(user.email, "Email Verification", body_html=EmailTemplates.get_verification_email(url_for("auth.verify_email", token=jwtToken, _external=True)))
        return make_response(jsonify({"status": "ok"}), 200)
    except Exception as e:
        logging.error(f"Error sending verification email: {e}")
        return make_response(jsonify({"error": "Failed to send verification email"}), 500)

@auth_bp.route("/test", methods=["GET"])
def testt():
    """ Test route for email verification."""
    html_sting_body=EmailTemplates.get_hello_mail("test")
    _email_utils.send_email("abdullahumut200@gmail.com","Test", body_html=html_sting_body)
    return make_response(jsonify({"status":"ok"}))