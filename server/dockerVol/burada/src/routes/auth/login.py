from flask import request, jsonify, make_response, Response, render_template, url_for
from urllib.parse import urlparse
from pydantic import ValidationError
import logging

# Models 
from modal.User import User

# Parent route
from routes.auth import auth_bp

# Middlewares
from auth.authmiddleware import AuthMiddleware

# Utils
from utils.JwtUtils import JwtUtils
from utils.redis.RedisUtils import AuthRedisClientUtils
from schemas.auth_schemas.LoginSchema import LoginSchema

auth_middleware = AuthMiddleware()

_jwt_util = JwtUtils()
_auth_redis_client_util = AuthRedisClientUtils()

@auth_bp.route("/login", methods=["GET"])
@auth_middleware.not_login_required
def login_get():
    """ Render the login page."""
    return render_template("auth/login.html", forgot_path=urlparse(url_for('auth.forgot_get')).path, register_path=urlparse(url_for('auth.register_get')).path, login_path=urlparse(url_for('auth.login_get')).path) 

@auth_bp.route("/login", methods=["POST"])
@auth_middleware.not_login_required
def login_post():
    """
    Handles user login by validating input data, authenticating the user, and generating a JWT token.
    This function expects a JSON payload with the following fields:
    - `username` (str): The username of the user.
    - `email` (str): The email address of the user.
    - `phone` (str): The phone number of the user.
    - `password` (str): The password of the user.
    Returns:
        Response: A Flask response object with the following outcomes:
        - 400 Bad Request: If required fields are missing.
        - 401 Unauthorized: If authentication fails.
        - 200 OK: If authentication is successful, includes a JWT token in the `Authorization` header.
    Headers:
        - `Authorization`: Contains the JWT token in the format `Bearer <access_token>`.
        - `Location`: Redirects to the root path `/`.
        - `Access-Control-Expose-Headers`: Exposes the `Authorization` header for client-side access.
    Notes:
        - The `User.login` method is used to authenticate the user.
        - The `JwtUtils.create_token` method is used to generate the JWT token.
    """
    
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    phone = data.get("phone")
    password = data.get("password")

    if ((not username) and (not email) and (not phone)) or (not password):
        return make_response(jsonify({"error": "All field are required"}), 400)
    
    # if (not username) | (not email) | (not phone):
    #     return make_response(jsonify({"error": "Username, email, and phone are required"}), 400)
    
    # Validaiton
    try:
        schema_data = LoginSchema(username=username, email=email, phone=phone, password=password)
    except ValidationError as e:  # Catch Pydantic's ValidationError
        # Handle validation errors
        response = make_response(
            jsonify({"error": [{"field": error["loc"][0], "message": error["msg"]} for error in e.errors()], "redirect": None}), 401
        )
        response.set_cookie("auth_token", "", expires=0)
        response.headers["Location"] = f"{urlparse(url_for('auth.login_get'))}?redirectedFrom={request.path}"
        return response
    except Exception as e:  # Catch any other unexpected exceptions
        logging.error(f"Unexpected error during login: {str(e)}")
        response = make_response(
            jsonify({"error": "Unexpected error during login", "redirect": f"{urlparse(url_for('auth.login_get'))}?redirectedFrom={request.path}"}), 500
        )
        response.set_cookie("auth_token", "", expires=0)
        response.headers["Location"] = f"{urlparse(url_for('auth.login_get'))}?redirectedFrom={request.path}"
        return response
    
    print(schema_data.username, schema_data.email, schema_data.phone, schema_data.password)

    login = User.login(username=schema_data.username, email=schema_data.email, phone=schema_data.phone, password=schema_data.password)

    if not login[0]:    # Error occurred (false, error message)
        response = make_response(jsonify({"error": login[1]}), 418)
        response.headers["Location"] = f"{urlparse(url_for('auth.login_get'))}?redirectedFrom={request.path}"

    # login[0] is True, login[1] message login[2] is the user object
    token = _jwt_util.create_token(login[2].uniqueID, login[2].username, login[2].email)

    _auth_redis_client_util.whitelist_token(login[2].uniqueID, token["access_token"], token)

    response = make_response(jsonify({"message": login[1], "redirect": url_for("dash.dash_index")}), 200)
    response.headers["Access-Control-Expose-Headers"] = "Authorization"
    response.headers["Authorization"] = f"Bearer {token['access_token']}"
    response.set_cookie("auth_token", token["access_token"], httponly=True, secure=True, samesite="Strict")
    response.headers["Location"] = f"{urlparse(url_for('dash.dash_index'))}?redirectedFrom={request.path}"
    return response 


