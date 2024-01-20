import math 

from flask import Blueprint, render_template, request, redirect
from flask_login import login_required, current_user

from .user import User

users = Blueprint('users', __name__)

@users.before_request
def update_last_activity():
    User.update_last_activity(current_user.id)

@users.route('/users', methods=['GET']) 
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