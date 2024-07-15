from .models import db, User
import re

def validate_form(name, email, password, con_pass, reach = None, role = None):
    # Make sure all fields are filled
    if not name or not email or not password or not con_pass: return False
    # Make sure password and confirm password match
    if password != con_pass: return False
    # For Influencers, make sure reach is a number
    if (role and role == "Influencer") and (not reach or not re.search(r'^\d+$', reach)): return False
    # For all users, make sure name, email and password is valid
    name = re.search(r'^[\w\-\s]+$', name)
    email = re.search(r'^[\w\.\-]+@[\w\.\-]+\.\w+$', email)
    password = re.search(r'^(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])(?=.*\W)(?!.* ).{8,}$', password)
    if not name or not email or not password:
        return False
    return True

def validate_user(email, password):
    # Check if user exists
    user = User.query.filter_by(email=email, password=password).first()
    return user

def create_user(name, email, password, role, industry = None, category = None, reach = None):
    # Create user
    user = User(name=name, email=email, password=password, industry=industry, category=category, reach=reach, role=role)
    db.session.add(user)
    db.session.commit()
    return user

def get_user(email, id = None):
    # Get user
    # If id is provided, get user by id
    if id:
        user = User.query.filter_by(id=id).first()
        return user
    user = User.query.filter_by(email=email).first()
    return user

def update_user(email, params):
    # Update user
    user = get_user(email)
    for key in params:
        if not params[key]: continue
        setattr(user, key, params[key])
    db.session.commit()
    return user

def search_user(name, reach, category):
    # Search via name
    if name:
        users = User.query.filter(User.name.like('%' + name + '%')).filter_by(role="Influencer").all()
    else:
        users = User.query.filter_by(role="Influencer").all()
    # Only send requested categories
    if category:
        users = [user for user in users if user.category in category]
    # Sort based on reach
    if reach == "Low":
        users = sorted(users, key=lambda x: x.reach, reverse=True)
    elif reach == "High":
        users = sorted(users, key=lambda x: x.reach)
    return users
        