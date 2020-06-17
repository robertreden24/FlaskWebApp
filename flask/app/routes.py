from app import db
from app.auth import bp
from flask import render_template,flash,redirect,url_for,current_app
from app.auth.forms import LoginForm,RegistrationForm,PostForm,EmptyForm
from flask_login import current_user,login_user
from app.models import User,Post
from flask_login import logout_user
from flask_login import login_required
from flask import request
from werkzeug.urls import url_parse
from datetime import datetime
from app.auth.forms import EditProfileForm,ResetPasswordRequestForm

@bp.route('/')
@bp.route('/index')
def index():
    return redirect(url_for('auth.index'))


