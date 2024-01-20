
from flask_login import UserMixin

from .db import get_db

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
            sql = f"SELECT * FROM user {where} ORDER BY {sort_order} {sort_direction} LIMIT {page_size} OFFSET {page_size*(page_number-1)} ;"
            print(sql)
            cur.execute(sql)
            rows = cur.fetchall()
            
            return [User(row) for row in rows]

    @staticmethod
    def get(id):
        db = get_db()
        with db.cursor() as cur:
            cur.execute("SELECT * FROM user WHERE id = %s", (id))
            row = cur.fetchone()
            if not row:
                return None
            
            return User(row)

    @staticmethod
    def get_by_email(email):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(f"SELECT * FROM user WHERE email = %s", (email))
            row = cur.fetchone()
            if not row:
                return None

            return User(row)

    @staticmethod
    def create(name, email, image, role):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                "INSERT INTO user (name, email, image, role) "
                "VALUES (%s, %s, %s, %s)",
                (name, email, image, role),
            )
        db.commit()

        return User.get_by_email(email)
    

    @staticmethod
    def update_last_activity(id):
        db = get_db()
        with db.cursor() as cur:
            cur.execute("UPDATE user SET last_activity = UTC_TIMESTAMP() WHERE id = %s", (id,))
        db.commit()

    @staticmethod
    def update_last_login(id):
        db = get_db()
        with db.cursor() as cur:
            cur.execute("UPDATE user SET last_login = UTC_TIMESTAMP() WHERE id = %s", (id,))
        db.commit()

