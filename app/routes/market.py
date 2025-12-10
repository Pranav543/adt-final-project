from flask import Blueprint, request, jsonify
from ..models.models import db, MarketData, Protocol
from sqlalchemy import func, desc
from datetime import datetime, timedelta

bp = Blueprint('market', __name__, url_prefix='/api/market')

# CREATE
@bp.route('', methods=['POST'])
def create_market_data():
    data = request.get_json()
    
    required_fields = ['protocol_id', 'date']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    market_data = MarketData(
        protocol_id=data['protocol_id'],
        date=datetime.fromisoformat(data['date']).date(),
        total_volume=data.get('total_volume'),
        transaction_count=data.get('transaction_count'),
        unique_users=data.get('unique_users'),
        avg_transaction_value=data.get('avg_transaction_value'),
        total_fees=data.get('total_fees')
    )
    
    db.session.add(market_data)
    db.session.commit()
    
    return jsonify({'message': 'Market data created', 'market_data': market_data.to_dict()}), 201

# READ - Get all market data
@bp.route('', methods=['GET'])
def get_market_data():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    protocol_id = request.args.get('protocol_id', type=int)
    
    query = MarketData.query
    
    if protocol_id:
        query = query.filter_by(protocol_id=protocol_id)
    
    paginated = query.order_by(desc(MarketData.date)).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'market_data': [m.to_dict() for m in paginated.items],
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page
    })

# READ - Get single market data entry
@bp.route('/<int:market_id>', methods=['GET'])
def get_market_data_entry(market_id):
    market_data = MarketData.query.get_or_404(market_id)
    return jsonify(market_data.to_dict())

# UPDATE
@bp.route('/<int:market_id>', methods=['PUT'])
def update_market_data(market_id):
    market_data = MarketData.query.get_or_404(market_id)
    data = request.get_json()
    
    if 'total_volume' in data:
        market_data.total_volume = data['total_volume']
    if 'transaction_count' in data:
        market_data.transaction_count = data['transaction_count']
    if 'unique_users' in data:
        market_data.unique_users = data['unique_users']
    if 'avg_transaction_value' in data:
        market_data.avg_transaction_value = data['avg_transaction_value']
    if 'total_fees' in data:
        market_data.total_fees = data['total_fees']
    
    db.session.commit()
    
    return jsonify({'message': 'Market data updated', 'market_data': market_data.to_dict()})

# DELETE
@bp.route('/<int:market_id>', methods=['DELETE'])
def delete_market_data(market_id):
    market_data = MarketData.query.get_or_404(market_id)
    db.session.delete(market_data)
    db.session.commit()
    
    return jsonify({'message': 'Market data deleted'}), 200

# ANALYTICS - Market trends
@bp.route('/trends', methods=['GET'])
def get_market_trends():
    days = request.args.get('days', 30, type=int)
    protocol_id = request.args.get('protocol_id', type=int)
    
    query = MarketData.query
    
    if protocol_id:
        query = query.filter_by(protocol_id=protocol_id)
    
    start_date = datetime.utcnow().date() - timedelta(days=days)
    results = query.filter(MarketData.date >= start_date)\
                   .order_by(MarketData.date).all()
    
    return jsonify({
        'trends': [m.to_dict() for m in results]
    })

# ANALYTICS - Protocol comparison
@bp.route('/compare', methods=['GET'])
def compare_protocols():
    days = request.args.get('days', 7, type=int)
    start_date = datetime.utcnow().date() - timedelta(days=days)
    
    results = db.session.query(
        Protocol.protocol_name,
        Protocol.type,
        func.sum(MarketData.total_volume).label('total_volume'),
        func.sum(MarketData.transaction_count).label('transaction_count'),
        func.avg(MarketData.unique_users).label('avg_unique_users')
    ).join(MarketData, Protocol.protocol_id == MarketData.protocol_id)\
     .filter(MarketData.date >= start_date)\
     .group_by(Protocol.protocol_id, Protocol.protocol_name, Protocol.type)\
     .order_by(desc(func.sum(MarketData.total_volume))).all()
    
    return jsonify({
        'comparison': [{
            'protocol_name': r[0],
            'type': r[1],
            'total_volume': str(r[2]) if r[2] else '0',
            'transaction_count': r[3] or 0,
            'avg_unique_users': float(r[4]) if r[4] else 0
        } for r in results]
    })
