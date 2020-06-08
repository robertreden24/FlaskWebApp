from app.api import bp

@bp.route('/users/<int:id>',methods=['Get'])
def get_user(id):
    pass

@bp.route('/users',methods=['Get'])
def get_users():
    pass


