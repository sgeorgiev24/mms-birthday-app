from flask import Blueprint, render_template, redirect, url_for
from datetime import date

from .db import get_db

bp = Blueprint('birthday', __name__, url_prefix='/birthday')


def check_todays_birthdays():
    '''
    Check if someone has a birthday today and return list with user_id.
    Otherwise return None.
    '''
    today_birthdays = []
    db = get_db()

    # get all user ids and birthdays
    birthdays_array = db.execute(
        'select id, birthday_date from user'
    ).fetchall()

    # find out if someone has birthday today
    for birthday in birthdays_array:
        today = date.today().strftime("%d/%m")
        birthday_year = birthday['birthday_date'][-4:]

        if today+'/'+birthday_year == birthday['birthday_date']:
            today_birthdays.append(birthday['id'])

    if len(today_birthdays) == 0:
        return None
    else:
        return today_birthdays


def if_birthday_exists(birthday_date, user_id):
    db = get_db()

    birthday_id = db.execute(
            'select id from Birthday where user_id = ? and '
            'current_birthday_date = ?',
            (user_id, birthday_date)
        ).fetchone()

    if birthday_id is None:
        return False
    else:
        return True


@bp.route('/create')
def create_birthday():
    user_ids = check_todays_birthdays()
    today = date.today().strftime("%d/%m/%Y")

    for user_id in user_ids:
        if user_id is not None:
            # Create birthday
            db = get_db()

            if not if_birthday_exists(today, user_id):
                db.execute(
                    'insert into Birthday (user_id, current_birthday_date) '
                    'values (?,?)',
                    (user_id, today)
                )
                db.commit()

                birthday_id = db.execute(
                    'select id from Birthday where user_id = ? and '
                    'current_birthday_date = ?',
                    (user_id, today)
                ).fetchone()

                active_users = db.execute(
                    'select id from user where is_active = 1'
                ).fetchall()

                for user in active_users:
                    db.execute(
                        'insert into Payment (birthday_id, user_id, is_paid) '
                        'values (?,?,?)',
                        (birthday_id['id'], user['id'], 0)
                    )
                    db.commit()

    return redirect(url_for('home.index'))
