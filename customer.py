from flask import Blueprint, redirect, render_template, request, url_for, flash, session
import segno
from eLista.db import get_db
from datetime import datetime

bp = Blueprint('customer', __name__, url_prefix='/cust')

@bp.route('/', methods=('POST', 'GET'))
def cust():
    return render_template('customer/dash.html')

@bp.route('/history', methods=('POST', 'GET'))
def history():
    db = get_db()
    user_id = session.get('user_id')
    if not user_id:
        flash('User not logged in')
        return redirect(url_for('auth.login'))

    receipts = db.execute(
        'SELECT ts.receipt_id, r.receipt_amount, r.receipt_date '
        'FROM trans_saved ts '
        'INNER JOIN receipt r ON r.receipt_id = ts.receipt_id '
        'WHERE ts.user_id = ?', (user_id,)
    ).fetchall()
    return render_template('customer/history.html', receipts=receipts)

@bp.route('/save_order', methods=('POST',))
def save_order():
    db = get_db()
    user_id = session.get('user_id')
    if not user_id:
        flash('User not logged in')
        session['order'] = request.form['receipt_no']
        return render_template('auth/temp_login.html')
    receipt_no = request.form['receipt_no']

    # insert receipt and user id into trans_saved table
    db.execute ('INSERT INTO trans_saved (user_id, receipt_id) VALUES (?, ?)', (user_id, receipt_no))
    db.commit()

    return redirect(url_for('customer.history'))

@bp.route('/history_detail', methods=('GET',))
def history_detail():
    db = get_db()
    receipt_no = request.args.get('receipt_no')
    if not receipt_no:
        flash('Invalid receipt number')
        return redirect(url_for('customer.history'))
    items = db.execute(
        'SELECT qr_code, item_name, price FROM item INNER JOIN trans ON trans.item_id = item.item_id WHERE trans.receipt_id = ?', (receipt_no,)
    ).fetchall()
    total_amount = sum(item['price'] for item in items)
    return render_template('customer/history_detail.html', items=items, total_amount=total_amount, receipt_no=receipt_no)