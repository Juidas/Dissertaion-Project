from flask import Blueprint, render_template, request, redirect, url_for, current_app
from flask_login import login_required, current_user
from .models import Product
from . import db

admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.before_request
def restrict_to_admin():
    if not current_user.is_authenticated or not current_user.is_admin:
        current_app.logger.warning(f"403 Forbidden: {current_user.username if current_user.is_authenticated else 'Anonymous'} tried accessing admin panel")
        return render_template('403.html'), 403

@admin.route('/')
@login_required
def dashboard():
    products = Product.query.all()
    current_app.logger.info(f"Admin {current_user.username} accessed the dashboard")
    return render_template('admin/dashboard.html', products=products)

@admin.route('/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        product = Product(name=name, description=description, price=price)
        db.session.add(product)
        db.session.commit()
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/add_product.html')

@admin.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    if request.method == 'POST':
        product.name = request.form['name']
        product.description = request.form['description']
        product.price = float(request.form['price'])
        db.session.commit()
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/edit_product.html', product=product)

@admin.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('admin.dashboard'))
