from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import User
from flask_restx import Api, Resource, fields

# 创建 auth 蓝图
auth_bp = Blueprint('auth', __name__)
api = Api(auth_bp)

login_model = api.model('Login', {
    'username': fields.String(required=True, description='用户名'),
    'password': fields.String(required=True, description='密码')
})

user_model = api.model('User', {
    'username': fields.String(description='用户名'),
    'email': fields.String(description='邮箱'),
})

# 用户登录接口
@api.route('/login')
class Login(Resource):
    @api.expect(login_model)
    def post(self):
        """用户登录并返回 JWT token"""
        data = request.get_json()
        username = data['username']
        password = data['password']
        print(username, password)

        # 查找用户
        user = User.query.filter_by(username=username).first()
        print(user)
        print(check_password_hash(user.password_hash, password))
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({"message": "用户名或密码错误",
                            "status": 401})

        # 创建 JWT Token
        access_token = create_access_token(identity=str(user.id))
        print(access_token)

        return jsonify({"access_token": access_token,
                        "status": 200})

# 获取当前用户信息
@api.route('/user')
class UserInfo(Resource):
    @jwt_required()
    def get(self):
        """获取当前登录用户的信息"""
        current_user_id = get_jwt_identity()
        print(current_user_id)
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({"message": "用户未找到",
                            "status": 404})

        return jsonify(api.marshal(user, user_model))
