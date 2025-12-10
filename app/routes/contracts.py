from flask import Blueprint, request, jsonify
from ..models.models import db, Contract, Protocol

bp = Blueprint('contracts', __name__, url_prefix='/api/contracts')

# CREATE
@bp.route('', methods=['POST'])
def create_contract():
    data = request.get_json()
    
    required_fields = ['contract_address', 'blockchain', 'protocol_id']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if contract already exists
    existing = Contract.query.filter_by(
        contract_address=data['contract_address'],
        blockchain=data['blockchain']
    ).first()
    if existing:
        return jsonify({'error': 'Contract already exists'}), 409
    
    contract = Contract(
        contract_address=data['contract_address'],
        blockchain=data['blockchain'],
        protocol_id=data['protocol_id'],
        is_active=data.get('is_active', True)
    )
    
    db.session.add(contract)
    db.session.commit()
    
    return jsonify({'message': 'Contract created', 'contract': contract.to_dict()}), 201

# READ - Get all contracts
@bp.route('', methods=['GET'])
def get_contracts():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    blockchain = request.args.get('blockchain')
    protocol_id = request.args.get('protocol_id', type=int)
    
    query = Contract.query
    
    if blockchain:
        query = query.filter_by(blockchain=blockchain)
    if protocol_id:
        query = query.filter_by(protocol_id=protocol_id)
    
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'contracts': [c.to_dict() for c in paginated.items],
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page
    })

# READ - Get single contract
@bp.route('/<int:contract_id>', methods=['GET'])
def get_contract(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    return jsonify(contract.to_dict())

# UPDATE
@bp.route('/<int:contract_id>', methods=['PUT'])
def update_contract(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    data = request.get_json()
    
    if 'is_active' in data:
        contract.is_active = data['is_active']
    if 'contract_address' in data:
        contract.contract_address = data['contract_address']
    if 'blockchain' in data:
        contract.blockchain = data['blockchain']
    
    db.session.commit()
    
    return jsonify({'message': 'Contract updated', 'contract': contract.to_dict()})

# DELETE
@bp.route('/<int:contract_id>', methods=['DELETE'])
def delete_contract(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    db.session.delete(contract)
    db.session.commit()
    
    return jsonify({'message': 'Contract deleted'}), 200

# ANALYTICS - Contracts by blockchain
@bp.route('/by-blockchain', methods=['GET'])
def contracts_by_blockchain():
    from sqlalchemy import func
    
    results = db.session.query(
        Contract.blockchain,
        func.count(Contract.contract_id).label('count')
    ).group_by(Contract.blockchain).all()
    
    return jsonify({
        'blockchains': [{'blockchain': r[0], 'count': r[1]} for r in results]
    })
