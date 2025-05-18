from flask import Blueprint, redirect, render_template, url_for, g
from urllib.parse import urlparse

# Middlewares
from auth.authmiddleware import AuthMiddleware
auth_middleware = AuthMiddleware()


dash_bp = Blueprint("dash", __name__, url_prefix="/dashboard")


@dash_bp.route("/")
@auth_middleware.login_required
def dash_index():
    return render_template("dashboard/dashboard.html", logout_path=urlparse(url_for("auth.logout_get")).path)

@dash_bp.route("/lessons")
@auth_middleware.login_required
def lessons():
    return render_template("dashboard/lessons/index.html", logout_path=urlparse(url_for("auth.logout_get")).path)

@dash_bp.route("/lessons/detail/<lesson_uuid>")
@auth_middleware.login_required
def lessons_detail(lesson_uuid):
    return render_template("dashboard/lessons/detail.html", lesson_uuid=lesson_uuid, logout_path=urlparse(url_for("auth.logout_get")).path)