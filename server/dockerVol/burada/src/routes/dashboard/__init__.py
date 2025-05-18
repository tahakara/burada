from flask import Blueprint, redirect, render_template, url_for
from urllib.parse import urlparse

# Middlewares
from auth.authmiddleware import AuthMiddleware
auth_middleware = AuthMiddleware()


dash_bp = Blueprint("dash", __name__, url_prefix="/dashboard")


@dash_bp.route("/")
@auth_middleware.login_required
def dash_index():
    return render_template("dashboard/dashboard.html", logout_path=urlparse(url_for("auth.logout_get")).path)