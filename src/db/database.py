import os
import sqlite3
from flask import Flask, g


app = Flask(__name__)

class Database: 

    def __init__(self):
        app.config.update(dict(DATABASE=os.path.join(app.root_path, 'users.db')))

    def init_db(self):
        self.db = self.get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            self.db.cursor().executescript(f.read())
        self.db.commit()

    @app.cli.command('initdb')
    def initdb_command(self):
        self.init_db()
        print('Initialized the database.')

    def connect_db(self):
        """Connects to the specific database."""
        db = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
        return db

    def get_db(self):
        if not hasattr(g, 'users.db'):
            g.sqlite_db = self.connect_db()
        return g.sqlite_db

    @app.teardown_appcontext
    def close_db(error):
        if hasattr(g, 'users.db'):
            g.sqlite_db.close()


    def query_db(self, query, args=(), one=False):
        cur = self.get_db().execute(query, args)
        rv = cur.fetchall()
        cur.close()
        return (rv[0] if rv else None) if one else rv
