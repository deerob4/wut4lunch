import datetime

from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask.ext.login import logout_user, login_required, current_user, login_user

from wut4lunch import cache
from wut4lunch.forms import LoginForm, AddLunch, RegisterForm, ChangePassword
from wut4lunch.models import db, User, Lunch

main = Blueprint('main', __name__)


@main.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = AddLunch()
    page = request.args.get('page', 1, type=int)
    pagination = Lunch.query.filter_by(visible_to='all').order_by(Lunch.pub_date.desc()).paginate(page, 12)
    lunches = pagination.items
    if form.validate_on_submit():
        lunch = Lunch(text=form.lunch.data, pub_date=datetime.datetime.now(), enjoyed=form.enjoyed.data, visible_to=form.visible_to.data, author_id=current_user.id)
        db.session.add(lunch)
        db.session.commit()
        return redirect(url_for('.index'))
    return render_template('index.html', form=form, lunches=lunches)


@main.route('/about')
def about():
    return render_template('about.html')


@main.route('/profile/<username>')
@login_required
def profile(username):
    form = AddLunch()
    user = User.query.filter_by(username=username).first()
    if user:
        lunches = Lunch.query.filter_by(author_id=user.id).all()
        return render_template('profile.html', user=user, form=form, lunches=lunches)
    else:
        return render_template('errors/404.html', form=form), 404


@main.route('/profile/<username>/change-password', methods=['GET', 'POST'])
@login_required
def change_password(username):
    form = AddLunch()
    password_form = ChangePassword()
    user = User.query.filter_by(username=username).first()
    if user:
        if user.username == current_user.username:
            if password_form.validate_on_submit():
                user.password = user.set_password(password_form.new_password.data)
                db.session.add(user)
                db.session.commit()
                flash('Password changed successfully!', 'success')
                return redirect(url_for(change_password, username=current_user.username))
            for error in password_form.errors.items():
                flash(error[1][0], 'danger')
            return render_template('auth/change_password.html', form=form, password_form=password_form)
        else:
            return render_template('errors/401.html', form=form), 401
    else:
        return render_template('errors/404.html', form=form), 404


@main.route('/lunch/<lunch_id>')
def lunch(lunch_id):
    form = AddLunch()
    lunch = Lunch.query.filter_by(id=lunch_id).first()
    if lunch:
        if lunch.visible_to == 'all':
            return render_template('lunches/lunch.html', lunch=lunch, form=form)
        elif lunch.visible_to != 'all' and lunch.author_id == current_user.id:
            return render_template('lunches/lunch.html', lunch=lunch, form=form)
        else:
            return render_template('lunches/private_lunch.html', form=form)
    else:
        return render_template('errors/404.html', form=form), 404


@main.route('/signin', methods=['GET', 'POST'])
def signin():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user)
            return redirect(request.args.get('next') or url_for('.index'))
        flash('Invalid email or password.', 'danger')
    for error in form.errors.items():
        flash(error[1][0], 'danger')
    return render_template('auth/signin.html', form=form)


@main.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.email.data.replace('.', '').split('@')[0]
        user = User(name=form.name.data, email=form.email.data, username=username, password=form.password.data,
                    member_since=datetime.datetime.now())
        db.session.add(user)
        db.session.commit()
        flash('You can now sign in!', 'success')
        return redirect(url_for('.signin'))
    for error in form.errors.items():
        flash(error[1][0], 'danger')
    return render_template('auth/signup.html', form=form)


@main.route('/signout')
def signout():
    logout_user()
    flash('You have been successfully signed out.', 'success')
    return redirect(url_for('.signin'))



