"""
auth.py - login protection helpers.
Use the decorators above any route that needs a logged-in user or a specific role.

Example:
    @app.route("/admin")
    @role_required("admin")
    def admin_page(): ...
"""
from functools import wraps
from flask import session, redirect, url_for, flash

# Only students of the university can register.
# Change this to your university's real email domain.
ALLOWED_EMAIL_DOMAIN = "student.edu.sa"


def login_required(view):
    """Allow the page only for logged-in users."""
    @wraps(view)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapper


def role_required(*roles):
    """Allow the page only for the given roles, e.g. @role_required('seller', 'admin')."""
    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            if "user_id" not in session:
                flash("Please log in first.", "warning")
                return redirect(url_for("login"))
            if session.get("role") not in roles:
                flash("You do not have permission to open this page.", "danger")
                return redirect(url_for("index"))
            return view(*args, **kwargs)
        return wrapper
    return decorator