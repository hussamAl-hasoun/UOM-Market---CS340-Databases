"""
routes/admin.py - the admin panel (the university supervisor / doctor).
The admin can:
  - see ALL listings with full details, and remove any of them (reason required)
  - see all students, and suspend / activate them (a suspended student is logged out)
  - read the moderation log (every removed listing and why)
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from db import fetch_all, fetch_one, execute, get_connection
from auth import role_required

bp = Blueprint("admin", __name__, url_prefix="/admin")


def run_transaction(steps):
    """Run several statements as ONE unit: all succeed, or none are saved.
    steps = [(sql, params), (sql, params), ...]"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        for sql, params in steps:
            cursor.execute(sql, params or ())
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@bp.before_app_request
def block_suspended_users():
    """If the admin suspended a logged-in user, log him out right away.
    (before_app_request = this check runs before EVERY page of the website)"""
    if "user_id" in session and request.endpoint not in ("static", "serve_image"):
        row = fetch_one("SELECT is_active FROM users WHERE user_id = %s", (session["user_id"],))
        if row is None or not row["is_active"]:
            session.clear()
            flash("Your account is suspended. Please contact the administration.", "danger")
            return redirect(url_for("login"))


# ---------------------------------------------------------------
# Listings: see all (with details), remove any
# ---------------------------------------------------------------
@bp.route("/")
@role_required("admin")
def listings():
    search = request.args.get("search", "").strip()
    status = request.args.get("status", "")

    counts = fetch_one("""
        SELECT (SELECT COUNT(*) FROM users)                               AS users,
               (SELECT COUNT(*) FROM listings)                            AS listings,
               (SELECT COUNT(*) FROM listings WHERE status = 'available') AS available,
               (SELECT COUNT(*) FROM orders)                              AS orders,
               (SELECT COUNT(*) FROM moderation_log)                      AS removed
    """)

    sql = "SELECT * FROM admin_listings_overview WHERE 1 = 1"
    params = []
    if search:
        sql += " AND (title LIKE %s OR seller LIKE %s OR seller_email LIKE %s)"
        params += [f"%{search}%"] * 3
    if status in ("available", "sold"):
        sql += " AND status = %s"
        params.append(status)
    sql += " ORDER BY created_at DESC, listing_id DESC"

    return render_template("admin_listings.html", counts=counts,
                           listings=fetch_all(sql, params), search=search, status=status)


@bp.route("/listings/<int:listing_id>/remove", methods=["POST"])
@role_required("admin")
def remove_listing(listing_id):
    reason = request.form.get("reason", "").strip()
    listing = fetch_one("SELECT listing_id, title, seller_id FROM listings WHERE listing_id = %s",
                        (listing_id,))

    if not listing:
        flash("Listing not found.", "danger")
    elif not reason:
        flash("Please write a reason for removing the listing.", "danger")
    else:
        orders_count = fetch_one("SELECT COUNT(*) AS n FROM orders WHERE listing_id = %s",
                                 (listing_id,))["n"]
        # ONE transaction: write the log, delete its orders, delete the listing.
        # If any step fails, nothing is saved.
        run_transaction([
            ("INSERT INTO moderation_log (admin_id, seller_id, listing_title, reason, orders_removed) "
             "VALUES (%s, %s, %s, %s, %s)",
             (session["user_id"], listing["seller_id"], listing["title"], reason[:255], orders_count)),
            ("DELETE FROM orders WHERE listing_id = %s", (listing_id,)),
            ("DELETE FROM listings WHERE listing_id = %s", (listing_id,)),
        ])
        flash(f"Listing '{listing['title']}' was removed and the action was logged.", "success")

    return redirect(url_for("admin.listings"))


# ---------------------------------------------------------------
# Students: see all, suspend / activate
# ---------------------------------------------------------------
@bp.route("/users")
@role_required("admin")
def users():
    search = request.args.get("search", "").strip()

    sql = "SELECT * FROM admin_users_overview WHERE 1 = 1"
    params = []
    if search:
        sql += " AND (full_name LIKE %s OR email LIKE %s)"
        params += [f"%{search}%"] * 2
    sql += " ORDER BY created_at DESC, user_id DESC"

    return render_template("admin_users.html", users=fetch_all(sql, params), search=search)


@bp.route("/users/<int:user_id>/toggle", methods=["POST"])
@role_required("admin")
def toggle_user(user_id):
    user = fetch_one("SELECT * FROM users WHERE user_id = %s", (user_id,))

    if not user:
        flash("User not found.", "danger")
    elif user["role"] == "admin":
        flash("Admin accounts cannot be suspended.", "danger")
    else:
        execute("UPDATE users SET is_active = 1 - is_active WHERE user_id = %s", (user_id,))
        state = "activated" if not user["is_active"] else "suspended"
        flash(f"{user['full_name']} was {state}.", "success")

    return redirect(url_for("admin.users"))


# ---------------------------------------------------------------
# Moderation log
# ---------------------------------------------------------------
@bp.route("/log")
@role_required("admin")
def log():
    rows = fetch_all("""
        SELECT m.log_id, m.listing_title, m.reason, m.orders_removed, m.created_at,
               a.full_name AS admin, s.full_name AS seller
        FROM moderation_log m
        LEFT JOIN users a ON m.admin_id  = a.user_id
        LEFT JOIN users s ON m.seller_id = s.user_id
        ORDER BY m.created_at DESC, m.log_id DESC
    """)
    return render_template("admin_log.html", log=rows)
