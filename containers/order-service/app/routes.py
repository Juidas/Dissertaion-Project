import requests
from flask import Blueprint, jsonify, request
from .models import Order, OrderItem
from . import db
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

order_bp = Blueprint('order', __name__, url_prefix='/orders')

@order_bp.route('/checkout', methods=['POST'])
@jwt_required()
def checkout():
    username = get_jwt_identity()

    # 1. Get user's cart from cart-service
    try:
        cart_response = requests.get(
            "http://cart-service:5000/cart/",
            headers={"Authorization": request.headers.get("Authorization")}
        )
        cart_response.raise_for_status()
        cart_items = cart_response.json()
    except Exception as e:
        return {"message": f"Failed to fetch cart: {str(e)}"}, 500

    if not cart_items:
        return {"message": "Cart is empty"}, 400

    total = 0
    validated_items = []

    # 2. Get all products from product-service
    try:
        product_response = requests.get("http://product-service:5000/products/")
        product_response.raise_for_status()
        products = product_response.json()
    except Exception as e:
        return {"message": f"Failed to fetch product data: {str(e)}"}, 500

    product_map = {p['id']: p for p in products}

    for item in cart_items:
        pid = item['product_id']
        qty = item['quantity']
        product = product_map.get(pid)

        if not product:
            return {"message": f"Product ID {pid} not found in catalog"}, 400

        price = product['price']
        total += qty * price

        validated_items.append({
            "product_id": pid,
            "quantity": qty,
            "unit_price": price
        })

    # 3. Save order and items
    new_order = Order(user_name=username, total_amount=total)
    db.session.add(new_order)
    db.session.flush()

    for vi in validated_items:
        db.session.add(OrderItem(
            order_id=new_order.id,
            product_id=vi["product_id"],
            quantity=vi["quantity"],
            unit_price=vi["unit_price"]
        ))

    db.session.commit()

    # 4. Clear the cart
    try:
        clear = requests.post(
            "http://cart-service:5000/cart/clear",
            headers={"Authorization": request.headers.get("Authorization")}
        )
        clear.raise_for_status()
    except Exception as e:
        return {"message": "Order saved but failed to clear cart", "error": str(e)}, 500

    return {"message": "Order placed and cart cleared!"}, 201

@order_bp.route('/', methods=['GET'])
@jwt_required()
def user_orders():
    username = get_jwt_identity()
    orders = Order.query.filter_by(user_name=username).all()

    # Fetch product data
    try:
        product_response = requests.get("http://product-service:5000/products/")
        product_response.raise_for_status()
        products = product_response.json()
    except Exception as e:
        return {"message": f"Failed to fetch product data: {str(e)}"}, 500

    product_map = {p['id']: p['name'] for p in products}

    enriched = []
    for o in orders:
        items = []
        total = 0
        for item in o.items:
            name = product_map.get(item.product_id, f"Product {item.product_id}")
            subtotal = item.unit_price * item.quantity
            total += subtotal
            items.append({
                "product_id": item.product_id,
                "product_name": name,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "subtotal": round(subtotal, 2)
            })

        enriched.append({
            "order_id": o.id,
            "total": round(total, 2),
            "timestamp": o.timestamp,
            "items": items
        })

    return jsonify(enriched)


@order_bp.route('/all', methods=['GET'])
@jwt_required()
def all_orders():
    claims = get_jwt()
    if not claims.get('is_admin', False):
        return {"message": "Admins only!"}, 403

    # Get all products to build a product map
    try:
        product_response = requests.get("http://product-service:5000/products/")
        product_response.raise_for_status()
        products = product_response.json()
    except Exception as e:
        return {"message": f"Failed to fetch product data: {str(e)}"}, 500

    product_map = {p['id']: p['name'] for p in products}

    orders = Order.query.all()
    enriched = []

    for o in orders:
        items = []
        for item in o.items:
            items.append({
                "product_id": item.product_id,
                "product_name": product_map.get(item.product_id, f"Product {item.product_id}"),
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "subtotal": round(item.unit_price * item.quantity, 2)
            })

        enriched.append({
            "id": o.id,
            "user_id": o.user_name,
            "timestamp": o.timestamp,
            "total_amount": round(o.total_amount, 2),
            "items": items
        })

    return jsonify(enriched)