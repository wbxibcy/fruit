import click
from flask import Flask
from flask_restx import Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from models import db
from routes.auth import auth_bp
from routes.products import products_bp
from routes.cart import cart_bp
from routes.orders import orders_bp

app = Flask(__name__)
CORS(app)

# 配置应用
app.config.from_object('config.Config')

db.init_app(app)
jwt = JWTManager(app)

# 注册蓝图
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(products_bp, url_prefix='/products')
app.register_blueprint(cart_bp, url_prefix='/cart')
app.register_blueprint(orders_bp, url_prefix='/orders')

# CLI 命令：初始化数据库
@app.cli.command('initdb')
def init_db():
    with app.app_context():
        click.echo("Resetting the database...")

        # 删除所有表
        db.drop_all()

        # 创建所有表
        click.echo("Creating database tables...")
        db.create_all()

        click.echo("Database initialized successfully.")

if __name__ == '__main__':
    app.run(debug=True)
