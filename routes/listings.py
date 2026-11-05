"""
routes/listings.py - everything about listings:
  - listing details page (everyone)
  - seller dashboard: add / edit / delete own listings
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from mysql.connector import errors

from db import fetch_all, fetch_one, execute
from auth import role_required

bp = Blueprint("listings", __name__)


def get_own_listing(listing_id):
    """Return the listing only if it belongs to the logged-in seller."""
    return fetch_one(
        "SELECT * FROM listings WHERE listing_id = %s AND seller_id = %s",
        (listing_id, session["user_id"]),
    )


def read_listing_form():
    """Read + validate the add/edit form. Returns (data, error)."""
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    item_type = request.form.get("item_type", "")
    category_id = request.form.get("category_id", "") or None
    status = request.form.get("status", "available")

    try:
        price = round(float(request.form.get("price", "")), 2)
    except ValueError:
        return None, "Price must be a number."

    if not title:
        return None, "Title is required."
    if price < 0:
        return None, "Price cannot be negative."
    if item_type not in ("product", "service"):
        return None, "Choose product or service."
    if status not in ("available", "sold"):
        status = "available"

    data = (title, description or None, price, item_type, category_id, status)
    return data, None


# ---------------------------------------------------------------
# Public: listing details
# ---------------------------------------------------------------
@bp.route("/listing/<int:listing_id>")
def detail(listing_id):
    listing = fetch_one(
        """
        SELECT l.*, c.name AS category, u.full_name AS seller, u.phone AS seller_phone
        FROM listings l
        JOIN users u           ON l.seller_id = u.user_id
        LEFT JOIN categories c ON l.category_id = c.category_id
        WHERE l.listing_id = %s
        """,
        (listing_id,),
    )
    if not listing:
        flash("Listing not found.", "danger")
        return redirect(url_for("index"))

    # Can the current user order it? And did he already order it?
    can_order = False
    already_ordered = False
    uid = session.get("user_id")
    if uid and session.get("role") in ("user", "seller") \
            and listing["seller_id"] != uid and listing["status"] == "available":
        can_order = True
        already_ordered = fetch_one(
            "SELECT order_id FROM orders WHERE buyer_id = %s AND listing_id = %s "
            "AND status IN ('pending', 'accepted')",
            (uid, listing_id),
        ) is not None

    return render_template("listing_detail.html", listing=listing,
                           can_order=can_order, already_ordered=already_ordered)


# ---------------------------------------------------------------
# Seller: my listings
# ---------------------------------------------------------------
@bp.route("/seller/listings")
@role_required("seller")
def my_listings():
    listings = fetch_all(
        """
        SELECT l.*, c.name AS category
        FROM listings l
        LEFT JOIN categories c ON l.category_id = c.category_id
        WHERE l.seller_id = %s
        ORDER BY l.created_at DESC
        """,
        (session["user_id"],),
    )
    return render_template("my_listings.html", listings=listings)


@bp.route("/seller/listings/new", methods=["GET", "POST"])
@role_required("seller")
def create():
    categories = fetch_all("SELECT category_id, name FROM categories ORDER BY name")

    if request.method == "POST":
        data, error = read_listing_form()
        if error:
            flash(error, "danger")
            return render_template("listing_form.html", listing=request.form,
                                   categories=categories, editing=False)

        title, description, price, item_type, category_id, status = data
        execute(
            "INSERT INTO listings (seller_id, category_id, title, description, price, item_type) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (session["user_id"], category_id, title, description, price, item_type),
        )
        flash("Listing added.", "success")
        return redirect(url_for("listings.my_listings"))

    return render_template("listing_form.html", listing={}, categories=categories, editing=False)


@bp.route("/seller/listings/<int:listing_id>/edit", methods=["GET", "POST"])
@role_required("seller")
def edit(listing_id):
    listing = get_own_listing(listing_id)
    if not listing:
        flash("Listing not found.", "danger")
        return redirect(url_for("listings.my_listings"))

    categories = fetch_all("SELECT category_id, name FROM categories ORDER BY name")

    if request.method == "POST":
        data, error = read_listing_form()
        if error:
            flash(error, "danger")
            return render_template("listing_form.html", listing=request.form,
                                   categories=categories, editing=True, listing_id=listing_id)

        title, description, price, item_type, category_id, status = data
        execute(
            "UPDATE listings SET title=%s, description=%s, price=%s, item_type=%s, "
            "category_id=%s, status=%s WHERE listing_id=%s AND seller_id=%s",
            (title, description, price, item_type, category_id, status,
             listing_id, session["user_id"]),
        )
        flash("Listing updated.", "success")
        return redirect(url_for("listings.my_listings"))

    return render_template("listing_form.html", listing=listing, categories=categories,
                           editing=True, listing_id=listing_id)


@bp.route("/seller/listings/<int:listing_id>/delete", methods=["POST"])
@role_required("seller")
def delete(listing_id):
    if not get_own_listing(listing_id):
        flash("Listing not found.", "danger")
        return redirect(url_for("listings.my_listings"))

    try:
        execute("DELETE FROM listings WHERE listing_id = %s", (listing_id,))
        flash("Listing deleted.", "info")
    except errors.IntegrityError:
        # ON DELETE RESTRICT in the database blocked the delete (the listing has orders)
        flash("Cannot delete: this listing has orders. Mark it as 'sold' instead.", "danger")

    return redirect(url_for("listings.my_listings"))