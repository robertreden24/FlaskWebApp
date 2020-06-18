from app import db,images
from app.auth import bp
from flask import render_template,flash,redirect,url_for,current_app,send_from_directory
from app.auth.forms import LoginForm,RegistrationForm,PostForm,EmptyForm
from flask_login import current_user,login_user
from app.models import User,Post
from flask_login import logout_user
from flask_login import login_required
from flask import request,jsonify
from werkzeug.urls import url_parse
from datetime import datetime
from app.auth.forms import EditProfileForm,ResetPasswordRequestForm
from app.auth.email import send_password_reset_email
import requests
from werkzeug.exceptions import NotFound, ServiceUnavailable
from werkzeug.utils import secure_filename
import os
import requests
@bp.route('/uploads/<filename>')
def download_file(filename):
    print("HERE")
    return send_from_directory("uploads/postimages", filename, as_attachment=True)

@bp.route('/edit_profile',methods =['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    print("not here")
    print(form.username.data)
    print(form.about_me.data)
    if form.validate_on_submit():
        current_user.username = form.username.data
        print("in here")
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Username and profile changed', 'success')
        return redirect(url_for('auth.user', username= current_user.username))
    # elif request.method == 'GET':
    #     form.username.data = current_user.username
    #     form.about_me.data = current_user.about_me
    #     print("in here instead")
    return render_template('edit_profile.html', title='Edit Profile',form=form)


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now()
        db.session.commit()

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    page = request.args.get('page',1,type = int)
    posts = Post.query.filter_by(verified=True).order_by(Post.timestamp.desc())
    posts = posts.paginate(page, current_app.config['EVENTS_PER_PAGE'],False)
    # posts = Post.query.order_by(Post.timestamp.desc()).all() #change this to only query for verified ones only
    form = EmptyForm()
    verify = False
    print(url_for('static', filename='css/custom.css'))
    if posts.has_next:
        next_url = url_for('auth.index', page=posts.next_num)
    else:
        next_url = None
    if posts.has_prev:
        prev_url = url_for('auth.index', page=posts.next_num)
    else:
        prev_url = None
    return render_template('index.html', title='Home Page',
                           posts=posts.items, user = current_user, form = form, verify = verify,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/login', methods = ['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            # flash('Login requested for user {}, remember_me={}'.format(
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))
        login_user(user,remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('auth.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', form = form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.index'))


@bp.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username = form.username.data, email=form.email.data,user_level = 3)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Register', form=form)

@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    # posts = [
    #     {'author' : user , 'body': 'Test post #1'},
    #     {'author' : user,  'body': 'Test post #2'}
    # ]
    page = request.args.get('page', 1, type=int)
    form = EmptyForm()
    posts = Post.query.filter_by(verified=True).order_by(Post.timestamp.desc())
    posts = posts.paginate(page, current_app.config['EVENTS_PER_PAGE'], False)
    next_url = url_for('auth.user',username = username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('auth.user', username = username, page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('user.html', user=user, title='Profile', form = form, posts=posts.items, next_url = next_url, prev_url=prev_url)

@bp.route('/make_event',methods=['GET','POST'])
@login_required
def make_event():
    form = PostForm()
    if form.is_submitted():
        print("submitted")
    if form.validate():
        print("valid")

    if form.validate_on_submit():
        print(form.errors)
        print(form.image.data)
        if not form.image.data:
            print('no files has been uploaded')
            post = Post(title=form.title.data, body=form.details.data,
                        user_id=current_user.id, max_participant=form.max_participant.data,
                        start_time=form.start_time.data,
                        socialHours=form.socialHours.data)
        else:
            f = form.image.data
            filename = secure_filename(f.filename)
            f.save(os.path.join(current_app.config['UPLOAD_FOLDER'],filename))
            print(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            url = url_for('auth.download_file',filename = filename)
            # filename = images.save(form.image.data)
            # print(filename)
            # url = images.path(filename)
            # print(url)
            # url = images.url(filename)
            # print(url)
            # url = url [11:]


            filedata = {"image_filename": filename, "image_url": url}
            # filedata = jsonify(filedata)
            try:
                new_Post = requests.post("http://localhost:5001/images/",json = filedata)    #CHANGE THIS LINK TO WHATEVER DOMAIN U HAVE FOR THE MICROSERVICE
            except requests.exceptions.ConnectionError:
                flash("image upload service unavailable")
                redirect(url_for("auth.make_event"))

            post = Post(title=form.title.data, body = form.details.data,
                        user_id = current_user.id,max_participant=form.max_participant.data,
                        start_time = form.start_time.data,
                        socialHours=form.socialHours.data,filename=filename)
        db.session.add(post)
        db.session.commit()
        flash('We have received your application', 'success')
        return redirect(url_for('auth.index'))
    return render_template('make_event.html', user=current_user, form=form)

@bp.route('/verify_events')
@login_required
def verify_events():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(verified=False).order_by(Post.timestamp.desc())
    posts = posts.paginate(page, current_app.config['EVENTS_PER_PAGE'], False)
    form = EmptyForm()
    verify = True
    next_url = url_for('auth.index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('auth.index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title='Home Page', posts=posts.items, user = current_user, form = form,
                           verify = verify,
                           next_url = next_url, prev_url=prev_url)



@bp.route('/event/<id>')
@login_required
def event_details(id):
    post = Post.query.filter_by(id = id).first_or_404()
    form = EmptyForm()
    list_of_participants = post.participant_list()
    if post.filename:

        url = "http://localhost:5001/images/" + post.filename
        data = requests.get(url, headers={'content-type':'application/json'})

        data = data.json()
        image_url = data["image_url"]
        return render_template('event_details.html', post = post, user=current_user, form =form, list_of_participants=list_of_participants,image_url = image_url)


    return render_template('event_details.html', post = post, user=current_user, form =form, list_of_participants=list_of_participants)

@bp.route('/join/<id>',methods=['Post'])
@login_required
def join(id):
    post = Post.query.filter_by(id=id).first_or_404()
    form = EmptyForm()
    if form.validate_on_submit():
        post = Post.query.filter_by(id = id).first()
        if post is None:
            flash("Event {} does not exist".format(id), 'warning')
            return redirect(url_for('auth.index'))
        # if post.verified is False:
        #     flash("event is not verified yet")
        #     return redirect(url_for('event',id=id))
        if post.has_joined(current_user) is True:
            flash('You have already joined this event', 'info')
            return redirect(url_for('auth.event_details',id=id))
        post.join(current_user)
        db.session.commit()
        flash('You have successfully joined the event!!', 'success')
        return redirect(url_for('auth.event_details',id=id))
    else:
        return redirect(url_for('auth.index'))

@bp.route('/leave/<id>',methods=['Post'])
@login_required
def leave(id):
    post = Post.query.filter_by(id=id).first_or_404()
    form = EmptyForm()
    if form.validate_on_submit():
        post = Post.query.filter_by(id = id).first()
        if post is None:
            flash("Event {} does not exist".format(id), 'danger')
            return redirect(url_for('auth.index'))
        # if post.verified is False:
        #     flash("event is not verified yet")
        #     return redirect(url_for('event_details',id=id))
        if post.has_joined(current_user) is False:
            flash('You have not joined this event', 'danger')
            return redirect(url_for('auth.event_details',id=id))
        post.leave(current_user)
        db.session.commit()
        flash('You have successfully left the event!!', 'info')
        return redirect(url_for('auth.event_details',id=id))
    else:
        return redirect(url_for('auth.index'))

@bp.route('/verify/<id>',methods=['Post'])
@login_required
def verify(id):
    post = Post.query.filter_by(id=id).first_or_404()
    form = EmptyForm()
    if form.validate_on_submit():
        if current_user.user_level > 2:
            flash("you do not have the authority for this action")
            redirect(url_for('auth.index'))
        post = Post.query.filter_by(id = id).first()
        if post is None:
            flash("Event {} does not exist".format(id), 'danger')
            return redirect(url_for('auth.index'))
        if post.verified is True:
            flash('Event already verified', 'info')
            return redirect(url_for('auth.event_details',id=id))
        post.verified = True
        db.session.commit()
        flash('Event is verified!!', 'success')
        return redirect(url_for('auth.event_details',id=id))
    else:
        return redirect(url_for('auth.index'))

@bp.route('/delete_event/<id>',methods=['Post'])
def delete_event(id):
    post = Post.query.filter_by(id=id).first_or_404()
    form = EmptyForm()
    if form.validate_on_submit():

        post = Post.query.filter_by(id=id).first()
        if current_user.user_level > 2 and current_user.id != post.user_id:
            flash("you do not have the authority for this action")
            redirect(url_for('auth.index'))
        if post is None:
            flash("event {} does not exist".format(id))
            return redirect(url_for('auth.index'))
        db.session.delete(post)
        db.session.commit()
        flash('event is deleted!!')
        return redirect(url_for(index))
    else:
        return redirect(url_for('auth.index'))

@bp.route('/reset_password_request', methods=['GET','POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for further action')
        return redirect((url_for('auth.login')))
    return render_template('auth/reset_password_request.html', title ='Reset Password', form = form)


@bp.route('/reset_password/<token>', methods=['GET','POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))
    user = User.verify_reset_password_token(token)
    if not user:
            return redirect(url_for('auth.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Password has changed')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)
