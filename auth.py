import functools

from flask import (
    Blueprint, flash, g, redirect, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from eLista.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        usertype = request.form['usertype']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif not usertype:
            error = 'Type of user is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password, user_type) VALUES (?, ?, ?)",
                    (username, generate_password_hash(password), usertype),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for('admin.dash'))

        flash(error)

    return redirect(url_for('admin.dash'))

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = "User doesn't Exist"
        elif not check_password_hash(user['password'], password):
            error = "Incorrect Password"


        if error is None:
            if session['order']:
                order_url = "/pos/order/" + session['order']
                session.clear()
                session['user_id'] = user['user_id']
                return redirect(order_url)
            session.clear()
            session['user_id'] = user['user_id']
            if user['user_type'] == 'admin':
                return redirect(url_for('admin.dash'))
            elif user['user_type'] == 'customer':
                return redirect(url_for('customer.cust'))
            else:
                return redirect(url_for('pos.pos'))

        flash(error)

    return redirect(url_for('index'))

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE user_id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view