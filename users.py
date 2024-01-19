from flask import Blueprint, render_template
from flask_login import login_required, current_user

from .user import User

users = Blueprint('users', __name__)

@users.route('/users', methods=['GET']) 
@login_required
def users():
    User.update_last_activity(current_user.id)
    return render_template("users.html")    
