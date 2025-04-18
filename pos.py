from flask import Blueprint, redirect, render_template, request, url_for, flash, session
import segno
from eLista.db import get_db
from datetime import datetime

bp = Blueprint('pos', __name__, url_prefix='/pos')

# Initialize cart in session if it doesn't exist
def get_cart():
    if 'cart' not in session:
        session['cart'] = []
    return session['cart']

@bp.route('/', methods=('POST', 'GET'))
def pos():
    if request.method == 'POST':
        product_code = request.form['p_code']
        product = get_product(product_code)

        if product:
            cart = get_cart()
            cart.append(product)
            session.modified = True  # Mark session as modified
            return redirect(url_for('pos.update'))
        return render_template('pos/pos.html', error="Product doesn't exist")

    return render_template('pos/pos.html')


@bp.route('/remove', methods=('POST',))
def remove():
    cart = get_cart()
    product_index = int(request.form['p_code'])
    
    if 0 <= product_index < len(cart):
        cart.pop(product_index)
        session.modified = True  # Mark session as modified
    return redirect(url_for('pos.update'))


@bp.route('/update', methods=('GET',))
def update():
    cart = get_cart()
    total_amount = calculate_total(cart)
    return render_template('pos/pos.html', merge=enumerate(cart), total=total_amount)


@bp.route('/checkout', methods=('POST',))
def checkout():
    cart = get_cart()
    if not cart:
        flash("Cart is empty. Please add items before checking out.", 'error')
        return redirect(url_for('pos.pos'))

    try:
        db = get_db()
        receipt_no = get_new_receipt_id(db)
        total_amount = calculate_total(cart)

        # Insert receipt and transaction details
        db.execute(
            'INSERT INTO receipt (receipt_id, receipt_amount, receipt_date) VALUES (?, ?, ?)', ( receipt_no, total_amount, datetime.now())
        )
        db.commit()

        for item in cart:
            db.execute('INSERT INTO trans (item_id, receipt_id) VALUES (?, ?)', (item['item_id'], receipt_no))
        db.commit()

        # Generate QR code
        order_qr = segno.make_qr(f'http://127.0.0.1:5000/pos/order/{receipt_no}')
        temp_cart = session['cart'].copy()

        # Clear cart in session
        session.pop('cart', None)
        
        # Render thank-you page with details
        return render_template('pos/thank_you.html', order_qr=order_qr, total=total_amount, receipt_no=receipt_no, temp_cart=temp_cart)

    except Exception as e:
        flash("Checkout failed. Please try again.", 'error')
        print(e)
        return redirect(url_for('pos.pos'))


@bp.route('/order/<int:receipt_id>')
def order(receipt_id):
    db = get_db()
    products = get_order_items(db, receipt_id)
    total_amount = calculate_total(products)
    return render_template('pos/order.html', products=products, total_amount=total_amount, receipt_id=receipt_id)


def get_product(product_code):
    db = get_db()
    product = db.execute('SELECT * FROM item WHERE qr_code = ?', (product_code,)).fetchone()
    return dict(product) if product else None  # Convert Row to dict


def calculate_total(cart):
    """Calculate the total amount for items in the cart."""
    return sum(item['price'] for item in cart)


def get_new_receipt_id(db):
    """Get the latest receipt ID or start from 0 if none exists."""
    result = db.execute('SELECT COUNT(receipt_id) FROM receipt').fetchone()
    return result[0] if result else 0


def get_order_items(db, receipt_id):
    """Fetch order items based on receipt ID."""
    items = db.execute(
        'SELECT trans.receipt_id, item.qr_code, item.item_name, item.price '
        'FROM item '
        'INNER JOIN trans ON trans.item_id = item.item_id '
        'WHERE trans.receipt_id = ?',
        (receipt_id,)
    ).fetchall()
    return [dict(item) for item in items]  # Convert Rows to dicts