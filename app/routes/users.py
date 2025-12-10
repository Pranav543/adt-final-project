from flask import Blueprint, request, jsonify
from ..models.models import db, User
from sqlalchemy import func

bp = Blueprint('users', __name__, url_prefix='/api/users')

# CREATE
@bp.route('', methods=['POST'])
def create_user():
    data = request.get_json()
    
    if 'user_address' not in data:
        return jsonify({'error': 'user_address is required'}), 400
    
    existing = User.query.filter_by(user_address=data['user_address']).first()
    if existing:
        return jsonify({'error': 'User already exists'}), 409
    
    user = User(
        user_address=data['user_address'],
        user_type=data.get('user_type')
    )
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': 'User created', 'user': user.to_dict()}), 201

# READ - Get all users
@bp.route('', methods=['GET'])
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    user_type = request.args.get('user_type')
    
    query = User.query
    
    if user_type:
        query = query.filter_by(user_type=user_type)
    
    paginated = query.order_by(User.total_volume.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'users': [u.to_dict() for u in paginated.items],
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page
    })

# READ - Get single user
@bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

# READ - Get user by address
@bp.route('/address/<string:address>', methods=['GET'])
def get_user_by_address(address):
    user = User.query.filter_by(user_address=address).first_or_404()
    return jsonify(user.to_dict())

# UPDATE
@bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    if 'user_type' in data:
        user.user_type = data['user_type']
    if 'total_transactions' in data:
        user.total_transactions = data['total_transactions']
    if 'total_volume' in data:
        user.total_volume = data['total_volume']
    
    db.session.commit()
    
    return jsonify({'message': 'User updated', 'user': user.to_dict()})

# DELETE
@bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': 'User deleted'}), 200

# ANALYTICS - Top users by volume
@bp.route('/top-by-volume', methods=['GET'])
def get_top_users():
    limit = request.args.get('limit', 10, type=int)
    
    users = User.query.order_by(User.total_volume.desc()).limit(limit).all()
    
    return jsonify({
        'top_users': [u.to_dict() for u in users]
    })

# ANALYTICS - User statistics
@bp.route('/stats', methods=['GET'])
def get_user_stats():
    total_users = User.query.count()
    active_users = User.query.filter(User.total_transactions > 0).count()
    
    stats = {
        'total_users': total_users,
        'active_users': active_users,
        'inactive_users': total_users - active_users
    }
    
    return jsonify(stats)
