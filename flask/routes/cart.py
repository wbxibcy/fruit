from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import CartItem, Product, User
from flask_restx import Api, Resource, fields
from models import db

# 创建 cart 蓝图
cart_bp = Blueprint('cart', __name__)
api = Api(cart_bp)

# 定义购物车项模型
cart_item_model = api.model('CartItem', {
    'product_id': fields.Integer(description='商品ID'),
    'product_name': fields.String(description='商品名称'),
    'quantity': fields.Integer(description='商品数量'),
    'price': fields.Float(description='商品价格'),
    'total_price': fields.Float(description='商品总价'),
})

# 获取购物车内容
@api.route('/cart')
class Cart(Resource):
    @jwt_required()
    def get(self):
        """获取用户购物车内容"""
        current_user_id = get_jwt_identity()
        print(current_user_id)

        cart_items = CartItem.query.filter_by(user_id=current_user_id).all()
        print(cart_items)

        if not cart_items:
            return jsonify({"message": "购物车为空"})

        cart_data = [{
            'product_id': item.product.id,
            'product_name': item.product.name,
            'quantity': item.quantity,
            'price': item.product.price,
            'total_price': item.quantity * item.product.price
        } for item in cart_items]

        return jsonify(cart_data)

# 添加商品到购物车
@api.route('/cart')
class AddToCart(Resource):
    @jwt_required()
    def post(self):
        """将商品添加到购物车"""
        current_user_id = get_jwt_identity()
        product_id = request.json.get('product_id')
        quantity = request.json.get('quantity', 1)

        if not product_id or quantity <= 0:
            return jsonify({"message": "无效的商品ID或数量"})

        product = Product.query.get(product_id)

        if not product:
            return jsonify({"message": "商品未找到"})

        existing_item = CartItem.query.filter_by(user_id=current_user_id, product_id=product_id).first()

        if existing_item:
            existing_item.quantity = quantity
        else:
            new_cart_item = CartItem(user_id=current_user_id, product_id=product_id, quantity=quantity)
            db.session.add(new_cart_item)

        db.session.commit()

        return jsonify({"message": "商品已添加到购物车"})