from app.api import bp

@bp.route('/Posts',methods=['Get'])
def get_posts():
    pass

@bp.route('/Posts/<int:id>',methods=['Get'])
def get_post(id):
    pass

@bp.route('/Posts/<int:id>/participants',methods=['Get'])
def get_post_participants(id):
    pass

@bp.route('/users', methods=['POST'])
def create_user():
    pass

