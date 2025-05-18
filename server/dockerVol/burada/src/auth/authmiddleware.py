from functools import wraps
from flask import request, g, Response, redirect, url_for, jsonify, make_response, render_template

from utils.JwtUtils import JwtUtils
from utils.redis.RedisUtils import AuthRedisClientUtils

# from routes.auth import auth_bp
# from routes.dashboard import dash_bp

class AuthMiddleware:
    def __init__(self):
        self.redis_client = AuthRedisClientUtils()
        self.jwt_utils = JwtUtils()

    def check_token_in_redis(self, token: str, payload: dict) -> bool:
        """
        Checks if a given token is blacklisted in Redis.
        Args:
            token (str): The token to be checked.
        Returns:
            bool: False if the token is blacklisted, True otherwise.
        """
        whitelisted = self.redis_client.is_token_whitelisted(payload['user_uuid'], token)
        if not whitelisted:
            return False
        return True

    def login_required(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            jwt_token = None

            if 'Authorization' in request.headers:
                jwt_token = request.headers['Authorization'].split(" ")[1]
            elif 'auth_token' in request.cookies:
                jwt_token = request.cookies.get('auth_token')
                # jwt_token = request.headers['Authorization'].split(" ")[1]

            if not jwt_token:
                response = make_response(jsonify({'error': 'Token is missing!'}), 302)
                response.headers['Location'] = f"{url_for('auth.login_get')}?redirectedFrom={request.path}"
                return response

            try:
                payload = self.jwt_utils.validate_token(jwt_token)
                if not payload:
                    response = make_response(jsonify({'error': 'Token is invalid or expired!'}), 302)
                    response.headers['Location'] = f"{url_for('auth.login_get')}?redirectedFrom={request.path}"
                    response.headers['Authorization'] = ''
                    return response

                # Check if the token is blacklisted in Redis
                if not self.check_token_in_redis(jwt_token, payload):
                    response = make_response(jsonify({'error': 'Token is invalid or expired!'}), 302)
                    response.headers['Location'] = f"{url_for('auth.login_get')}?redirectedFrom={request.path}"
                    response.headers['Authorization'] = ''
                    return response
                
                g.user = {}
                g.user['user_uuid'] = payload['user_uuid']
            except Exception as e:
                return jsonify({'error': f'Token validation error: {str(e)}'}), 403

            return f(*args, **kwargs)

        return decorated_function

    def not_login_required(self, f):
        """
        A decorator to allow access to routes only if the user is not logged in.
        This middleware checks for the presence of an authorization token in the 
        request headers. If a valid token is found and is not blacklisted, it 
        assumes the user is already logged in and denies access to the route. 
        Otherwise, it allows the request to proceed.
        Args:
            f (function): The route handler function to be wrapped by the decorator.
        Returns:
            function: The decorated function that enforces the "not logged in" requirement.
        Behavior:
            - If no token is present in the request headers, the request proceeds.
            - If a token is present:
                - If the token is blacklisted or invalid, the request proceeds.
                - If the token is valid and not blacklisted, a 403 response is returned 
                  with an "Already logged in!" error message.
        """

        @wraps(f)
        def decorated_function(*args, **kwargs):
            jwt_token = None
            if 'Authorization' in request.headers:
                jwt_token = request.headers['Authorization'].split(" ")[1]
            elif 'auth_token' in request.cookies:
                jwt_token = request.cookies.get('auth_token')
                print("burdayım be burdayım", jwt_token)

            if not jwt_token:
                return f(*args, **kwargs)

            try:
                payload = self.jwt_utils.validate_token(jwt_token)
                if payload:
                    # Check token in Redis to ensure it's not blacklisted
                    if not self.check_token_in_redis(jwt_token, payload):
                        return redirect(url_for('auth.logout_get', redirectedFrom=request.path))

                        # return jsonify({'error': 'Token is blacklisted or invalid (Midleware)!'}), 403
                    
                    # If token is valid and whitelisted, user is logged in
                    # TODO: Redericet to dash or something
                    return redirect(url_for('dash.dash_index', redirectedFrom=request.path))
                else:
                    return redirect(url_for('auth.logout_get', redirectedFrom=request.path))
            except Exception as e:
                print("asds", e)
                return f(*args, **kwargs)

        return decorated_function
