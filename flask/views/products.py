from flask import Blueprint, jsonify, request
from flask_restx import Namespace, Resource, fields, abort
from .utils import get_db_connection

# 创建 Blueprint
products_bp = Blueprint('products', __name__, url_prefix='/products')

# 创建 Api Namespace
api = Namespace('products', description='Products related operations')

# 定义请求和响应模型
product_model = api.model('Product', {
    'id': fields.Integer(required=False, description='The product ID'),
    'name': fields.String(required=True, description='The product name'),
    'description': fields.String(required=True, description='The product description'),
    'price': fields.Float(required=True, description='The product price'),
    'image': fields.String(required=True, description='The product image URL')
})

# 获取商品信息接口
@api.route('/select')
class ProductList(Resource):
    @api.doc('get_products')
    @api.marshal_list_with(product_model)
    def get(self):
        """获取商品列表"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM products LIMIT 20')
            products = cursor.fetchall()
            conn.close()

            if not products:
                api.abort(404, "No products found")
            return [dict(row) for row in products]

        except Exception as e:
            api.abort(500, f"An error occurred: {str(e)}")

# 删除商品接口
@api.route('/delete')
class ProductDelete(Resource):
    @api.doc('delete_product')
    @api.expect(product_model)
    def post(self):
        """删除商品接口"""
        try:
            data = request.get_json()

            id = data.get('id')

            conn = get_db_connection()
            cursor = conn.cursor()

            query = "DELETE FROM products WHERE 1 = 1"
            params = []

            if id:
                query += " AND id = ?"
                params.append(id)

            cursor.execute(query, params)
            conn.commit()

            query_select_all = "SELECT * FROM products"
            cursor.execute(query_select_all)
            rows = cursor.fetchall()

            conn.close()

            results = [dict(row) for row in rows]
            if not results:
                return jsonify({'error': 'No products found matching the criteria'}), 404
            else:
                return jsonify(results), 200
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            return jsonify({'error': error_message}), 500

# 增加商品接口
@api.route('/add')
class ProductAdd(Resource):
    @api.doc('add_product')
    @api.expect(product_model)
    def post(self):
        """增加商品接口"""
        try:
            data = request.get_json()

            name = data.get('name')
            description = data.get('description')
            price = data.get('price')
            image = data.get('image')

            conn = get_db_connection()
            cursor = conn.cursor()

            query_insert = "INSERT INTO products (name, description, price, image) VALUES (?, ?, ?, ?)"
            params = (name, description, price, image)

            cursor.execute(query_insert, params)
            conn.commit()  # 提交事务

            query_select_all = "SELECT * FROM products"
            cursor.execute(query_select_all)
            rows = cursor.fetchall()

            conn.close()

            results = [dict(row) for row in rows]
            if not results:
                return jsonify({'error': 'No products found matching the criteria'}), 404
            else:
                return jsonify(results), 200
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            return jsonify({'error': error_message}), 500

# 更新商品信息接口
@api.route('/update')
class ProductUpdate(Resource):
    @api.doc('update_product')
    @api.expect(product_model)
    def put(self):
        """更新商品接口"""
        try:
            data = request.get_json()

            product_id = data.get('id')
            name = data.get('name')
            description = data.get('description')
            price = data.get('price')
            image = data.get('image')

            conn = get_db_connection()
            cursor = conn.cursor()

            query_update = "UPDATE products SET name=?, description=?, price=?, image=? WHERE id=?"
            params = (name, description, price, image, product_id)

            cursor.execute(query_update, params)
            conn.commit()

            query_select_all = "SELECT * FROM products"
            cursor.execute(query_select_all)
            rows = cursor.fetchall()

            conn.close()

            results = [dict(row) for row in rows]
            if not results:
                return jsonify({'error': 'No products found'}), 404
            else:
                return jsonify(results), 200
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            return jsonify({'error': error_message}), 500

# 获取商品图片接口
@api.route('/image')
class ProductImage(Resource):
    @api.doc('get_product_image')
    def get(self):
        """获取商品图片"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT image FROM products WHERE id = 1')
            products = cursor.fetchall()
            conn.close()

            if not products:
                api.abort(404, "No product found with ID 1")
            return jsonify([dict(row) for row in products]), 200
        except Exception as e:
            api.abort(500, f"An error occurred: {str(e)}")

# 将这个 Namespace 注册到 Flask 应用的 Api 实例中
products_bp.api = api
