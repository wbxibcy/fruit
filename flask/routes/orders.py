from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Order, CartItem, OrderItem, Product, User, Payment
from models import db
from alipay import AliPay

# 创建订单蓝图
orders_bp = Blueprint('orders', __name__)

# 创建订单
@orders_bp.route('/orders', methods=['POST'])
@jwt_required()  # JWT 保护，确保用户登录后才能访问
def create_order():
    """根据购物车内容创建订单"""
    current_user_id = get_jwt_identity()

    # 获取当前用户的购物车内容
    cart_items = CartItem.query.filter_by(user_id=current_user_id).all()

    if not cart_items:
        return jsonify({"message": "购物车为空，无法创建订单"})

    # 计算总价并生成订单项
    total_price = 0
    order_items = []

    for item in cart_items:
        product = item.product
        if product.stock < item.quantity:
            return jsonify({"message": f"商品 {product.name} 库存不足"})
        total_price += product.price * item.quantity
        order_items.append({
            'product_id': product.id,
            'quantity': item.quantity,
            'price': product.price
        })

    # 创建订单
    order = Order(user_id=current_user_id, total_price=total_price, status='Pending')
    db.session.add(order)
    db.session.commit()

    # 创建订单项
    for order_item in order_items:
        order_item_obj = OrderItem(order_id=order.id, **order_item)
        db.session.add(order_item_obj)

    # 清空购物车
    CartItem.query.filter_by(user_id=current_user_id).delete()

    db.session.commit()

    return jsonify({"message": "订单创建成功", "order_id": order.id})


# 查看订单列表
@orders_bp.route('/orders', methods=['GET'])
@jwt_required()  # JWT 保护，确保用户登录后才能访问
def get_orders():
    """获取当前用户的所有订单"""
    current_user_id = get_jwt_identity()  # 获取当前登录的用户 ID

    # 获取当前用户的所有订单
    orders = Order.query.filter_by(user_id=current_user_id).all()

    if not orders:
        return jsonify({"message": "没有找到任何订单"})

    # 返回订单列表
    order_data = [{
        'order_id': order.id,
        'status': order.status,
        'total_price': order.total_price,
        'created_at': order.created_at,
        'updated_at': order.updated_at
    } for order in orders]

    return jsonify(order_data)


# 查看订单详情
@orders_bp.route('/orders/<int:order_id>', methods=['GET'])
@jwt_required()  # JWT 保护，确保用户登录后才能访问
def get_order_details(order_id):
    """查看指定订单的详细内容"""
    current_user_id = get_jwt_identity()  # 获取当前登录的用户 ID
    current_user_id = int(current_user_id)
    print(current_user_id)

    # 查找指定订单
    order = Order.query.get(order_id)
    print(type(order.user_id))

    if not order:
        return jsonify({"message": "订单未找到"})

    if order.user_id != current_user_id:
        return jsonify({"message": "无法查看其他用户的订单"})

    # 获取订单项
    order_items = OrderItem.query.filter_by(order_id=order.id).all()

    order_data = {
        'order_id': order.id,
        'status': order.status,
        'total_price': order.total_price,
        'created_at': order.created_at,
        'updated_at': order.updated_at,
        'items': [{
            'product_name': item.product.name,
            'quantity': item.quantity,
            'price': item.price,
            'total_price': item.quantity * item.price
        } for item in order_items]
    }

    return jsonify(order_data)


# 取消订单
@orders_bp.route('/orders/<int:order_id>', methods=['DELETE'])
@jwt_required()  # JWT 保护，确保用户登录后才能访问
def cancel_order(order_id):
    """取消指定订单"""
    current_user_id = get_jwt_identity()  # 获取当前登录的用户 ID
    current_user_id = int(current_user_id)

    # 查找指定订单
    order = Order.query.get(order_id)

    if not order:
        return jsonify({"message": "订单未找到"})

    if order.user_id != current_user_id:
        return jsonify({"message": "无法取消其他用户的订单"})

    if order.status == 'Completed':
        return jsonify({"message": "已支付的订单无法取消"})

    # 更新订单状态为取消
    order.status = 'Cancelled'
    db.session.commit()

    return jsonify({"message": "订单已取消"})


