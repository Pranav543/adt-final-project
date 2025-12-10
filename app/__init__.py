from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from .models.models import db
import os
from dotenv import load_dotenv

load_dotenv()

migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://localhost/defi_analytics')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Register blueprints
    from .routes import protocols, contracts, users, transactions, market, dashboard
    
    app.register_blueprint(protocols.bp)
    app.register_blueprint(contracts.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(transactions.bp)
    app.register_blueprint(market.bp)
    app.register_blueprint(dashboard.bp)  # NEW
    
    return app
