from app import db,create_app
from app.models import User,Post

app = create_app()
db.app = app
db.create_all()
@app.shell_context_processor
def make_shell_context():
    return{'db': db, 'User': User, 'Post': Post}
