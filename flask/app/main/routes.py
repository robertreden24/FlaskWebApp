from app.main import bp
from flask import url_for,redirect
@bp.route('/')
@bp.route('/index')
def index():
    return redirect(url_for('auth.index'))
