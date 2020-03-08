from flask import Blueprint, render_template, redirect, url_for, request
from datetime import date

from .db import get_db
from .auth import admin_required

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
                    'select id '
                    'from user '
                    'where is_active = 1 and id != ?',
                    (user_id,)
                ).fetchall()

                for user in active_users:
                    # this will skip the man who has birthday
                    if user['id'] == user_id:
                        continue

                    db.execute(
                        'insert into Payment (birthday_id, user_id, is_paid) '
                        'values (?,?,?)',
                        (birthday_id['id'], user['id'], 0)
                    )
                    db.commit()

    return redirect(url_for('home.index'))


@bp.route('/edit/<int:id>', methods=('GET', 'POST'))
@admin_required
def edit(id):
    db = get_db()

    birthday = db.execute(
        'select birthday.id, birthday.current_birthday_date, '
        'user.name, user.last_name '
        'from birthday '
        'join user on birthday.user_id=user.id '
        'where birthday.id = ?',
        (id,)
    ).fetchone()

    if birthday is None:
        abort(404, "This birthday doesn't exist.")

    payments = db.execute(
        'select Payment.user_id, Payment.is_paid, user.name, user.last_name '
        'from Payment '
        'join user on Payment.user_id=user.id '
        'where birthday_id = ? '
        'order by user.name desc, user.last_name desc',
        (birthday['id'],)
    ).fetchall()

    if request.method == 'POST':
        checkboxes = request.form.getlist('payment')

        if len(checkboxes) != 0:
            for user_id in checkboxes:
                db.execute(
                    'update Payment set is_paid = 1 '
                    'where user_id = ? and birthday_id = ?',
                    (user_id, birthday['id'])
                )
                db.commit()

        return redirect(url_for('birthday.edit', id=id))

    return render_template('birthday/edit.html',
                            birthday=birthday,
                            payments=payments)
