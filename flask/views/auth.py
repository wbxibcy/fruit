from flask import Blueprint, jsonify, request
from flask_restx import Namespace, Resource, fields
from .utils import get_db_connection

# 创建 Blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# 创建 Api Namespace
api = Namespace('auth', description='Authentication operations')

# 定义请求和响应模型
login_model = api.model('Login', {
    'username': fields.String(required=True, description='The user\'s username'),
    'password': fields.String(required=True, description='The user\'s password')
})

# 登录接口
@api.route('/login')
class Login(Resource):
    @api.doc('login')
    @api.expect(login_model)
    def post(self):
        """用户登录接口"""
        try:
            data = request.get_json()

            username = data.get('username')
            password = data.get('password')

            # 检查是否提供了用户名和密码
            if not username or not password:
                return {'error': 'Username and password are required'}, 400

            # 连接数据库并验证用户名和密码
            conn = get_db_connection()
            cursor = conn.cursor()

            # 使用用户名查询数据库
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()
            conn.close()

            # 检查用户是否存在
            if user is None:
                return {'error': 'Invalid username or password'}, 401

            # 比较密码
            if password == user['password']:
                return {'message': 'Login successful', 'user_id': user['id']}, 200
            else:
                return {'error': 'Invalid username or password'}, 401

        except Exception as e:
            # 捕获异常并返回500错误
            return {'error': str(e)}, 500

# 将这个 Namespace 注册到 Flask 应用的 Api 实例中
auth_bp.api = api
