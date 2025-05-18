from flask import request, Response, jsonify, make_response, render_template, url_for
from urllib.parse import urlparse
import logging 

from modal.User import User
from routes.auth import auth_bp

from auth.authmiddleware import AuthMiddleware
from utils.JwtUtils import JwtUtils
from utils.redis.RedisUtils import AuthRedisClientUtils

auth_middleware = AuthMiddleware()

_jwt_util = JwtUtils()
_auth_redis_client_util = AuthRedisClientUtils()

@auth_bp.route("/logout", methods=["GET", "PUT", "POST", "DELETE", "PATCH", "HEAD", "OPTIONS", "TRACE"])
# @auth_middleware.login_required
def logout_get():
    """ Logout route for user authentication."""
    # blacklist jwt token
    response = make_response(render_template('auth/logout.html', logout_path=urlparse(url_for('auth.logout_get')).path, auth_path=urlparse(url_for('auth.auth_index')).path), 200)
    response.set_cookie('auth_token', '', expires=0)
    response.headers['Location'] = f"{url_for('auth.auth_index')}?redirectedFrom={request.path}"
    try:
        token = request.headers.get("Authorization")
        if token:
            token = token.split(" ")[1]
            payload = _jwt_util.validate_token(token)

            if not payload:
                return response

            _auth_redis_client_util.convert_token_whitelist_to_blacklist(token)

    except Exception as e:
        logging.error(f"Error during logout: {str(e)}")
    
    response.headers['Authorization'] = ''
    return response