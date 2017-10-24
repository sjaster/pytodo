import os
import sqlite3
from flask import Flask, g

class Database: 

    def __init__(self, app):
        self.app = app
        self.app.teardown_appcontext(self.close_db)
        app.config.update(dict(DATABASE=os.path.join(app.root_path, 'db/db.sqlite3')))

    def init_db(self):
        self.db = self.get_db()
        with self.app.open_resource('db/schema.sql', mode='r') as f:
            self.db.cursor().executescript(f.read())
        self.db.commit()

    def connect_db(self):
        """Connects to the specific database."""
        db = sqlite3.connect(self.app.config['DATABASE'])
        db.row_factory = sqlite3.Row
        return db

    def get_db(self):
        if not hasattr(g, 'db.sqlite3'):
            g.sqlite_db = self.connect_db()
        return g.sqlite_db

    def close_db(self,error):
        if hasattr(g, 'db.sqlite3'):
            g.sqlite_db.close()


    def query_db(self, query, args=(), one=False):
        cur = self.get_db().execute(query, args)
        rv = cur.fetchall()
        cur.close()
        return (rv[0] if rv else None) if one else rv
