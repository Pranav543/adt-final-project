from app import create_app
from app.models.models import db, Protocol, Contract, User, Transaction, MarketData
import os

app = create_app()

@app.cli.command('init-db')
def init_db():
    """Initialize the database"""
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("Database initialized!")

@app.cli.command('load-data')
def load_data():
    """Load data from Parquet files"""
    with app.app_context():
        from app.utils.data_loader import load_all_data
        results = load_all_data('data')
        print(f"Data loaded: {results}")

@app.cli.command('seed-sample')
def seed_sample():
    """Seed sample data for testing visualizations"""
    with app.app_context():
        import random
        from datetime import datetime, timedelta
        
        # Check if protocols exist
        if Protocol.query.count() == 0:
            protocols_data = [
                ('Uniswap', 'UNI', 'DEX'),
                ('Curve DAO', 'CRV', 'DEX'),
                ('Balancer', 'BAL', 'DEX'),
                ('Aave', 'AAVE', 'Lending'),
                ('Maker', 'MKR', 'Lending'),
                ('yearn.finance', 'YFI', 'Yield Farming'),
                ('Harvest Finance', 'FARM', 'Yield Farming'),
                ('USDC', 'USDC', 'Stablecoin'),
                ('Tether', 'USDT', 'Stablecoin'),
                ('Dai', 'DAI', 'Stablecoin'),
            ]
            
            for name, symbol, ptype in protocols_data:
                protocol = Protocol(
                    protocol_name=name,
                    protocol_symbol=symbol,
                    type=ptype,
                    description=f'{name} is a {ptype} protocol'
                )
                db.session.add(protocol)
            
            db.session.commit()
            print("Sample protocols added!")
        
        # Add sample market data
        protocols = Protocol.query.all()
        for protocol in protocols:
            for i in range(30):
                date = datetime.utcnow().date() - timedelta(days=30-i)
                existing = MarketData.query.filter_by(
                    protocol_id=protocol.protocol_id,
                    date=date
                ).first()
                
                if not existing:
                    market = MarketData(
                        protocol_id=protocol.protocol_id,
                        date=date,
                        total_volume=random.uniform(10000, 500000),
                        transaction_count=random.randint(100, 5000),
                        unique_users=random.randint(50, 1000),
                        avg_transaction_value=random.uniform(100, 1000),
                        total_fees=random.uniform(100, 5000)
                    )
                    db.session.add(market)
        
        db.session.commit()
        print("Sample market data added!")

if __name__ == '__main__':
    app.run(debug=True, port=5000)
