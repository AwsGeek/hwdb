import math

from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort

from .db import get_db

bp = Blueprint("store", __name__)

class Store(dict):
    def __init__(self, dictionary):
        dict.__init__(self, dictionary)
        for k, v in dictionary.items():
            setattr(self, k, v)


@bp.route("/stores")
def stores():

    page_number = int(request.args.get('page_number', 1))
    page_size = int(request.args.get('page_size', 5))
    sort_order = request.args.get('sort_order', 'asc')
    sort_column = request.args.get('sort_column', 'id')

    db = get_db()
    cur = db.cursor()
    
    cur.execute(
        "SELECT COUNT(*) AS count FROM stores;"
    )
    total_count = cur.fetchone()['count']
    
    sql = f"SELECT * FROM stores ORDER BY {sort_column} {sort_order} LIMIT {page_size} OFFSET {page_size * (page_number-1)};"
    cur.execute(sql)
    stores = cur.fetchall()
    cur.close()
    
    total_pages = math.ceil(total_count / page_size)

    # Pagination
    num_links = min(math.floor((total_pages*2-1)/2), 7)
    num_links = min(total_pages, 7)

    max_page = page_number + math.floor(num_links/2)
    min_page = page_number - math.floor(num_links/2)
    if min_page < 1:
        max_page = num_links
        min_page = 1        

    if max_page > total_pages:
        min_page = max(1, total_pages-num_links+1)
        max_page = total_pages    
    
    pagination = {
        'page_size': page_size,
        'total_pages': total_pages,
        'previous_page': max(page_number-1, 1),
        'page_list': [*range(min_page, max_page+1, 1)],
        'next_page': min(page_number+1, total_pages),
        'current_page': page_number
    }

    
    stores = { 'list':[dict(row) for row in stores], 'total_count': total_count }
    sort = {'column': sort_column, 'order': sort_order}
    
    return render_template("store.html", stores=stores, pagination=pagination, sort=sort)