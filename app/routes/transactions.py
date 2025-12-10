from flask import Blueprint, request, jsonify
from ..models.models import db, Transaction
from sqlalchemy import func, desc
from datetime import datetime, timedelta

bp = Blueprint('transactions', __name__, url_prefix='/api/transactions')

# CREATE
@bp.route('', methods=['POST'])
def create_transaction():
    data = request.get_json()
    
    required_fields = ['transaction_hash', 'contract_id', 'from_address', 'timestamp']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    existing = Transaction.query.filter_by(transaction_hash=data['transaction_hash']).first()
    if existing:
        return jsonify({'error': 'Transaction already exists'}), 409
    
    transaction = Transaction(
        transaction_hash=data['transaction_hash'],
        contract_id=data['contract_id'],
        from_user_id=data.get('from_user_id'),
        to_user_id=data.get('to_user_id'),
        from_address=data['from_address'],
        to_address=data.get('to_address'),
        value=data.get('value'),
        gas_used=data.get('gas_used'),
        gas_price=data.get('gas_price'),
        transaction_fee=data.get('transaction_fee'),
        timestamp=datetime.fromisoformat(data['timestamp']),
        block_number=data.get('block_number'),
        status=data.get('status', 'success')
    )
    
    db.session.add(transaction)
    db.session.commit()
    
    return jsonify({'message': 'Transaction created', 'transaction': transaction.to_dict()}), 201

# READ - Get all transactions
@bp.route('', methods=['GET'])
def get_transactions():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    contract_id = request.args.get('contract_id', type=int)
    from_address = request.args.get('from_address')
    status = request.args.get('status')
    
    query = Transaction.query
    
    if contract_id:
        query = query.filter_by(contract_id=contract_id)
    if from_address:
        query = query.filter_by(from_address=from_address)
    if status:
        query = query.filter_by(status=status)
    
    paginated = query.order_by(desc(Transaction.timestamp)).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'transactions': [t.to_dict() for t in paginated.items],
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page
    })

# READ - Get single transaction
@bp.route('/<int:transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    return jsonify(transaction.to_dict())

# READ - Get transaction by hash
@bp.route('/hash/<string:tx_hash>', methods=['GET'])
def get_transaction_by_hash(tx_hash):
    transaction = Transaction.query.filter_by(transaction_hash=tx_hash).first_or_404()
    return jsonify(transaction.to_dict())

# UPDATE
@bp.route('/<int:transaction_id>', methods=['PUT'])
def update_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    data = request.get_json()
    
    if 'status' in data:
        transaction.status = data['status']
    
    db.session.commit()
    
    return jsonify({'message': 'Transaction updated', 'transaction': transaction.to_dict()})

# DELETE
@bp.route('/<int:transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    db.session.delete(transaction)
    db.session.commit()
    
    return jsonify({'message': 'Transaction deleted'}), 200

# ANALYTICS - Transaction volume over time
@bp.route('/volume-over-time', methods=['GET'])
def get_volume_over_time():
    days = request.args.get('days', 30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    results = db.session.query(
        func.date(Transaction.timestamp).label('date'),
        func.sum(Transaction.value).label('total_volume'),
        func.count(Transaction.transaction_id).label('transaction_count')
    ).filter(Transaction.timestamp >= start_date)\
     .group_by(func.date(Transaction.timestamp))\
     .order_by(func.date(Transaction.timestamp)).all()
    
    return jsonify({
        'data': [{
            'date': r[0].isoformat() if r[0] else None,
            'total_volume': str(r[1]) if r[1] else '0',
            'transaction_count': r[2]
        } for r in results]
    })

# ANALYTICS - Transaction statistics
@bp.route('/stats', methods=['GET'])
def get_transaction_stats():
    total_transactions = Transaction.query.count()
    total_volume = db.session.query(func.sum(Transaction.value)).scalar() or 0
    avg_transaction_value = db.session.query(func.avg(Transaction.value)).scalar() or 0
    total_fees = db.session.query(func.sum(Transaction.transaction_fee)).scalar() or 0
    
    return jsonify({
        'total_transactions': total_transactions,
        'total_volume': str(total_volume),
        'avg_transaction_value': str(avg_transaction_value),
        'total_fees': str(total_fees)
    })
