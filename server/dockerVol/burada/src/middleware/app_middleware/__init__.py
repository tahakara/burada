from flask import Blueprint
from flask import request, g

import re

from modal import db
from modal import save_request_info, select_uuid

middleware_bp = Blueprint("middleware", __name__)

# region Middleware
@middleware_bp.before_app_request
def check_or_generate_cookies():
    """Before request hook to handle 'dust' cookie and set 'X-Dust-UUID' header."""
    uuid_regex = re.compile(r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$', re.IGNORECASE)
    if ('dust' in request.cookies) and uuid_regex.match(request.cookies.get('dust')):
        # If 'dust' cookie exists and matches UUID regex, set its value to 'X-Dust-UUID' header
        g.dust = request.cookies.get('dust')
    else:
        g.dust = select_uuid()

    if ('dust-device' in request.cookies) and uuid_regex.match(request.cookies.get('dust-device')):
        # If 'dust-device' cookie exists and matches UUID regex, set its value to 'X-Dust-Device' header
        g.dust_device = request.cookies.get('dust-device')
    else:
        g.dust_device = select_uuid()

@middleware_bp.after_app_request
def after_request(response):
    """After request hook to save request information."""
    response.set_cookie('dust', g.dust, max_age=86400, httponly=True, secure=True, samesite='None') # 1 day 60*60*24 = 
    response.set_cookie('dust-device', g.dust_device, max_age=31536000, httponly=True, secure=True, samesite='None') # 1 year 60*60*24*365
    save_request_info(db, request, g.dust, g.dust_device)

    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response
# endregion