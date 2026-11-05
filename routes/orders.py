"""
routes/orders.py - everything about orders:
  - buyer: place an order, see my orders, cancel a pending order
  - seller: see received orders, accept / complete / reject them
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from db import fetch_all, fetch_one, execute
from auth import login_required, role_required

bp = Blueprint("orders", __name__)

# Allowed status changes: current status -> statuses the seller can move to
SELLER_TRANSITIONS = {
    "pending":  ("accepted", "cancelled"),
    "accepted": ("completed", "cancelled"),
}


# ---------------------------------------------------------------
# Buyer
# ---------------------------------------------------------------
@bp.route("/order/<int:listing_id>", methods=["POST"])
@role_required("user", "seller")
def create(listing_id):
    listing = fetch_one("SELECT * FROM listings WHERE listing_id = %s", (listing_id,))
    uid = session["user_id"]

    if not listing:
        flash("Listing not found.", "danger")
        return redirect(url_for("index"))
    if listing["seller_id"] == uid:
        flash("You cannot order your own listing.", "danger")
    elif listing["status"] != "available":
        flash("This listing is no longer available.", "danger")
    elif fetch_one(
        "SELECT order_id FROM orders WHERE buyer_id = %s AND listing_id = %s "
        "AND status IN ('pending', 'accepted')", (uid, listing_id)):
        flash("You already have an active order for this listing.", "warning")
    else:
        execute("INSERT INTO orders (buyer_id, listing_id) VALUES (%s, %s)", (uid, listing_id))
        flash("Order sent! The seller will review it.", "success")
        return redirect(url_for("orders.my_orders"))

    return redirect(url_for("listings.detail", listing_id=listing_id))


@bp.route("/my-orders")
@login_required
def my_orders():
    orders = fetch_all(
        """
        SELECT o.order_id, o.status, o.created_at,
               l.listing_id, l.title, l.price,
               u.full_name AS seller, u.phone AS seller_phone
        FROM orders o
        JOIN listings l ON o.listing_id = l.listing_id
        JOIN users u    ON l.seller_id = u.user_id
        WHERE o.buyer_id = %s
        ORDER BY o.created_at DESC
        """,
        (session["user_id"],),
    )
    return render_template("my_orders.html", orders=orders)


@bp.route("/my-orders/<int:order_id>/cancel", methods=["POST"])
@login_required
def cancel(order_id):
    order = fetch_one(
        "SELECT * FROM orders WHERE order_id = %s AND buyer_id = %s",
        (order_id, session["user_id"]),
    )
    if order and order["status"] == "pending":
        execute("UPDATE orders SET status = 'cancelled' WHERE order_id = %s", (order_id,))
        flash("Order cancelled.", "info")
    else:
        flash("This order cannot be cancelled.", "danger")
    return redirect(url_for("orders.my_orders"))


# ---------------------------------------------------------------
# Seller
# ---------------------------------------------------------------
@bp.route("/seller/orders")
@role_required("seller")
def seller_orders():
    orders = fetch_all(
        """
        SELECT o.order_id, o.status, o.created_at,
               l.title, l.price,
               u.full_name AS buyer, u.phone AS buyer_phone
        FROM orders o
        JOIN listings l ON o.listing_id = l.listing_id
        JOIN users u    ON o.buyer_id = u.user_id
        WHERE l.seller_id = %s
        ORDER BY o.created_at DESC
        """,
        (session["user_id"],),
    )
    return render_template("seller_orders.html", orders=orders)


@bp.route("/seller/orders/<int:order_id>/status", methods=["POST"])
@role_required("seller")
def update_status(order_id):
    new_status = request.form.get("status", "")

    # Make sure this order belongs to one of MY listings
    order = fetch_one(
        """
        SELECT o.order_id, o.status, o.listing_id
        FROM orders o
        JOIN listings l ON o.listing_id = l.listing_id
        WHERE o.order_id = %s AND l.seller_id = %s
        """,
        (order_id, session["user_id"]),
    )

    if not order:
        flash("Order not found.", "danger")
    elif new_status not in SELLER_TRANSITIONS.get(order["status"], ()):
        flash("This status change is not allowed.", "danger")
    else:
        execute("UPDATE orders SET status = %s WHERE order_id = %s", (new_status, order_id))
        if new_status == "completed":
            # A completed order means the item is sold
            execute("UPDATE listings SET status = 'sold' WHERE listing_id = %s",
                    (order["listing_id"],))
        flash(f"Order marked as {new_status}.", "success")

    return redirect(url_for("orders.seller_orders"))