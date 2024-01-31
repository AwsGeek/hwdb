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

bp = Blueprint("casting", __name__)

class Casting(dict):
    def __init__(self, dictionary):
        dict.__init__(self, dictionary)
        for k, v in dictionary.items():
            setattr(self, k, v)
            
    @staticmethod
    def years():
        db = get_db()
        with db.cursor() as cur:

            sql = f"SELECT DISTINCT year FROM castings;"
            cur.execute(sql)
            rows = cur.fetchall()
            
            return [int(row['year']) for row in rows]
        
    @staticmethod
    def brands():
        db = get_db()
        with db.cursor() as cur:

            sql = f"SELECT DISTINCT b.* FROM brands AS b JOIN castings AS c ON b.code = c.brand;"
            cur.execute(sql)
            rows = cur.fetchall()
            
            return [Casting(row) for row in rows]

    @staticmethod
    def stores():
        db = get_db()
        with db.cursor() as cur:

            sql = f"SELECT DISTINCT s.* FROM stores AS s JOIN castings AS c ON s.code = c.store;"
            cur.execute(sql)
            rows = cur.fetchall()
            
            return [Casting(row) for row in rows]

    @staticmethod
    def chases():
        db = get_db()
        with db.cursor() as cur:

            sql = f"SELECT DISTINCT s.* FROM chases AS s JOIN castings AS c ON s.code = c.chase;"
            cur.execute(sql)
            rows = cur.fetchall()
            
            return [Casting(row) for row in rows]

    @staticmethod
    def count(years, brands, search_phrase="", facets=[]):
        
        where = []
        if search_phrase:
            where.append(f"name LIKE '%{search_phrase}%'")
            
        for facet in facets:
            if facets[facet]:
                ins = "','".join(facets[facet].split(','))
                where.append(f"{facet} IN ('{ins}')")

        where = " AND ".join(where)
        if where:
            where = f"WHERE {where}"
        
        db = get_db()
        with db.cursor() as cur:
    
            cur.execute(
                f"SELECT COUNT(*) AS count FROM castings {where};"
            )
            return cur.fetchone()['count']


    @staticmethod
    def get(id):

        db = get_db()
        with db.cursor() as cur:
        
            sql = f"SELECT * FROM castings WHERE id = {id};"
            print(sql)
            cur.execute(sql)
            row = cur.fetchone()

            return Casting(row)


    @staticmethod
    def list(page_number, page_size, sort_order, sort_column, search_phrase, facets):

        where = []
        if search_phrase:
            where.append(f"name LIKE '%{search_phrase}%'")
            
        for facet in facets:
            if facets[facet]:
                ins = "','".join(facets[facet].split(','))
                where.append(f"{facet} IN ('{ins}')")

        where = " AND ".join(where)
        if where:
            where = f"WHERE {where}"


        sorting = {
            "year": "number ASC",
            "number": "year ASC",
            "series": "year ASC, number ASC",
            "name": "year ASC, number ASC"
        }

        sort = f"{sort_column} {sort_order}"
        if sort_column in sorting:
            sort = f"{sort}, { sorting[sort_column] }"
        
        db = get_db()
        with db.cursor() as cur:
        
            sql = f"SELECT * FROM castings {where} ORDER BY {sort} LIMIT {page_size} OFFSET {page_size * (page_number-1)};"
            print(sql)
            cur.execute(sql)
            rows = cur.fetchall()

            return [Casting(row) for row in rows]

@bp.route("/")
def castings():

    page_number = int(request.args.get('page_number', 1))
    page_size = int(request.args.get('page_size', 5))
    sort_order = request.args.get('sort_order', 'asc')
    sort_column = request.args.get('sort_column', 'year')
    years = request.args.get('year', '')
    brands = request.args.get('brand', '')
    stores = request.args.get('store', '')
    chases = request.args.get('chase', '')

    options = {
        'years': {'query':years, 'years':[{'year':x, 'selected': (str(x) in years)} for x in Casting.years()]},
        'brands': {'query':brands, 'brands':[{'brand': x, 'selected': (str(x.code) in brands)} for x in Casting.brands()] },
        'stores': {'query':stores, 'stores':[{'store': x, 'selected': (str(x.code) in stores)} for x in Casting.stores()] },
        'chases': {'query':chases, 'chases':[{'chase': x, 'selected': (str(x.code) in chases)} for x in Casting.chases()] },
    }
    print(options['stores'])
    

    facets = {
        'store': stores,
        'chase': chases,
        'year': years,
        'brand': brands
    }

    castings = Casting.list(page_number, page_size, sort_order, sort_column, "", facets)
    num_castings = Casting.count(years, brands, "", facets)
    
    num_pages = math.ceil(num_castings / page_size)

    # Pagination
    num_links = min(math.floor((num_pages*2-1)/2), 7)
    num_links = min(num_pages, 7)

    max_page = page_number + math.floor(num_links/2)
    min_page = page_number - math.floor(num_links/2)
    if min_page < 1:
        max_page = num_links
        min_page = 1        

    if max_page > num_pages:
        min_page = max(1, num_pages-num_links+1)
        max_page = num_pages    
    
    pagination = {
        'page_size': page_size,
        'num_pages': num_pages,
        'prev_page': max(page_number-1, 1),
        'page_list': [*range(min_page, max_page+1, 1)],
        'next_page': min(page_number+1, num_pages),
        'curr_page': page_number
    }


    sort = {'sort_column': sort_column, 'sort_order': sort_order}

    chases = {}
    db = get_db()
    with db.cursor() as cur:

        sql = f"SELECT * FROM chases;"
        cur.execute(sql)
        rows = cur.fetchall()
        
        chases = [Casting(row) for row in rows]
        chases = {x.code: x for x in chases} 

    stores = {}
    db = get_db()
    with db.cursor() as cur:

        sql = f"SELECT * FROM stores;"
        cur.execute(sql)
        rows = cur.fetchall()
        
        stores = [Casting(row) for row in rows]
        stores = {x.code: x for x in stores} 
        

    for casting in castings:
        if casting['chase']:
            casting['chase-store'] = chases[casting['chase']].icon
            casting['chase-store-tooltip'] = chases[casting['chase']].name
        elif casting['store']:
            casting['chase-store'] = stores[casting['store']].icon
            casting['chase-store-tooltip'] = stores[casting['store']].name


    columns = [
        {'name':'chase-store', 'title':'', 'width':'45px', 'type': 'icon', 'tooltip': 'chase-store-tooltip', 'align':'center'}, 
        {'name':'year', 'title':'Year', 'width':'60px', 'sortable':True, 'align':'center'}, 
        {'name':'mpn', 'title':'MPN', 'width':'70px', 'sortable':True, 'align':'center'}, 
        {'name':'number', 'title':'#', 'width':'65px', 'sortable':True, 'align':'center'}, 
        {'name':'name', 'title':'Casting', 'width':'100%', 'sortable':True, 'align':'left'}, 
        {'name':'series', 'title':'Series', 'sortable':True, 'align':'left'}]

    return render_template("casting.html", castings=castings, num_castings=num_castings, pagination=pagination, sort=sort, options=options, chases=chases, stores=stores, columns=columns)