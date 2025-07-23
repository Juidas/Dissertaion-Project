from flask import Blueprint, render_template, request, redirect, url_for, session, current_app, flash
from flask_login import login_user, logout_user, login_required, current_user
from .models import Product, User, Order, OrderItem
from sqlalchemy import text
from . import db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

@main.route('/cart/add/<int:product_id>', methods=["POST"])
@login_required
def add_to_cart(product_id):
    quantity = int(request.form.get("quantity", 1))
    cart = session.get("cart", [])

    # Check if product already in cart
    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            break
    else:
        cart.append({"product_id": product_id, "quantity": quantity})

    session["cart"] = cart
    flash("Product added to cart", "success")
    return redirect(url_for('main.index'))


@main.route('/cart')
@login_required
def view_cart():
    raw_cart = session.get("cart", [])
    cart = []

    # Force valid structure in case data was corrupted or manually edited
    for item in raw_cart:
        if isinstance(item, dict) and "product_id" in item and "quantity" in item:
            cart.append(item)

    products = Product.query.all()
    product_map = {p.id: p for p in products}
    total = 0

    for item in cart:
        product = product_map.get(item["product_id"])
        if product:
            item["name"] = product.name
            item["price"] = product.price
            item["subtotal"] = product.price * item["quantity"]
            total += item["subtotal"]

    return render_template("cart.html", cart=cart, total=total)

@main.route('/cart/remove/<int:product_id>')
@login_required
def remove_from_cart(product_id):
    cart = session.get("cart", [])
    cart = [item for item in cart if item["product_id"] != product_id]
    session["cart"] = cart
    flash("Item removed from cart", "info")
    return redirect(url_for("main.view_cart"))

@main.route('/cart/checkout', methods=["POST"])
@login_required
def checkout():
    cart = session.get("cart", [])
    if not cart:
        flash("Cart is empty.", "warning")
        return redirect(url_for("main.view_cart"))

    new_order = Order(user_id=current_user.id, total_amount=0)
    db.session.add(new_order)
    db.session.flush()

    total = 0
    for item in cart:
        product = Product.query.get(item["product_id"])
        if not product:
            continue
        subtotal = product.price * item["quantity"]
        total += subtotal
        db.session.add(OrderItem(
            order_id=new_order.id,
            product_id=product.id,
            quantity=item["quantity"],
            unit_price=product.price
        ))

    new_order.total_amount = total
    db.session.commit()
    session["cart"] = []
    flash("Order placed successfully!", "success")
    return redirect(url_for("main.order_history"))

@main.route('/orders')
@login_required
def order_history():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.timestamp.desc()).all()
    return render_template('orders.html', orders=orders)

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('main.register'))

        new_user = User(username=username)
        new_user.set_password(password)  # Uses your User model's method
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('main.index'))

    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            current_app.logger.info(f"User login successful: {username}")
            return redirect(url_for('main.index'))
        else:
            current_app.logger.warning(f"Failed login attempt for username: {username}")
            return 'Invalid username or password', 401

    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@main.route('/profile')
@login_required
def profile():
    return f'Logged in as: {current_user.username}'

@main.route('/vulnerable-search')
def vulnerable_search():
    search_term = request.args.get('q', '')

    if not search_term:
        return '''
        <form method="GET">
            <input name="q" placeholder="Search by product name">
            <button type="submit">Search</button>
        </form>
        '''

    # ⚠️ Vulnerable raw SQL (no parameter binding)
    query = text(f"SELECT * FROM product WHERE name LIKE '%{search_term}%'")
    results = db.session.execute(query).fetchall()

    output = f"<h3>Results for: {search_term}</h3><ul>"
    for row in results:
        output += f"<li>{row.name} - ${row.price}</li>"
    output += "</ul>"

    return output
