import json

from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort

from .db import get_db
from .store import Store
from .casting import Casting

bp = Blueprint("api", __name__)

@bp.route("/api/store/<int:id>", methods=['GET'])
def get(id):
    """Show all the posts, most recent first."""
    db = get_db()
    cur = db.cursor()
    cur.execute(
        f"SELECT * FROM stores WHERE id = {id};"
    )
    store = cur.fetchone()
    cur.close()
    
    store = Store(store)
    return store
    
@bp.route("/api/store/<int:id>", methods=['PUT'])
def put(id):

    store = Store(request.json)

    db = get_db()
    cur = db.cursor()
    sql = f"UPDATE stores SET code = '{store.code}', name = '{store.name}', icon = '{store.icon}' WHERE id = {id} RETURNING *;"
    print(sql)
    cur.execute(sql)
    db.commit()
    store = cur.fetchone()
    cur.close()
    
    return Store(store)

@bp.route("/api/store", methods=['POST'])
def post():

    store = Store(request.json)

    db = get_db()
    cur = db.cursor()
    sql = f"INSERT INTO stores (code, name, icon) VALUES  ('{store.code}', '{store.name}', '{store.icon}') RETURNING *;"
    print(sql)
    cur.execute(sql)
    db.commit()
    store = cur.fetchone()
    cur.close()
    
    return Store(store)


@bp.route("/api/casting/<int:id>", methods=['GET'])
def get_casting(id):
    return Casting.get(id)

@bp.route("/api/castings", methods=['POST'])
def import_castings():
    
    if request.files:
        f = request.files["file"]                    
        if f:
            
            db = get_db()
            cur = db.cursor()

            castings = json.loads(f.read())
            for casting in castings:
                c = Casting(casting)
                cur.execute(
                   "INSERT INTO castings (brand, year, number, name, assortment, recolor, series, mpn, image, store, chase)"
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (c.brand, c.year, c.number, c.name, c.assortment, c.recolor, c.series, c.mpn, c.image, c.store or None, c.chase or None),
                )    
                db.commit()
            cur.close()
            print(casting)
                
    return "OK"