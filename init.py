from flask import Flask, g, request

from route.user import user_bp
from route.welcome import welcome_bp


def create_app():
    app = Flask(__name__)

    with app.app_context():
        # 注册路由
        app.register_blueprint(welcome_bp)
        app.register_blueprint(user_bp)

    return app
