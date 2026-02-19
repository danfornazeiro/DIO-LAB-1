from decimal import Decimal
from flask import Flask
from flask.json.provider import DefaultJSONProvider
from config import Config
from extensions import db
from routes.products import products_bp
from routes.cart import cart_bp
from routes.orders import orders_bp


class JSONProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.json_provider_class = JSONProvider
    app.json = JSONProvider(app)

    db.init_app(app)

    app.register_blueprint(products_bp, url_prefix="/products")
    app.register_blueprint(cart_bp, url_prefix="/cart")
    app.register_blueprint(orders_bp, url_prefix="/orders")

    with app.app_context():
        db.create_all()

    @app.route("/health")
    def health():
        return {"status": "ok"}, 200

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=app.config.get("DEBUG", False))
