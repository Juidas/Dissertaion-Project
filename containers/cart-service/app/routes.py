import os
import requests
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

cart_bp = Blueprint('cart', __name__, url_prefix='/cart')


CART = {}

@cart_bp.route('/add', methods=['POST'])
@jwt_required()
def add_to_cart():
    product_service_url = current_app.config["PRODUCT_SERVICE_URL"]
    user = get_jwt_identity()
    data = request.get_json()
    product_id = data.get("product_id")
    quantity = data.get("quantity")

    if not product_id or not quantity:
        return {"message": "product_id and quantity are required"}, 400

    try:
        r = requests.get(product_service_url)
        r.raise_for_status()
        all_products = r.json()
        if not any(p["id"] == product_id for p in all_products):
            return {"message": "Product does not exist"}, 404
    except Exception as e:
        return {"message": f"Error validating product: {str(e)}"}, 500

    CART.setdefault(user, [])

    for item in CART[user]:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            return {"message": "Quantity updated"}, 200

    CART[user].append({"product_id": product_id, "quantity": quantity})
    return {"message": "Item added to cart"}, 201


@cart_bp.route('/', methods=['GET'])
@jwt_required()
def view_cart():
    product_service_url = current_app.config["PRODUCT_SERVICE_URL"]
    user = get_jwt_identity()
    user_cart = CART.get(user, [])

    try:
        r = requests.get(product_service_url)
        r.raise_for_status()
        all_products = r.json()
    except Exception as e:
        return {"message": f"Error fetching product data: {str(e)}"}, 500

    enriched_cart = []
    for item in user_cart:
        product = next((p for p in all_products if p["id"] == item["product_id"]), None)
        if product:
            enriched_cart.append({
                "product_id": item["product_id"],
                "product_name": product["name"],
                "price": product["price"],
                "quantity": item["quantity"]
            })

    return jsonify(enriched_cart)

@cart_bp.route('/remove', methods=['DELETE'])
@jwt_required()
def remove_from_cart():
    user = get_jwt_identity()
    data = request.get_json()
    product_id = data.get("product_id")

    if not product_id:
        return {"message": "product_id required"}, 400

    if user not in CART or not CART[user]:
        return {"message": "Cart is empty"}, 404

    existing = [item for item in CART[user] if item["product_id"] == product_id]
    if not existing:
        return {"message": "Product not found in cart"}, 404

    CART[user] = [item for item in CART[user] if item["product_id"] != product_id]
    return {"message": "Item removed"}, 200

@cart_bp.route('/clear', methods=['POST'])
@jwt_required()
def clear_cart():
    user = get_jwt_identity()
    CART.pop(user, None)
    return {"message": "Cart cleared"}, 200
