from flask import request, Response, jsonify, make_response, render_template
import logging 

from modal.User import User
from routes.auth import auth_bp

from auth.authmiddleware import AuthMiddleware
from utils.JwtUtils import JwtUtils
from utils.redis.RedisUtils import AuthRedisClientUtils

auth_middleware = AuthMiddleware()

_jwt_util = JwtUtils()
_auth_redis_client_util = AuthRedisClientUtils()

@auth_bp.route("/forgot", methods=["GET"])
@auth_middleware.not_login_required
def forgot_get():
    """ Render the forgot password page."""
    return render_template("auth/forgot.html")