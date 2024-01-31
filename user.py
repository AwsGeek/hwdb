import math 

from flask import Blueprint, render_template, request, redirect
from flask_login import UserMixin, login_required, current_user

from .db import get_db

bp = Blueprint('users', __name__)


class User(dict, UserMixin):
    def __init__(self, dictionary):
        dict.__init__(self, dictionary)
        for k, v in dictionary.items():
            setattr(self, k, v)

    def is_active(self):
        return self.active

    @staticmethod
    def count():
        db = get_db()
        with db.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS count FROM user")
            row = cur.fetchone()
            if not row:
                return None

            return int(row['count'])

    @staticmethod
    def list(page_size, page_number, sort_order='id', sort_direction='asc',search_phrase=''):
        db = get_db()
        with db.cursor() as cur:
            where = f" WHERE name LIKE '%{search_phrase}%' OR email LIKE '%{search_phrase}%'" if search_phrase else ''
            sql = f"SELECT * FROM users {where} ORDER BY {sort_order} {sort_direction} LIMIT {page_size} OFFSET {page_size*(page_number-1)} ;"
            print(sql)
            cur.execute(sql)
            rows = cur.fetchall()
            
            return [User(row) for row in rows]

    @staticmethod
    def get(id):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(f"SELECT * FROM users WHERE id = {id}")
            row = cur.fetchone()
            if not row:
                return None
            
            return User(row)

    @staticmethod
    def get_by_email(email):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(f"SELECT * FROM users WHERE email = '{email}'")
            row = cur.fetchone()
            if not row:
                return None

            return User(row)

    @staticmethod
    def create(name, email, image, role):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                "INSERT INTO users (name, email, image, role) "
                "VALUES (%s, %s, %s, %s)",
                (name, email, image, role),
            )
        db.commit()

        return User.get_by_email(email)
    

    @staticmethod
    def update_last_activity(id):
        db = get_db()
        with db.cursor() as cur:
            cur.execute("UPDATE users SET last_activity = NOW() WHERE id = %s", (id,))
        db.commit()

    @staticmethod
    def update_last_login(id):
        db = get_db()
        with db.cursor() as cur:
            cur.execute("UPDATE users SET last_login = NOW() WHERE id = %s", (id,))
        db.commit()


@bp.before_request
def update_last_activity():
    User.update_last_activity(current_user.id)

@bp.route('/users', methods=['GET']) 
@login_required
def list():

    page_size = int(request.args.get('page_size', 5) or 5)
    page_number = int(request.args.get('page_number', 1) or 1)
    sort_order = request.args.get('sort_order', 'email')
    sort_direction = request.args.get('sort_direction', 'asc')
    search_phrase = request.args.get('search_phrase', '')

    params = {
        'page_size' : page_size,
        'page_number' : page_number,
        'sort_order' : sort_order,
        'sort_direction' : sort_direction,
        'search_phrase' : search_phrase,

    }

    total_users = User.count()
    users = {
        'count': total_users,
        'list': User.list(page_size, page_number, sort_order, sort_direction, search_phrase)
    }


    total_pages = math.ceil(total_users / page_size)

    num_links = min(math.floor((total_pages*2-1)/2), 7)
    num_links = min(total_pages, 7)

    max_page = page_number+math.floor(num_links/2)
    min_page = page_number-math.floor(num_links/2)
    if min_page < 1:
        max_page = num_links
        min_page = 1        

    if max_page > total_pages:
        min_page = max(1, total_pages-num_links+1)
        max_page = total_pages

    pages = {
        'count': total_pages,
        'prev': max(page_number-1, 1),
        'list': [*range(min_page, max_page+1, 1)],
        'next': min(page_number+1, total_pages),
        'curr': page_number
    }
    return render_template("users/list.html", users=users, pages=pages, params=params)