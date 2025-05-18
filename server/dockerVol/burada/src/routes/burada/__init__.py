from flask import Blueprint
from flask import request, g
from flask import current_app 
from flask import jsonify, make_response, send_from_directory, render_template


burada_bp = Blueprint("bot", __name__, url_prefix='/burada')

ALL_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD', 'TRACE', 'CONNECT']

@burada_bp.route('/', methods=['POST', 'GET'])
def burada():
    from random import choice
    print(request.data)
    """Sending javascript file from static folder"""
    return make_response(jsonify({'status':choice([000, 100, 200, 400])}), 200, {'Content-Type': 'application/json'})