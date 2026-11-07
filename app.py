"""
app.py - the main file. Starts the website and defines the pages (routes).
Run it with:  python app.py
"""
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
import os

from db import fetch_all, fetch_one, execute
from auth import ALLOWED_EMAIL_DOMAIN
from routes import listings, orders, admin

app = Flask(__name__)
app.secret_key = "change-this-secret-key"   # needed for login sessions

# Register the other route files (blueprints)
app.register_blueprint(listings.bp)
app.register_blueprint(orders.bp)
app.register_blueprint(admin.bp)

# Serve images from imeg folder
@app.route('/imeg/<path:filename>')
def serve_image(filename):
    return send_from_directory(os.path.join(os.path.dirname(__file__), 'imeg'), filename)


# Get image path based on listing title
def get_listing_image(title):
    """Return the image path for a listing based on its title."""
    if not title:
        return '/imeg/University logo.png'
    
    title_lower = title.lower()
    
    # Map of keywords to image filenames
    image_mapping = {
        'data structures book': '/imeg/Data Structures Book.jpeg',
        'data structures': '/imeg/Data Structures Book.jpeg',
        'book': '/imeg/Data Structures Book.jpeg',
        'pens pack': '/imeg/Pens Pack (10 pieces).svg',
        'pens': '/imeg/Pens Pack (10 pieces).svg',
        'programming tutoring': '/imeg/Programming Tutoring.svg',
        'tutoring': '/imeg/Programming Tutoring.svg',
        'programming': '/imeg/Programming Tutoring.svg',
        'scientific calculator': '/imeg/Scientific Calculator.svg',
        'calculator': '/imeg/Scientific Calculator.svg',
        'usb flash drive': '/imeg/USB Flash Drive 64GB.svg',
        'usb': '/imeg/USB Flash Drive 64GB.svg',
        'flash drive': '/imeg/USB Flash Drive 64GB.svg',
    }
    
    # Check for matching keywords
    for keyword, image_path in image_mapping.items():
        if keyword in title_lower:
            return image_path
    
    # Default to university logo if no match
    return '/imeg/University logo.png'


# Language switching
@app.route('/set_language/<lang>')
def set_language(lang):
    if lang in ['ar', 'en']:
        session['lang'] = lang
    return redirect(request.referrer or url_for('index'))


