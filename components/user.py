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

def delete_user(email):
    # Delete user
    user = get_user(email)
    db.session.delete(user)
    db.session.commit()
    return user

def get_users(page):
    # Get all users
    if page == -1:
        users = User.query.filter(User.role.in_(["Sponsor", "Influencer"])).all()
        return users
    users = User.query.filter(User.role.in_(["Sponsor", "Influencer"])).paginate(page=page, per_page=5, error_out=False)
    return users

def search_user(name, reach, category, page):
    # Search via name
    if name:
        users = User.query.filter(User.name.like('%' + name + '%')).filter_by(role="Influencer").paginate(page=page, per_page=10, error_out=False)
    else:
        users = User.query.filter_by(role="Influencer").paginate(page=page, per_page=5, error_out=False)
    # Only send requested categories
    if category:
        users.items = [user for user in users.items if user.category in category]
    # Sort based on reach
    if reach == "Low":
        users.items = sorted(users.items, key=lambda x: x.reach, reverse=True)
    elif reach == "High":
        users.items = sorted(users.items, key=lambda x: x.reach)
    return users
        