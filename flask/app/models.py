from app import login
from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from time import time
import jwt
from flask import current_app,url_for


participants = db.Table('participants',
                        db.Column('user_id', db.Integer, db.ForeignKey('user.id'),primary_key=True),
                        db.Column('post_id', db.Integer, db.ForeignKey('post.id'),primary_key=True))

class PaginatedAPIMixin(object):
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = query.paginate(page, per_page, False)
        data = {
            'items': [item.to_dict() for item in resources.items],
            '_meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total
            },
            '_links': {
                'self': url_for(endpoint, page=page, per_page=per_page,
                                **kwargs),
                'next': url_for(endpoint, page=page + 1, per_page=per_page,
                                **kwargs) if resources.has_next else None,
                'prev': url_for(endpoint, page=page - 1, per_page=per_page,
                                **kwargs) if resources.has_prev else None
            }
        }
        return data

class User(PaginatedAPIMixin,UserMixin, db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(128),index=True,unique=True,nullable=False)
    email = db.Column(db.String(128), index=True, unique=True, nullable=False)
    password = db.Column(db.String(128),nullable=False)
    user_level = db.Column(db.Integer,nullable= False,default=3)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)


    def __repr__(self):
        return '<User{}>'.format(self.username)

    def set_password(self,password):
        self.password = generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password,password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def get_reset_password_token(self,expires_in=600):
        return jwt.encode({'reset_password': self.id, 'exp': time() + expires_in},current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    def to_dict(self, include_email = False):
        data = {'id': self.id,
            'username': self.username,
            'user_level': self.user_level,
            'about_me':self.about_me,
            'last_seen': self.last_seen.isoformat() +'+7',
            'links': {
                'self':url_for('api.get_user',id=self.id),
            }
        }
        if (include_email):
            data['email']=self.email
        return data

    def from_dict(self, data, new_user=False):
        for field in ['username', 'email', 'about_me']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


class Post(PaginatedAPIMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100),nullable = False , index = True)
    body = db.Column(db.String(1000))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now())
    start_time  = db.Column(db.DateTime, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)
    max_participant = db.Column(db.Integer)
    verified = db.Column(db.BOOLEAN,nullable=False,default = False)
    socialHours = db.Column(db.Integer)
    filename = db.Column(db.String(1000))

    participant_count = db.relationship('User', secondary=participants,
                                        primaryjoin =(participants.c.post_id == id),
                                        secondaryjoin =(participants.c.user_id == User.id),
                                        backref=db.backref('Post',lazy=True), lazy=True)



    def __repr__(self):
        return '<Post {}>'.format(self.title)

    def join(self, user):
        if not self.has_joined(user):
            self.participant_count.append(user)

    def leave(self, user):
        if self.has_joined(user):
            self.participant_count.remove(user)

    def has_joined(self, user):
        # return self.participant_count.filter(
        #     participants.c.user_id == user.id).count() > 0
        return Post.query.filter(participants.c.user_id == user.id, participants.c.post_id == self.id).count()> 0

    def participant_list(self):
        return User.query.join(participants,(participants.c.user_id == User.id)).\
            filter(participants.c.post_id == self.id).all()

    def to_dict(self):
        data = {'id': self.id,
            'title': self.title,
            'body': self.body,
            'timestamp':self.timestamp.isoformat() + '+7',
            'start_time': self.start_time.isoformat() +'+7',
            'user_id': self.user_id,
            'max_participant': self.max_participant,
            'verified': self.verified,
            'socialHours': self.socialHours,
            'links': {
                'self':url_for('api.get_post',id=self.id),
                'participants':url_for('api.get_post_participants', id=self.id)
            }
        }
        return data
    def to_dict_filename(self):
        data = {'filename': self.filename}
        return data

    def from_dict(self,data):
        for field in ['title','body','start_time',
                      'user_id','max_participant','verified','socialHours']:
            if field in data:
                setattr(self,field,data[field])

@login.user_loader
def load_user(id):
    return User.query.get(int(id))



