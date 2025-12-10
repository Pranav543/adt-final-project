import pandas as pd
from ..models.models import db, Protocol, Contract, User, Transaction, MarketData
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import os

def load_contracts_from_parquet(parquet_path):
    """Load contracts data from Parquet file"""
    df = pd.read_parquet(parquet_path)
    
    protocols_added = {}
    contracts_added = 0
    
    for _, row in df.iterrows():
        protocol_name = row['protocol_name']
        
        if protocol_name not in protocols_added:
            protocol = Protocol.query.filter_by(protocol_name=protocol_name).first()
            if not protocol:
                protocol = Protocol(
                    protocol_name=row['protocol_name'],
                    protocol_symbol=row['protocol_symbol'],
                    type=row['type'],
                    description=row.get('description', ''),
                    website_url=row.get('website_url', '')
                )
                db.session.add(protocol)
                db.session.flush()
            protocols_added[protocol_name] = protocol.protocol_id
        
        existing_contract = Contract.query.filter_by(
            contract_address=row['contract_address'],
            blockchain=row['blockchain']
        ).first()
        
        if not existing_contract:
            contract = Contract(
                contract_address=row['contract_address'],
                blockchain=row['blockchain'],
                protocol_id=protocols_added[protocol_name]
            )
            db.session.add(contract)
            contracts_added += 1
    
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
    
    return {'protocols_added': len(protocols_added), 'contracts_added': contracts_added}


def load_users_from_parquet(parquet_path):
    """Load users data from Parquet file"""
    df = pd.read_parquet(parquet_path)
    users_added = 0
    
    for _, row in df.iterrows():
        existing_user = User.query.filter_by(user_address=row['user_address']).first()
        
        if not existing_user:
            user = User(
                user_address=row['user_address'],
                total_transactions=row.get('total_transactions', 0),
                total_volume=row.get('total_volume', 0),
                first_transaction_date=pd.to_datetime(row.get('first_transaction_date')) if pd.notna(row.get('first_transaction_date')) else None,
                last_transaction_date=pd.to_datetime(row.get('last_transaction_date')) if pd.notna(row.get('last_transaction_date')) else None,
                user_type=row.get('user_type', 'regular')
            )
            db.session.add(user)
            users_added += 1
    
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
    
    return {'users_added': users_added}


def load_transactions_from_parquet(parquet_path):
    """Load transactions data from Parquet file"""
    df = pd.read_parquet(parquet_path)
    transactions_added = 0
    
    # Create address to contract_id mapping
    contracts = {c.contract_address: c.contract_id for c in Contract.query.all()}
    users = {u.user_address: u.user_id for u in User.query.all()}
    
    for _, row in df.iterrows():
        existing_tx = Transaction.query.filter_by(transaction_hash=row['transaction_hash']).first()
        
        if not existing_tx:
            contract_id = contracts.get(row.get('contract_address'))
            if not contract_id:
                continue
            
            transaction = Transaction(
                transaction_hash=row['transaction_hash'],
                contract_id=contract_id,
                from_user_id=users.get(row.get('from_address')),
                to_user_id=users.get(row.get('to_address')),
                from_address=row['from_address'],
                to_address=row.get('to_address'),
                value=row.get('value', 0),
                gas_used=row.get('gas_used'),
                gas_price=row.get('gas_price'),
                transaction_fee=row.get('transaction_fee'),
                timestamp=pd.to_datetime(row['timestamp']),
                block_number=row.get('block_number'),
                status=row.get('status', 'success')
            )
            db.session.add(transaction)
            transactions_added += 1
            
            if transactions_added % 1000 == 0:
                db.session.commit()
    
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
    
    return {'transactions_added': transactions_added}


def load_market_from_parquet(parquet_path):
    """Load market data from Parquet file"""
    df = pd.read_parquet(parquet_path)
    market_added = 0
    
    protocols = {p.protocol_name: p.protocol_id for p in Protocol.query.all()}
    
    for _, row in df.iterrows():
        protocol_id = protocols.get(row.get('protocol_name'))
        if not protocol_id:
            continue
        
        date_val = pd.to_datetime(row['date']).date() if pd.notna(row.get('date')) else None
        
        existing = MarketData.query.filter_by(
            protocol_id=protocol_id,
            date=date_val
        ).first()
        
        if not existing:
            market = MarketData(
                protocol_id=protocol_id,
                date=date_val,
                total_volume=row.get('total_volume', 0),
                transaction_count=row.get('transaction_count', 0),
                unique_users=row.get('unique_users', 0),
                avg_transaction_value=row.get('avg_transaction_value', 0),
                total_fees=row.get('total_fees', 0)
            )
            db.session.add(market)
            market_added += 1
    
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
    
    return {'market_added': market_added}


def load_all_data(data_dir='data'):
    """Load all Parquet files"""
    results = {}
    
    contracts_path = os.path.join(data_dir, 'contracts.parquet')
    if os.path.exists(contracts_path):
        results['contracts'] = load_contracts_from_parquet(contracts_path)
    
    users_path = os.path.join(data_dir, 'users.parquet')
    if os.path.exists(users_path):
        results['users'] = load_users_from_parquet(users_path)
    
    transactions_path = os.path.join(data_dir, 'transactions.parquet')
    if os.path.exists(transactions_path):
        results['transactions'] = load_transactions_from_parquet(transactions_path)
    
    market_path = os.path.join(data_dir, 'market.parquet')
    if os.path.exists(market_path):
        results['market'] = load_market_from_parquet(market_path)
    
    return results
