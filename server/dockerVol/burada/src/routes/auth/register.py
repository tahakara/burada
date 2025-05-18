from flask import request, jsonify, make_response, Response, render_template, url_for
from urllib.parse import urlparse
from pydantic import ValidationError
from hashlib import sha256
import logging

from modal.User import User
from routes.auth import auth_bp

from auth.authmiddleware import AuthMiddleware
from utils.JwtUtils import JwtUtils
from utils.EmailUtils import EmailUtils, EmailTemplates
from utils.redis.RedisUtils import AuthRedisClientUtils
from schemas.auth_schemas.RegisterSchema import RegisterSchema, UsernameCheckSchema, EmailCheckSchema, PhoneCheckSchema

auth_middleware = AuthMiddleware()

_email_utils = EmailUtils()

@auth_bp.route("/register", methods=["GET"])
@auth_middleware.not_login_required
def register_get():
    """ Render the registration page."""
    return render_template("auth/register.html", username_available_path=url_for('auth.check_username'), register_path=url_for('auth.register_get'), login_path=url_for('auth.login_get'), forgot_path=url_for('auth.forgot_get'))

@auth_bp.route("/register", methods=["POST"])
@auth_middleware.not_login_required
def register_post():
    data = request.get_json()
    
    print("Data: ", data)

    username = data.get("username")
    email = data.get("email")
    phone = data.get("phone")
    password = data.get("password")
    password_confirm = data.get("password_confirm")

    try:
        shcema_data = RegisterSchema(**data)
    except ValidationError as e:
        # TODO: Critical:
        response = make_response(
            jsonify({"error": [{"field": error["loc"][0], "message": error["msg"]} for error in e.errors()], "redirect": None}), 401
        )
        return response
    
    username = shcema_data.username
    email = shcema_data.email
    phone = shcema_data.phone
    password = shcema_data.password
    password_confirm = shcema_data.passwordConfirm

    if sha256(password.encode()).hexdigest() != sha256(password_confirm.encode()).hexdigest():
        return make_response(jsonify({"error": "Password and password confirm do not match"}), 400)
       
    status, message, user = User.create(username=username, email=email, phone=phone, password=password)    
    if not status or not user:
        return make_response(jsonify({"error": message}), 400)

    verificaiton_email_content = EmailTemplates.get_verification_email(url_for("auth.verify_email", token=message, _external=True))
    try:
        is_hello_email_sent = _email_utils.send_email(user.email, "Hello", body_html=EmailTemplates.get_hello_mail())
        is_verificaiton_email_sent = _email_utils.send_email(user.email, "Verification Email", body_html=verificaiton_email_content)
    except Exception as e:
        logging.error(f"Error sending email: {e}")

    return make_response(jsonify({"message": "User created successfully","redirect":f"{url_for('auth.login_get')}?redirectedFrom={request.path}"}), 200)

@auth_bp.route("/register/username/available", methods=["POST"])
@auth_middleware.not_login_required
def check_username():
    """ Check if the username is already taken."""
    data = request.get_json()
    username = data.get("username").lower()

    if not username:
        return make_response(jsonify({"error": "Username is required"}), 400)
    
    # validate username
    try:
        schema_data = UsernameCheckSchema(**data)
    except ValidationError as e:
        return make_response(jsonify({"error": str(e)}), 400)

    username = schema_data.username.lower()

    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify({"available": False})

    return jsonify({"available": True})

@auth_bp.route("/register/email/available", methods=["POST"])
@auth_middleware.not_login_required
def check_email():
    """ Check if the username is already taken."""
    data = request.get_json()
    email = data.get("email").lower()

    if not email:
        return make_response(jsonify({"error": "Email is required"}), 400)
    
    if len(email) > 120:
        return make_response(jsonify({"error": "Email is too long"}), 400)
    try:
        schema_data = EmailCheckSchema(**data)
    except ValidationError as e:
        return make_response(jsonify({"error": str(e)}), 400)

    email = schema_data.username.lower()

    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify({"available": False})
    
    return jsonify({"available": True})

@auth_bp.route("/register/phone/available", methods=["POST"])
@auth_middleware.not_login_required
def check_phone():
    """ Check if the username is already taken."""
    data = request.get_json()
    phone = data.get("phone").lower()

    if not phone:
        return make_response(jsonify({"error": "Phone is required"}), 400)
    
    try:
        schema_data = PhoneCheckSchema(**data)
    except ValidationError as e:
        return make_response(jsonify({"error": str(e)}), 400)

    phone = schema_data.username.lower()

    user = User.query.filter_by(phone=phone).first()
    if user:
        return jsonify({"available": False})
    
    return jsonify({"available": True})