# Translation dictionary
TRANSLATIONS = {
    'ar': {
        'site_title': 'UOM Market',
        'admin_panel': 'لوحة الأدمن',
        'available_listings': 'الإعلانات المتاحة',
        'browse_listings': 'شوف اللي يبيعه طلاب الجامعة',
        'search_placeholder': 'ابحث عن الشي...',
        'all_categories': 'كل التصنيفات',
        'search_button': 'بحث',
        'no_listings': 'ما فيه إعلانات',
        'try_filters': 'جرب تغير البحث أو الفلتر',
        'view_details': 'التفاصيل',
        'my_orders': 'طلباتي',
        'my_listings': 'إعلاناتي',
        'received_orders': 'الطلبات الواردة',
        'logout': 'خروج',
        'login': 'دخول',
        'register': 'تسجيل',
        'welcome_back': 'أهلاً مره ثانية 👋',
        'login_subtitle': 'سجل دخولك عشان تكمل',
        'university_email': 'ايميل الجامعة',
        'password': 'كلمة السر',
        'no_account': 'ما عندك حساب؟',
        'register_here': 'سجل حساب جديد',
        'create_account': 'سجل حساب جديد 🎓',
        'join_marketplace': 'انضم لسوق جامعة المستقبل',
        'full_name': 'الاسم الكامل',
        'phone': 'الجوال (اختياري)',
        'confirm_password': 'تأكيد كلمة السر',
        'account_type': 'نوع الحساب',
        'buyer_option': 'مشتري (تشوف وتشتري)',
        'seller_option': 'بائع (تبيع وتعرض)',
        'register_button': 'سجل',
        'have_account': 'عندك حساب بالفعل؟',
        'login_here': 'سجل دخولك',
        'back_to_listings': 'رجوع للإعلانات',
        'description': 'الوصف',
        'seller': 'البائع',
        'posted_date': 'تاريخ النشر',
        'order_now': 'اطلب الآن',
        'already_ordered': 'طلبت هذا الشي من قبل',
        'view_my_orders': 'شوف طلباتي',
        'login_to_order': 'سجل دخول عشان تطلب',
        'item_sold': 'هذا الشي تم بيعه',
        'add_listing': '+ أضف إعلان',
        'title': 'العنوان',
        'price': 'السعر',
        'type': 'النوع',
        'category': 'التصنيف',
        'status': 'الحالة',
        'save': 'حفظ',
        'cancel': 'إلغاء',
        'product': 'منتج',
        'service': 'خدمة',
        'no_category': 'بدون تصنيف',
        'available': 'متاح',
        'sold': 'تم البيع',
        'edit': 'تعديل',
        'delete': 'حذف',
        'delete_confirm': 'متأكد تريد حذف هذا الإعلان؟',
        'no_listings_yet': 'ما عندك إعلانات بعد',
        'item': 'المنتج',
        'date': 'التاريخ',
        'action': 'إجراء',
        'cancel_order': 'إلغاء',
        'cancel_order_confirm': 'متأكد تريد إلغاء هذا الطلب؟',
        'no_orders_yet': 'ما عندك طلبات بعد',
        'buyer': 'المشتري',
        'actions': 'إجراءات',
        'accept': 'قبول',
        'reject': 'رفض',
        'complete': 'إكمال',
        'no_orders_received': 'ما فيه طلبات واردة بعد',
        'no_description': 'ما فيه وصف',
        'footer': 'سوق جامعة المستقبل - مشروع قاعدة بيانات CS340',
        'demo_accounts': 'حسابات تجريبية للتجربة:',
        'admin_account': 'أدمن: admin@student.edu.sa / 123456',
        'seller_account': 'بائع: ahmed@student.edu.sa / 123456',
        'buyer_account': 'مشتري: sara@student.edu.sa / 123456',
    },
    'en': {
        'site_title': 'UOM Market',
        'admin_panel': 'Admin Panel',
        'available_listings': 'Available Listings',
        'browse_listings': 'Browse through amazing products and services',
        'search_placeholder': 'Search by title...',
        'all_categories': 'All categories',
        'search_button': 'Search',
        'no_listings': 'No listings found',
        'try_filters': 'Try adjusting your search or filters',
        'view_details': 'View Details',
        'my_orders': 'My Orders',
        'my_listings': 'My Listings',
        'received_orders': 'Received Orders',
        'logout': 'Logout',
        'login': 'Login',
        'register': 'Register',
        'welcome_back': 'Welcome Back! 👋',
        'login_subtitle': 'Login to access your account',
        'university_email': 'University Email',
        'password': 'Password',
        'no_account': "Don't have an account?",
        'register_here': 'Register here',
        'create_account': 'Create Account 🎓',
        'join_marketplace': 'Join our university marketplace',
        'full_name': 'Full Name',
        'phone': 'Phone (optional)',
        'confirm_password': 'Confirm Password',
        'account_type': 'Account Type',
        'buyer_option': 'Buyer (browse and order)',
        'seller_option': 'Seller (post items and services)',
        'register_button': 'Register',
        'have_account': 'Already have an account?',
        'login_here': 'Login here',
        'back_to_listings': 'Back to listings',
        'description': 'Description',
        'seller': 'Seller',
        'posted_date': 'Posted on',
        'order_now': 'Order Now',
        'already_ordered': 'You already ordered this',
        'view_my_orders': 'View my orders',
        'login_to_order': 'Login to Order',
        'item_sold': 'This item has been sold',
        'add_listing': '+ Add listing',
        'title': 'Title',
        'price': 'Price',
        'type': 'Type',
        'category': 'Category',
        'status': 'Status',
        'save': 'Save',
        'cancel': 'Cancel',
        'product': 'Product',
        'service': 'Service',
        'no_category': 'No category',
        'available': 'Available',
        'sold': 'Sold',
        'edit': 'Edit',
        'delete': 'Delete',
        'delete_confirm': 'Delete this listing?',
        'no_listings_yet': 'You have no listings yet',
        'item': 'Item',
        'date': 'Date',
        'action': 'Action',
        'cancel_order': 'Cancel',
        'cancel_order_confirm': 'Cancel this order?',
        'no_orders_yet': 'You have no orders yet',
        'buyer': 'Buyer',
        'actions': 'Actions',
        'accept': 'Accept',
        'reject': 'Reject',
        'complete': 'Complete',
        'no_orders_received': 'No orders received yet',
        'no_description': 'No description',
        'footer': 'UOM Market - CS340 Database Project',
        'demo_accounts': 'Demo accounts for testing:',
        'admin_account': 'Admin: admin@student.edu.sa / 123456',
        'seller_account': 'Seller: ahmed@student.edu.sa / 123456',
        'buyer_account': 'Buyer: sara@student.edu.sa / 123456',
    }
}


