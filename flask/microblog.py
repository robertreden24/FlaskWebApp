from app import db,create_app
from app.models import User,Post

application = create_app()
# run this code in terminal with xampp run to create database
db.app = application
db.create_all()

@app.shell_context_processor
def make_shell_context():
    return{'db': db, 'User': User, 'Post': Post}
