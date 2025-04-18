from flask import Blueprint, flash, redirect, render_template, request, url_for

from eLista.auth import login_required
from eLista.db import get_db

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/dash')
@login_required
def dash():
    return render_template('admin/admin.html')

def get_product(db, product_code):
    """Retrieve product from the database."""
    return db.execute('SELECT * FROM item WHERE qr_code = ?', (product_code,)).fetchone()

def validate_product_form(product_code, product_name, product_price):
    """Validate product form inputs."""
    if not product_code:
        return 'Product Code is required.'
    if not product_name:
        return 'Product Name is required.'
    if not product_price:
        return 'Product Price is required.'
    return None

@bp.route('/search', methods=('GET', 'POST'))
@login_required
def search():
    if request.method == 'POST':
        product_code = request.form['p_code']
        db = get_db()

        product = get_product(db, product_code)
        if product is None:
            flash("Product doesn't exist")
            return redirect(url_for('admin.dash'))

        return render_template('admin/search.html', product=product)

    return redirect(url_for('admin.dash'))

@bp.route('/add', methods=('GET', 'POST'))
@login_required
def add():
    if request.method == 'POST':
        product_code = request.form['p_code']
        product_name = request.form['p_name']
        product_price = request.form['p_price']
        db = get_db()

        error = validate_product_form(product_code, product_name, product_price)
        if error is None:
            try:
                db.execute(
                    "INSERT INTO item (qr_code, item_name, price) VALUES (?, ?, ?)",
                    (product_code, product_name, product_price),
                )
                db.commit()
                return redirect(url_for("admin.dash"))
            except db.IntegrityError:
                error = f"Product Code {product_code} is already registered."

        flash(error)

    return redirect(url_for('admin.dash'))

@bp.route('/remove', methods=('POST',))
@login_required
def remove():
    product_code = request.form['p_code']
    db = get_db()
    db.execute('DELETE FROM item WHERE qr_code = ?', (product_code,))
    db.commit()
    return redirect(url_for('admin.dash'))
