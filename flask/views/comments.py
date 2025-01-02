from flask import Blueprint, jsonify, request
from flask_restx import Namespace, Resource, fields, abort
from .utils import get_db_connection

# 创建 Blueprint
comments_bp = Blueprint('comments', __name__, url_prefix='/comments')

# 创建 Api Namespace
api = Namespace('comments', description='Comments related operations')

# 定义请求和响应模型
comment_model = api.model('Comment', {
    'id': fields.Integer(required=False, description='The comment ID'),
    'content': fields.String(required=True, description='The content of the comment'),
    'comment_date': fields.String(required=False, description='The date when the comment was posted')
})

# 获取评论列表接口
@api.route('/')
class CommentsList(Resource):
    @api.doc('get_comments')
    @api.marshal_list_with(comment_model)
    def get(self):
        """获取评论列表"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM comments LIMIT 5')
            comments = cursor.fetchall()
            conn.close()

            if not comments:
                api.abort(404, "No comments found")
            return [dict(row) for row in comments]

        except Exception as e:
            api.abort(500, f"An error occurred: {str(e)}")

# 删除评论接口
@api.route('/delete')
class CommentDelete(Resource):
    @api.doc('delete_comment')
    @api.expect(comment_model)
    def post(self):
        """删除评论接口"""
        try:
            data = request.get_json()

            id = data.get('id')
            content = data.get('content')
            comment_date = data.get('comment_date')

            conn = get_db_connection()
            cursor = conn.cursor()

            query = "DELETE FROM comments WHERE 1 = 1"
            params = []

            if id:
                query += " AND id = ?"
                params.append(id)
            if content:
                query += " AND content = ?"
                params.append(content)
            if comment_date:
                query += " AND comment_date = ?"
                params.append(comment_date)

            cursor.execute(query, params)
            conn.commit()  # 提交事务

            # Fetch the updated list of comments after deletion
            query_select_all = "SELECT * FROM comments"
            cursor.execute(query_select_all)
            rows = cursor.fetchall()

            conn.close()

            results = [dict(row) for row in rows]
            if not results:
                return jsonify({'error': 'No comments found matching the criteria'}), 404
            else:
                return jsonify(results), 200
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            return jsonify({'error': error_message}), 500

# 将这个 Namespace 注册到 Flask 应用的 Api 实例中
comments_bp.api = api
