from flask import Blueprint, jsonify, request
from .models import Product
from flask_jwt_extended import jwt_required, get_jwt
from . import db

product_bp = Blueprint('product', __name__, url_prefix='/products')

@product_bp.route('/', methods=['GET'])
def list_products():
    products = Product.query.all()
    return jsonify([
        {"id": p.id, "name": p.name, "description": p.description, "price": p.price}
        for p in products
    ])

@product_bp.route('/', methods=['POST'])
@jwt_required()
def add_product():
    claims = get_jwt()
    if not claims.get('is_admin', False):
        return {"message": "Admins only can add products!"}, 403

    data = request.json
    product = Product(
        name=data['name'],
        description=data.get('description', ''),
        price=float(data['price'])
    )
    db.session.add(product)
    db.session.commit()
    return {"message": "Product added successfully!"}, 201

@product_bp.route("/<int:product_id>", methods=["DELETE", "OPTIONS"])
@jwt_required()
def delete_product(product_id):
    if request.method == "OPTIONS":
        return '', 200

    product = Product.query.get(product_id)
    if not product:
        return jsonify({"message": "Product not found"}), 404

    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted"}), 200
