from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import Product
from flask_restx import Api, Resource, fields

# 创建 products 蓝图
products_bp = Blueprint('products', __name__)
api = Api(products_bp)

# 定义商品模型
product_model = api.model('Product', {
    'id': fields.Integer(description='商品ID'),
    'name': fields.String(description='商品名称'),
    'description': fields.String(description='商品描述'),
    'price': fields.Float(description='商品价格'),
    'stock': fields.Integer(description='商品库存'),
    'category': fields.String(description='商品分类'),
})

# 展示所有商品或搜索商品
@api.route('/products')
class Products(Resource):
    @jwt_required()
    def get(self):
        """展示所有商品或按条件搜索商品"""
        query = Product.query

        # 获取查询参数
        name = request.args.get('name')
        category = request.args.get('category')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)

        # 根据查询参数进行筛选
        if name:
            query = query.filter(Product.name.ilike(f'%{name}%'))  # 模糊匹配商品名称
        if category:
            query = query.filter(Product.category.ilike(f'%{category}%'))  # 按类别筛选
        if min_price is not None:
            query = query.filter(Product.price >= min_price)  # 按最小价格筛选
        if max_price is not None:
            query = query.filter(Product.price <= max_price)  # 按最大价格筛选

        # 获取商品列表
        products = query.all()

        return api.marshal(products, product_model), 200

# 查询单个商品详情
@api.route('/products/<int:product_id>')
class ProductDetail(Resource):
    @jwt_required()
    def get(self, product_id):
        """查询单个商品的详细信息"""
        product = Product.query.get(product_id)

        if not product:
            return jsonify({"message": "商品未找到"}), 404

        return api.marshal(product, product_model), 200
