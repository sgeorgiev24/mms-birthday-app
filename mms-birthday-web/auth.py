import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


def if_user_exists(username):
    db = get_db()

    user_id = db.execute(
            'select id from user where username = ?',
            (username,)
        ).fetchone()

    if user_id is None:
        return False
    else:
        return True


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'select * from user where id = ?',
            (user_id,)
        ).fetchone()


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        name = request.form['name']
        last_name = request.form['last_name']
        birthday_date = request.form['birthday_date']
        is_admin = 0
        is_active = 1

        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif not email:
            error = 'Email is required.'
        elif not name:
            error = 'Name is required.'
        elif not last_name:
            error = 'Last name is required.'
        elif not birthday_date:
            error = 'Birthday date is required.'
        elif if_user_exists(username):
            error = 'User with username {} already exists.'.format(username)

        if error is None:
            db.execute(
                'insert into user (username, password, email, name, last_name,'
                'birthday_date, is_admin, is_active) values (?,?,?,?,?,?,?,?)',
                (username, generate_password_hash(password), email, name,
                    last_name, birthday_date, is_admin, is_active)
            )
            db.commit()

            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        error = None

        user = db.execute(
            'select * from user where username = ?',
            (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            print(check_password_hash(user['password'], password))
            error = 'Wrong password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']

            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    session.clear()

    return redirect(url_for('index'))
