from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_recaptcha import ReCaptcha

app = Flask(__name__)

app.config.from_object(__name__)
app.config.update(dict(SECRET_KEY='dev_key'))
app.config.update(dict(SQLALCHEMY_DATABASE_URI='sqlite:////pytodo/db/db.sqlite3'))
app.config.update(dict(SQLALCHEMY_TRACK_MODIFICATIONS='False'))
app.config.update(dict(RECAPTCHA_ENABLED=True))
app.config.update(dict(RECAPTCHA_SITE_KEY='6Leg0jYUAAAAACe8_cMhVt7_xdcoE9XtnRDNTVse'))
app.config.update(dict(RECAPTCHA_SECRET_KEY='6Leg0jYUAAAAAFgowDmwMu28NYyzE4Fo_3O3X8MH'))

db = SQLAlchemy()

migrate = Migrate(app, db)
db.init_app(app)
db.create_all(app=app)
recaptcha = ReCaptcha(app=app)