def clear_session_keep_language():
    """Log out / log in without forgetting the language the user chose."""
    lang = session.get("lang")
    session.clear()
    if lang:
        session["lang"] = lang


@app.context_processor
def inject_user():
    """Make 'current_user' available in every template (for the navbar)."""
    lang = session.get('lang', 'ar')
    if "user_id" in session:
        return {
            "current_user": {"name": session["full_name"], "role": session["role"]},
            "lang": lang,
            "t": TRANSLATIONS.get(lang, TRANSLATIONS['ar']),
            "get_listing_image": get_listing_image
        }
    return {
        "current_user": None,
        "lang": lang,
        "t": TRANSLATIONS.get(lang, TRANSLATIONS['ar']),
        "get_listing_image": get_listing_image
    }


# ---------------------------------------------------------------
# Home page
# ---------------------------------------------------------------
@app.route("/")
def index():
    """Home page: shows available listings with search + category filter."""
    search = request.args.get("search", "").strip()
    category_id = request.args.get("category", "")

    sql = """
        SELECT l.listing_id, l.title, l.price, l.item_type,
               c.name      AS category,
               u.full_name AS seller
        FROM listings l
        JOIN users u            ON l.seller_id = u.user_id
        LEFT JOIN categories c  ON l.category_id = c.category_id
        WHERE l.status = 'available'
          AND u.is_active = 1
    """
    params = []

    if search:
        sql += " AND l.title LIKE %s"
        params.append(f"%{search}%")
    if category_id:
        sql += " AND l.category_id = %s"
        params.append(category_id)

    sql += " ORDER BY l.created_at DESC"

    listings = fetch_all(sql, params)
    categories = fetch_all("SELECT category_id, name FROM categories ORDER BY name")

    return render_template(
        "index.html",
        listings=listings,
        categories=categories,
        search=search,
        selected_category=category_id,
    )


# ---------------------------------------------------------------
# Register / Login / Logout
# ---------------------------------------------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")
        role = request.form.get("role", "user")

        # --- validation ---
        error = None
        if not full_name or not email or not password:
            error = "Name, email and password are required."
        elif not email.endswith("@" + ALLOWED_EMAIL_DOMAIN):
            error = f"Only university emails (@{ALLOWED_EMAIL_DOMAIN}) are allowed."
        elif len(password) < 6:
            error = "Password must be at least 6 characters."
        elif password != confirm:
            error = "Passwords do not match."
        elif role not in ("user", "seller"):      # nobody can register as admin
            error = "Invalid account type."
        elif fetch_one("SELECT user_id FROM users WHERE email = %s", (email,)):
            error = "This email is already registered."

        if error:
            flash(error, "danger")
            return render_template("register.html", form=request.form,
                                   domain=ALLOWED_EMAIL_DOMAIN)

        execute(
            "INSERT INTO users (full_name, email, password_hash, phone, role) "
            "VALUES (%s, %s, %s, %s, %s)",
            (full_name, email,
             generate_password_hash(password, method="pbkdf2:sha256"),
             phone or None, role),
        )
        flash("Account created! You can log in now.", "success")
        return redirect(url_for("login"))

    return render_template("register.html", form={}, domain=ALLOWED_EMAIL_DOMAIN)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = fetch_one("SELECT * FROM users WHERE email = %s", (email,))

        if user and check_password_hash(user["password_hash"], password):
            if not user["is_active"]:
                flash("Your account is suspended. Please contact the administration.", "danger")
                return render_template("login.html")
            clear_session_keep_language()
            session["user_id"] = user["user_id"]
            session["full_name"] = user["full_name"]
            session["role"] = user["role"]
            flash(f"Welcome back, {user['full_name']}!", "success")
            return redirect(url_for("admin.listings" if user["role"] == "admin" else "index"))

        flash("Wrong email or password.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    clear_session_keep_language()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)