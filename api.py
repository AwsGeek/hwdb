import math

from flask import Blueprint, request, url_for
from flask_login import login_required, current_user

from .user import User

api = Blueprint('api', __name__)

@api.route('/api/users/<int:user_id>', methods=['GET','PUT']) 
@login_required
def user(user_id):
    User.update_last_activity(current_user.id)

    if request.method == 'GET':
        return User.get(user_id)
    elif request.method == "PUT":
        return User.get(user_id)





@api.route('/api/users', methods=['GET']) 
@login_required
def users():

    User.update_last_activity(current_user.id)

    if request.method == 'GET':
        print(request.args)

        page_size = int(request.args.get('page_size', 5) or 5)
        page_number = int(request.args.get('page_number', 1) or 1)
        sort_order = request.args.get('sort_order', 'email')
        sort_direction = request.args.get('sort_direction', 'asc')
        search_phrase = request.args.get('search_phrase', '')
        print(page_number, page_size, sort_order, search_phrase)

        total_users = User.count()
        user_list = User.list(page_size, page_number, sort_order, sort_direction, search_phrase)
        total_pages = math.ceil(total_users / page_size)

        return {
            'user_list': user_list, 
            'total_users': total_users, 
            'current_page': page_number,
            'total_pages': total_pages
        }
