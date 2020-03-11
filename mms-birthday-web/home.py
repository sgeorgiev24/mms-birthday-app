from flask import Blueprint, render_template, g

from .db import get_db

bp = Blueprint('home', __name__)


@bp.route('/')
def index():
    db = get_db()

    user_id = None

    if g.user:
        user_id = g.user['id']

    # the keys are id, current_birthday_date, name, last_name
    birthdays = db.execute(
        'select birthday.id, birthday.current_birthday_date, user.name, '
        'user.last_name '
        'from birthday '
        'join user on birthday.user_id=user.id '
        'where is_active=1 and birthday.user_id != ?'
        'order by birthday.id desc',
        (user_id,)
    ).fetchall()

    return render_template('home/index.html', birthdays=birthdays)
