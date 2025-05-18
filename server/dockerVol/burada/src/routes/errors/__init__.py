from flask import Blueprint, render_template, make_response

errors_bp = Blueprint("errors", __name__)

@errors_bp.app_errorhandler(400)
def bad_request(e):
    """Return a 400 (Bad Request) error page."""
    return make_response(render_template('error/401.html'), 400, {'Content-Type': 'text/html'})

@errors_bp.app_errorhandler(401)
def unauthorized(e):
    """Return a 401 (Unauthorized) error page."""
    return make_response(render_template('error/401.html'), 401, {'Content-Type': 'text/html'})

@errors_bp.app_errorhandler(403)
def forbidden(e):
    """Return a 403 (Forbidden) error page."""
    return make_response(render_template('error/401.html'), 403, {'Content-Type': 'text/html'})

@errors_bp.app_errorhandler(404)
def page_not_found(e):
    """Return a 404 (Not Found) error page."""
    return make_response(render_template('error/401.html'), 404, {'Content-Type': 'text/html'})

@errors_bp.app_errorhandler(405)
def method_not_allowed(e):
    """Return a 405 (Not Allowed) error page."""
    return make_response(render_template('error/401.html'), 405, {'Content-Type': 'text/html'})

@errors_bp.app_errorhandler(408)
def request_timeout(e):
    """Return a 408 (Request Timeout) error page."""
    return make_response(render_template('error/401.html'), 408, {'Content-Type': 'text/html'})

@errors_bp.app_errorhandler(500)
def internal_server_error(e):
    """Return a 500 (Internal Server Error) error page."""
    return make_response(render_template('error/401.html'), 500, {'Content-Type': 'text/html'})

@errors_bp.app_errorhandler(501)
def not_implemented(e):
    """Return a 501 (Not Implemented) error page."""
    return make_response(render_template('error/401.html'), 501, {'Content-Type': 'text/html'})

@errors_bp.app_errorhandler(503)
def service_unavailable(e):
    """Return a 503 (Service Unavailable) error page."""
    return make_response(render_template('error/401.html'), 503, {'Content-Type': 'text/html'})

@errors_bp.app_errorhandler(504)
def gateway_timeout(e):
    """Return a 504 (Gateway Timeout) error page."""
    return make_response(render_template('error/401.html'), 504, {'Content-Type': 'text/html'})

@errors_bp.app_errorhandler(429)
def too_many_requests(e):
    """Return a 429 (Too Many Requests) error page."""
    return make_response(render_template('error/401.html'), 429, {'Content-Type': 'text/html'})

# @errors_bp.app_errorhandler(Exception)
# def handle_exception(e):
#     """Return a generic error page for unhandled exceptions."""
#     error(f"Unhandled exception: {e}")
#     return make_response(jsonify({"error": "X"}), 500, {'Content-Type': 'application/json'})
# endregion