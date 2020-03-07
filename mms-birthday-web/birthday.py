from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from datetime import date

from .db import get_db

bp = Blueprint('birthday', __name__, url_prefix='/birthday')


def check_todays_birthdays():
    '''
    Check if someone has a birthday today and return user_id.
    Otherwise return None.
    '''
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
            return birthday['id']

    return None


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


def create_birthday():
    user_id = check_todays_birthdays()
    today = date.today().strftime("%d/%m/%Y")
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
