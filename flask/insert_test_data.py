from app import app, db
from models import User, Product, CartItem, Order, OrderItem, Payment
from werkzeug.security import generate_password_hash
from datetime import datetime

# 启动 Flask 应用上下文
with app.app_context():
    # 删除现有的表
    db.drop_all()

    # 创建所有表
    db.create_all()

    # 插入测试数据
    print("开始插入测试数据...")

    # 创建用户
    password_user1 = '654321'
    password_user2 = '123456'

    # 哈希处理密码
    user1 = User(username='switch', password_hash=generate_password_hash(password_user1), email='switch@switch.com')
    user2 = User(username='xixi', password_hash=generate_password_hash(password_user2), email='xixi@xixi.com')
    db.session.add(user1)
    db.session.add(user2)
    db.session.commit()

    # 创建商品
    ps5_product = Product(name='PlayStation 5', description='Sony PlayStation 5 with 1TB SSD', price=4999.0, stock=50, category='Electronics')
    rtx4090_product = Product(name='NVIDIA RTX 4090', description='RTX 4090 GPU with 24GB VRAM', price=15999.0, stock=30, category='Electronics')

    db.session.add(ps5_product)
    db.session.add(rtx4090_product)
    db.session.commit()

    # 创建购物车项
    cart_item1 = CartItem(user_id=user1.id, product_id=ps5_product.id, quantity=1)
    cart_item2 = CartItem(user_id=user1.id, product_id=rtx4090_product.id, quantity=1)
    db.session.add(cart_item1)
    db.session.add(cart_item2)
    db.session.commit()

    # 创建订单
    order1 = Order(user_id=user1.id, total_price=20998.0, status='Pending')
    db.session.add(order1)
    db.session.commit()

    # 创建订单项
    order_item1 = OrderItem(order_id=order1.id, product_id=ps5_product.id, quantity=1, price=ps5_product.price)
    order_item2 = OrderItem(order_id=order1.id, product_id=rtx4090_product.id, quantity=1, price=rtx4090_product.price)
    db.session.add(order_item1)
    db.session.add(order_item2)
    db.session.commit()

    # 创建支付记录
    payment1 = Payment(order_id=order1.id, amount=20998.0, status='Completed')
    db.session.add(payment1)
    db.session.commit()

    print("测试数据插入成功！")
