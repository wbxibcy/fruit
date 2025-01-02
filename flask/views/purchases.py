from flask import Blueprint, jsonify, request
from flask_restx import Namespace, Resource, fields, abort
from .utils import get_db_connection

# 创建 Blueprint
purchases_bp = Blueprint('purchases', __name__, url_prefix='/purchases')

# 创建 Api Namespace
api = Namespace('purchases', description='Purchases related operations')

# 定义请求和响应模型
purchase_model = api.model('Purchase', {
    'id': fields.Integer(required=False, description='The purchase ID'),
    'product_id': fields.Integer(required=True, description='The product ID'),
    'quantity': fields.Integer(required=True, description='The quantity of the product'),
    'purchase_date': fields.String(required=True, description='The date of purchase')
})

# 获取采购信息接口
@api.route('')
class PurchaseList(Resource):
    @api.doc('get_purchases')
    @api.marshal_list_with(purchase_model)
    def get(self):
        """获取采购列表"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM purchases LIMIT 20')
            purchases = cursor.fetchall()
            conn.close()

            if not purchases:
                api.abort(404, "No purchases found")
            return [dict(row) for row in purchases]

        except Exception as e:
            api.abort(500, f"An error occurred: {str(e)}")

# 将这个 Namespace 注册到 Flask 应用的 Api 实例中
purchases_bp.api = api
