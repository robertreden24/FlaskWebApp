from app import app,db

from flask import render_template,flash,redirect,url_for
from app.forms import LoginForm,RegistrationForm,PostForm,EmptyForm
from flask_login import current_user,login_user
from app.models import User,Post
from flask_login import logout_user
from flask_login import login_required
from flask import request
from werkzeug.urls import url_parse
from datetime import datetime
from app.forms import EditProfileForm,ResetPasswordRequestForm
from app.email import send_password_reset_email

@app.route('/edit_profile',methods =['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Username and profile changed', 'success')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',form=form)


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now()
        db.session.commit()

@app.route('/')
@app.route('/index')
@login_required
def index():
    page = request.args.get('page',1,type = int)
    posts = Post.query.filter_by(verified=True).order_by(Post.timestamp.desc())
    posts = posts.paginate(page, app.config['EVENTS_PER_PAGE'],False)
    # posts = Post.query.order_by(Post.timestamp.desc()).all() #change this to only query for verified ones only
    form = EmptyForm()
    verify = False
    if posts.has_next:
        next_url = url_for('index', page=posts.next_num)
    else:
        next_url = None
    if posts.has_prev:
        prev_url = url_for('index', page=posts.next_num)
    else:
        prev_url = None
    return render_template('index.html',title='Home Page',
                           posts=posts.items, user = current_user,form = form,verify = verify,
                           next_url=next_url, prev_url=prev_url)


@app.route('/login', methods = ['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            # flash('Login requested for user {}, remember_me={}'.format(
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
        login_user(user,remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html',title='Sign In', form = form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username = form.username.data, email=form.email.data,user_level = 3)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author' : user , 'body': 'Test post #1'},
        {'author' : user,  'body': 'Test post #2'}
    ]
    return render_template('user.html',user=user,title='Post', posts=posts)

@app.route('/make_event',methods=['GET','POST'])
@login_required
def make_event():
    form = PostForm()
    print("hello")
    print(form.title.data)
    print(form.start_time.data)
    print(form.max_participant.data)
    if form.validate_on_submit():
        print("in here")
        post = Post(title=form.title.data, body = form.details.data,
                    user_id = current_user.id,max_participant=form.max_participant.data,
                    start_time = form.start_time.data)
        db.session.add(post)
        db.session.commit()
        flash('We have received your application', 'success')
        return redirect(url_for('index'))
    return render_template('make_event.html',user=current_user, form=form)

@app.route('/verify_events')
@login_required
def verify_events():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(verified=True).order_by(Post.timestamp.desc())
    posts = posts.paginate(page, app.config['EVENTS_PER_PAGE'], False)
    form = EmptyForm()
    verify = True
    next_url = url_for('explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html',title='Home Page',posts=posts.items, user = current_user,form = form,verify = verify,
                           next_url = next_url,prev_url=prev_url)


@app.route('/event/<id>')
@login_required
def event_details(id):
    post = Post.query.filter_by(id = id).first_or_404()
    form = EmptyForm()
    list_of_participants = post.participant_list()
    return render_template('event_details.html',post = post, user=current_user,form =form, list_of_participants=list_of_participants)

@app.route('/join/<id>',methods=['Post'])
@login_required
def join(id):
    post = Post.query.filter_by(id=id).first_or_404()
    form = EmptyForm()
    if form.validate_on_submit():
        post = Post.query.filter_by(id = id).first()
        if post is None:
            flash("Event {} does not exist".format(id), 'warning')
            return redirect(url_for('index'))
        # if post.verified is False:
        #     flash("event is not verified yet")
        #     return redirect(url_for('event',id=id))
        if post.has_joined(current_user) is True:
            flash('You have already joined this event', 'info')
            return redirect(url_for('event_details',id=id))
        post.join(current_user)
        db.session.commit()
        flash('You have successfully joined the event!!', 'success')
        return redirect(url_for('event_details',id=id))
    else:
        return redirect(url_for(index))

@app.route('/leave/<id>',methods=['Post'])
@login_required
def leave(id):
    post = Post.query.filter_by(id=id).first_or_404()
    form = EmptyForm()
    if form.validate_on_submit():
        post = Post.query.filter_by(id = id).first()
        if post is None:
            flash("Event {} does not exist".format(id), 'danger')
            return redirect(url_for('index'))
        # if post.verified is False:
        #     flash("event is not verified yet")
        #     return redirect(url_for('event_details',id=id))
        if post.has_joined(current_user) is False:
            flash('You have not joined this event', 'danger')
            return redirect(url_for('event_details',id=id))
        post.leave(current_user)
        db.session.commit()
        flash('You have successfully left the event!!', 'info')
        return redirect(url_for('event_details',id=id))
    else:
        return redirect(url_for(index))

@app.route('/verify/<id>',methods=['Post'])
@login_required
def verify(id):
    post = Post.query.filter_by(id=id).first_or_404()
    form = EmptyForm()
    if form.validate_on_submit():
        if current_user.user_level > 2:
            flash("you do not have the authority for this action")
            redirect(url_for(index))
        post = Post.query.filter_by(id = id).first()
        if post is None:
            flash("Event {} does not exist".format(id), 'danger')
            return redirect(url_for('index'))
        if post.verified is True:
            flash('Event already verified', 'info')
            return redirect(url_for('event_details',id=id))
        post.verified = True
        db.session.commit()
        flash('Event is verified!!', 'success')
        return redirect(url_for('event_details',id=id))
    else:
        return redirect(url_for(index))

@app.route('/delete_event/<id>',methods=['Post'])
def delete_event(id):
    post = Post.query.filter_by(id=id).first_or_404()
    form = EmptyForm()
    if form.validate_on_submit():

        post = Post.query.filter_by(id=id).first()
        if current_user.user_level > 2 and current_user.id != post.user_id:
            flash("you do not have the authority for this action")
            redirect(url_for(index))
        if post is None:
            flash("event {} does not exist".format(id))
            return redirect(url_for(index))
        db.session.delete(post)
        db.session.commit()
        flash('event is deleted!!')
        return redirect(url_for(index))
    else:
        return redirect(url_for(index))

@app.route('/reset_password_request', methods=['GET','POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for further action')
        return redirect((url_for('login')))
    return render_template('reset_password_request.html', title = 'Reset Password', form = form)


