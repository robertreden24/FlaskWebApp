import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    SQLALCHEMY_DATABASE_URI =  'mysql://admin:commservicer@dbcommservicer.cszctlutmjs9.us-east-2.rds.amazonaws.com:3306/app'
                                # 'mysql://newuser:password@localhost:3306/app'
                                # 'mysql+pymysql://root:''@localhost/app.sql'

    UPLOADED_IMAGES_DEST = 'app/uploads/postimages'
    UPLOAD_FOLDER = 'app/uploads/postimages'

    SQLALCHEMY_TRACK_MODIFICATIONS =False
    EVENTS_PER_PAGE = 10
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['commservicer@gmail.com']



