from flask import Flask
from flask_restx import Api
from views import init_app

app = Flask(__name__)

# 初始化蓝图和 API
api = Api(app, version='1.0', title='My API', description='A simple Flask API with Swagger UI')

init_app(app, api)

if __name__ == '__main__':
    app.run(debug=True)
