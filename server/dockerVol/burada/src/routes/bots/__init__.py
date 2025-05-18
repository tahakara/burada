from flask import Blueprint, redirect, url_for
from flask import request, g
from flask import current_app
from flask import make_response, send_from_directory, render_template


bots_bp = Blueprint("bots", __name__)

ALL_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD', 'TRACE', 'CONNECT']

@bots_bp.route('/robots.txt', methods=ALL_METHODS)
def robots_txt():
    """Return a robots.txt file."""
    return make_response(render_template('robots.txt'), 200, {'Content-Type': 'text/plain'})

@bots_bp.route('/favicon.ico', methods=ALL_METHODS)
def favicon_ico():
    """Return a favicon.ico file."""
    return make_response(send_from_directory(current_app.static_folder, 'favicon.ico'), 200, {'Content-Type': 'image/x-icon'})

@bots_bp.route('/favicon', methods=ALL_METHODS)
def favicon_png():
    """Return a 1x1 pixel favicon.png file."""
    response = make_response(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\xdac\xf8\xff\xff?\x00\x05\xfe\x02\xfeA\xdc\xcd\x00\x00\x00\x00IEND\xaeB`\x82', 200, {'Content-Type': 'image/png'})
    return response

