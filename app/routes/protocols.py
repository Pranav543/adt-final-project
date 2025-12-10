from flask import Blueprint, request, jsonify
from ..models.models import db, Protocol
from sqlalchemy import func

bp = Blueprint('protocols', __name__, url_prefix='/api/protocols')

# CREATE
@bp.route('', methods=['POST'])
def create_protocol():
    data = request.get_json()
    
    # Validation
    required_fields = ['protocol_name', 'protocol_symbol', 'type']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if protocol already exists
    existing = Protocol.query.filter_by(protocol_name=data['protocol_name']).first()
    if existing:
        return jsonify({'error': 'Protocol already exists'}), 409
    
    protocol = Protocol(
        protocol_name=data['protocol_name'],
        protocol_symbol=data['protocol_symbol'],
        type=data['type'],
        description=data.get('description'),
        website_url=data.get('website_url')
    )
    
    db.session.add(protocol)
    db.session.commit()
    
    return jsonify({'message': 'Protocol created', 'protocol': protocol.to_dict()}), 201

# READ - Get all protocols
@bp.route('', methods=['GET'])
def get_protocols():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    protocol_type = request.args.get('type')
    
    query = Protocol.query
    
    if protocol_type:
        query = query.filter_by(type=protocol_type)
    
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'protocols': [p.to_dict() for p in paginated.items],
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page
    })

# READ - Get single protocol
@bp.route('/<int:protocol_id>', methods=['GET'])
def get_protocol(protocol_id):
    protocol = Protocol.query.get_or_404(protocol_id)
    return jsonify(protocol.to_dict())

# UPDATE
@bp.route('/<int:protocol_id>', methods=['PUT'])
def update_protocol(protocol_id):
    protocol = Protocol.query.get_or_404(protocol_id)
    data = request.get_json()
    
    # Update fields
    if 'protocol_name' in data:
        protocol.protocol_name = data['protocol_name']
    if 'protocol_symbol' in data:
        protocol.protocol_symbol = data['protocol_symbol']
    if 'type' in data:
        protocol.type = data['type']
    if 'description' in data:
        protocol.description = data['description']
    if 'website_url' in data:
        protocol.website_url = data['website_url']
    
    db.session.commit()
    
    return jsonify({'message': 'Protocol updated', 'protocol': protocol.to_dict()})

# DELETE
@bp.route('/<int:protocol_id>', methods=['DELETE'])
def delete_protocol(protocol_id):
    protocol = Protocol.query.get_or_404(protocol_id)
    db.session.delete(protocol)
    db.session.commit()
    
    return jsonify({'message': 'Protocol deleted'}), 200

# ANALYTICS - Protocol statistics
@bp.route('/stats', methods=['GET'])
def get_protocol_stats():
    stats = db.session.query(
        Protocol.type,
        func.count(Protocol.protocol_id).label('count')
    ).group_by(Protocol.type).all()
    
    return jsonify({
        'protocol_types': [{'type': s[0], 'count': s[1]} for s in stats]
    })

# ANALYTICS - Top protocols by transaction volume
@bp.route('/top-by-volume', methods=['GET'])
def get_top_protocols():
    limit = request.args.get('limit', 10, type=int)
    
    from ..models.models import Contract, Transaction
    
    results = db.session.query(
        Protocol.protocol_name,
        Protocol.type,
        func.sum(Transaction.value).label('total_volume'),
        func.count(Transaction.transaction_id).label('transaction_count')
    ).join(Contract, Protocol.protocol_id == Contract.protocol_id)\
     .join(Transaction, Contract.contract_id == Transaction.contract_id)\
     .group_by(Protocol.protocol_id, Protocol.protocol_name, Protocol.type)\
     .order_by(func.sum(Transaction.value).desc())\
     .limit(limit).all()
    
    return jsonify({
        'top_protocols': [{
            'protocol_name': r[0],
            'type': r[1],
            'total_volume': str(r[2]) if r[2] else '0',
            'transaction_count': r[3]
        } for r in results]
    })
