import os

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 禁用追踪修改，减少开销
    SQLALCHEMY_DATABASE_URI = 'sqlite:///market.db'  # SQLite数据库的URI
    SECRET_KEY = 'market_key'