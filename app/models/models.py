from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Protocol(db.Model):
    __tablename__ = 'protocols'
    
    protocol_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    protocol_name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    protocol_symbol = db.Column(db.String(20), nullable=False, index=True)
    type = db.Column(db.String(50), nullable=False, index=True)  # DEX, Lending, Yield Farming, etc.
    description = db.Column(db.Text)
    website_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    contracts = db.relationship('Contract', backref='protocol', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'protocol_id': self.protocol_id,
            'protocol_name': self.protocol_name,
            'protocol_symbol': self.protocol_symbol,
            'type': self.type,
            'description': self.description,
            'website_url': self.website_url,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Contract(db.Model):
    __tablename__ = 'contracts'
    __table_args__ = (
        db.UniqueConstraint('contract_address', 'blockchain', name='uq_contract_blockchain'),
    )
    
    contract_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    contract_address = db.Column(db.String(255), nullable=False, index=True)
    blockchain = db.Column(db.String(50), nullable=False, index=True)
    protocol_id = db.Column(db.Integer, db.ForeignKey('protocols.protocol_id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    transactions = db.relationship('Transaction', backref='contract', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'contract_id': self.contract_id,
            'contract_address': self.contract_address,
            'blockchain': self.blockchain,
            'protocol_id': self.protocol_id,
            'protocol_name': self.protocol.protocol_name if self.protocol else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class User(db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_address = db.Column(db.String(255), unique=True, nullable=False, index=True)
    total_transactions = db.Column(db.Integer, default=0)
    total_volume = db.Column(db.Numeric(38, 18), default=0)
    first_transaction_date = db.Column(db.DateTime)
    last_transaction_date = db.Column(db.DateTime)
    user_type = db.Column(db.String(50))  # whale, regular, small, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    transactions_sent = db.relationship('Transaction', 
                                       foreign_keys='Transaction.from_user_id',
                                       backref='sender', 
                                       lazy='dynamic')
    transactions_received = db.relationship('Transaction',
                                           foreign_keys='Transaction.to_user_id',
                                           backref='receiver',
                                           lazy='dynamic')
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'user_address': self.user_address,
            'total_transactions': self.total_transactions,
            'total_volume': str(self.total_volume) if self.total_volume else '0',
            'first_transaction_date': self.first_transaction_date.isoformat() if self.first_transaction_date else None,
            'last_transaction_date': self.last_transaction_date.isoformat() if self.last_transaction_date else None,
            'user_type': self.user_type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    transaction_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    transaction_hash = db.Column(db.String(255), unique=True, nullable=False, index=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contracts.contract_id'), nullable=False)
    from_user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    to_user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    from_address = db.Column(db.String(255), nullable=False, index=True)
    to_address = db.Column(db.String(255), index=True)
    value = db.Column(db.Numeric(38, 18))
    gas_used = db.Column(db.BigInteger)
    gas_price = db.Column(db.Numeric(38, 18))
    transaction_fee = db.Column(db.Numeric(38, 18))
    timestamp = db.Column(db.DateTime, nullable=False, index=True)
    block_number = db.Column(db.BigInteger, index=True)
    status = db.Column(db.String(20), default='success')  # success, failed, pending
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'transaction_id': self.transaction_id,
            'transaction_hash': self.transaction_hash,
            'contract_id': self.contract_id,
            'from_address': self.from_address,
            'to_address': self.to_address,
            'value': str(self.value) if self.value else '0',
            'gas_used': self.gas_used,
            'gas_price': str(self.gas_price) if self.gas_price else '0',
            'transaction_fee': str(self.transaction_fee) if self.transaction_fee else '0',
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'block_number': self.block_number,
            'status': self.status
        }

class MarketData(db.Model):
    __tablename__ = 'market_data'
    
    market_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    protocol_id = db.Column(db.Integer, db.ForeignKey('protocols.protocol_id'), nullable=False)
    date = db.Column(db.Date, nullable=False, index=True)
    total_volume = db.Column(db.Numeric(38, 18))
    transaction_count = db.Column(db.Integer)
    unique_users = db.Column(db.Integer)
    avg_transaction_value = db.Column(db.Numeric(38, 18))
    total_fees = db.Column(db.Numeric(38, 18))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    protocol = db.relationship('Protocol', backref='market_data')
    
    __table_args__ = (
        db.UniqueConstraint('protocol_id', 'date', name='uq_protocol_date'),
    )
    
    def to_dict(self):
        return {
            'market_id': self.market_id,
            'protocol_id': self.protocol_id,
            'protocol_name': self.protocol.protocol_name if self.protocol else None,
            'date': self.date.isoformat() if self.date else None,
            'total_volume': str(self.total_volume) if self.total_volume else '0',
            'transaction_count': self.transaction_count,
            'unique_users': self.unique_users,
            'avg_transaction_value': str(self.avg_transaction_value) if self.avg_transaction_value else '0',
            'total_fees': str(self.total_fees) if self.total_fees else '0'
        }
