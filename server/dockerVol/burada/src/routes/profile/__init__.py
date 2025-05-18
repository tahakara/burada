from flask import Blueprint, redirect, render_template

# Middlewares
from auth.authmiddleware import AuthMiddleware
auth_middleware = AuthMiddleware()


profile_bp = Blueprint("profile", __name__, url_prefix="/profile")


@profile_bp.route("/")
@auth_middleware.login_required
def profile_index():
    return render_template("profile/profile.html")