from flask import Flask
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    from app.routes import main, lending, stable_pool, non_stable_pool
    app.register_blueprint(main.bp)
    app.register_blueprint(lending.bp)
    app.register_blueprint(stable_pool.bp)
    app.register_blueprint(non_stable_pool.bp)

    return app