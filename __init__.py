import os
from . import db, auth, admin, pos, dash, customer
from flask import Flask

app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
    SECRET_KEY='dev',
    DATABASE=os.path.join(app.instance_path, 'eLista.sqlite'),
)

# if test_config:
#     app.config.from_mapping(test_config)
# else:
#     app.config.from_pyfile('config.py', silent=True)

os.makedirs(app.instance_path, exist_ok=True)

db.init_app(app)
app.register_blueprint(auth.bp)
app.register_blueprint(admin.bp)
app.register_blueprint(pos.bp)
app.register_blueprint(dash.bp)
app.add_url_rule('/', endpoint='index')
app.register_blueprint(customer.bp)