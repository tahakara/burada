from flask import Blueprint, redirect, url_for

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/")
def auth_index():
    return redirect(url_for("auth.login_get", redirectedFrom="/auth"))
    
from . import login
from . import register
from . import logout
from . import forgot
from .verification import emailverification