from app.api import bp
from flask import jsonify
from app.models import User
@bp.route('/users/<int:id>',methods=['Get'])
def get_user(id):
    return jsonify(User.query.get_or_404(id).to_dict())

@bp.route('/users',methods=['Get'])
def get_users():
    pass

@bp.route('/users', methods=['POST'])
def create_user():
    pass
