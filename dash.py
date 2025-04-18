from flask import (
    Blueprint, render_template, session
)

bp = Blueprint('dash', __name__)

@bp.route('/')
def index():
    session['order'] = []
    return render_template('dash/index.html')