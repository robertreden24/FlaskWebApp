from app.api import bp
from flask import jsonify,request
from app.models import Post

@bp.route('/posts',methods=['Get'])
def get_posts():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = Post.to_collection_dict(Post.query, page, per_page, 'api.get_posts')
    return jsonify(data)

@bp.route('/posts/<int:id>',methods=['Get'])
def get_post(id):
    return jsonify(Post.query.get_or_404(id).to_dict())

@bp.route('/posts/<int:id>/participants',methods=['Get'])
def get_post_participants(id):
    pass



