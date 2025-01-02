from flask import Blueprint, jsonify
from flask_restx import Namespace, Resource, fields, abort
from .utils import get_db_connection

# 创建 Blueprint
sales_bp = Blueprint('sales', __name__, url_prefix='/sales')

# 创建 Api Namespace
api = Namespace('sales', description='Sales related operations')

# 定义响应模型
sale_model = api.model('Sale', {
    'sales_date': fields.String(required=True, description='The date of sale'),
    'amount': fields.Float(required=True, description='The amount of the sale')
})

# 获取销售数据接口
@api.route('')
class SaleList(Resource):
    @api.doc('get_sales')
    @api.marshal_list_with(sale_model)
    def get(self):
        """获取销售记录列表"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT sales_date, amount FROM sales LIMIT 30')
            sales = cursor.fetchall()
            conn.close()

            if not sales:
                api.abort(404, "No sales records found")
            return [dict(row) for row in sales]

        except Exception as e:
            api.abort(500, f"An error occurred: {str(e)}")

# 将这个 Namespace 注册到 Flask 应用的 Api 实例中
sales_bp.api = api
