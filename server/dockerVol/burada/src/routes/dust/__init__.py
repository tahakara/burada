from flask import Blueprint, redirect, url_for
from flask import request, g
from flask import current_app 
from flask import jsonify, make_response, send_from_directory
from modal.RequestInfo import RequestInfo


dust_bp = Blueprint("dust", __name__)

ALL_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD', 'TRACE', 'CONNECT']


@dust_bp.route('/ip', methods=ALL_METHODS)
def ip_info():
    """Endpoint to get IP information."""
    request_info = RequestInfo.create_request_info(request, g.dust, g.dust_device)
    return make_response(jsonify(request_info._toDictForIP()), 200, {'Content-Type': 'application/json'})

@dust_bp.route('/dust', methods=ALL_METHODS)
def favicon_png():
    """Return a 1x1 pixel favicon.png file."""
    response = make_response(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\xdac\xf8\xff\xff?\x00\x05\xfe\x02\xfeA\xdc\xcd\x00\x00\x00\x00IEND\xaeB`\x82', 200, {'Content-Type': 'image/png'})
    return response

@dust_bp.route('/beat', methods=ALL_METHODS)
def beat():
    """Endpoint to check if the server is alive."""
    return make_response(jsonify({"message": "alive"}), 200, {'Content-Type': 'application/json'})

@dust_bp.route('/trolley', methods=ALL_METHODS)
def trolley():
    """Sending javascript file from static folder"""
    return make_response(send_from_directory(current_app.static_folder, 'js/trolley/alpha-1/trolley-compact.js'), 200, {'Content-Type': 'application/javascript'})
