from flask import Blueprint
from flask_restx import Api

# 导入各个蓝图
from .auth import auth_bp
from .sales import sales_bp
from .comments import comments_bp
from .products import products_bp
from .purchases import purchases_bp

def init_app(app, api: Api):
    # 注册蓝图到 Flask 应用
    app.register_blueprint(auth_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(comments_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(purchases_bp)
    
    # 将每个蓝图的 Namespace 添加到 Api 实例中
    api.add_namespace(auth_bp.api)
    api.add_namespace(sales_bp.api)
    api.add_namespace(comments_bp.api)
    api.add_namespace(products_bp.api)
    api.add_namespace(purchases_bp.api)
