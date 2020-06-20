import os
import tempfile

import pytest

from app import db
app = create_app()

@pytest.fixture
def client():
    db_fd, db.config['DATABASE'] = tempfile.mkstemp()
    db.config['TESTING'] = True

    with db.test_client() as client:
        with db.app_context():
            db.init_db()
        yield client

    os.close(db_fd)
    os.unlink(db.config['DATABASE'])
    
# from flaskr import flaskr

# @pytest.fixture
# def client():
#     db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
#     flaskr.app.config['TESTING'] = True

#     with flaskr.app.test_client() as client:
#         with flaskr.app.app_context():
#             flaskr.init_db()
#         yield client

#     os.close(db_fd)
#     os.unlink(flaskr.app.config['DATABASE'])