def read_key_from_file(file_path):
    with open(file_path, 'r') as file:
        return file.read().strip()

ALIPAY_APP_ID = '2021000143617934'
ALIPAY_PRIVATE_KEY = read_key_from_file('alipay_private_key.txt')
ALIPAY_PUBLIC_KEY = read_key_from_file('alipay_public_key.txt')
ALIPAY_SANDBOX_URL = 'https://openapi-sandbox.dl.alipaydev.com/gateway.do'

# 支付订单
@orders_bp.route('/orders/<int:order_id>/pay', methods=['POST'])
@jwt_required()  # JWT 保护，确保用户登录后才能访问
def pay_order(order_id):
    """支付订单并更新订单状态"""
    current_user_id = get_jwt_identity()  # 获取当前登录的用户 ID
    current_user_id = int(current_user_id)

    # 查找指定订单
    order = Order.query.get(order_id)
    print(type(order.id))

    if not order:
        return jsonify({"message": "订单未找到"})

    if order.user_id != current_user_id:
        return jsonify({"message": "无法支付其他用户的订单"})

    if order.status == 'Completed':
        return jsonify({"message": "订单已支付"})
    
    alipay = AliPay(
        appid=ALIPAY_APP_ID,
        app_notify_url="https://12f1-2408-843c-4010-47ff-905a-faab-151c-a2bd.ngrok-free.app/orders/pay/notify",
        app_private_key_string=ALIPAY_PRIVATE_KEY,
        alipay_public_key_string=ALIPAY_PUBLIC_KEY,
        sign_type='RSA2',
        debug=True
    )
    
    order_str = alipay.api_alipay_trade_page_pay(
        out_trade_no=str(order.id),  # 订单号
        total_amount=order.total_price,  # 订单总金额
        subject=str(order.id),
        return_url="https://12f1-2408-843c-4010-47ff-905a-faab-151c-a2bd.ngrok-free.app/orders/pay/return",
        notify_url="https://12f1-2408-843c-4010-47ff-905a-faab-151c-a2bd.ngrok-free.app/orders/pay/notify"
    )

    pay_url = f'{ALIPAY_SANDBOX_URL}?{order_str}'
    print(pay_url)

    return jsonify({"pay_url": pay_url})

@orders_bp.route('/pay/return', methods=['GET'])
def pay_return():
    return jsonify({"status": "success", "message": "支付成功"})

@orders_bp.route('/pay/notify', methods=['POST'])
def pay_notify():
    print("Request form:", request.form)
    
    trade_status = request.form.get('trade_status')  # 获取支付状态
    out_trade_no = request.form.get('out_trade_no')  # 获取订单号
    trade_no = request.form.get('trade_no')  # 支付宝交易号
    total_amount = request.form.get('total_amount')  # 订单总金额
    
    print(f"trade_status: {trade_status}, out_trade_no: {out_trade_no}, trade_no: {trade_no}, total_amount: {total_amount}")

    # 校验参数
    if not trade_status or not out_trade_no:
        return jsonify({"status": "failed", "message": "缺少必要参数"})

    # 只处理支付成功的情况
    if trade_status == 'TRADE_SUCCESS':
        # 获取订单并验证
        order = Order.query.filter_by(id=out_trade_no).first()  # 使用订单号查找订单
        if order:
            # 校验金额是否一致
            if float(total_amount) != float(order.total_price):
                return jsonify({"status": "failed", "message": "支付金额不匹配"})
            
            # 更新订单状态为已支付
            order.status = 'Completed'
            db.session.commit()

            # 创建支付记录
            payment = Payment(order_id=order.id, amount=order.total_price, status='Completed')
            db.session.add(payment)
            db.session.commit()

            # 返回成功信息给支付宝
            return jsonify({"status": "success"})
    
    # 支付失败或信息不匹配
    return jsonify({"status": "failed", "message": "支付失败或信息不匹配"})
