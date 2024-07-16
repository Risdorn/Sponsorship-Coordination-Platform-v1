from .user import *
from .campaign import *
from .ad_request import *
from flask import Blueprint, request, jsonify

api = Blueprint('api', __name__)

# Register the routes
@api.route('/api/user', methods=['GET', 'POST', 'PUT', 'DELETE'])
def user():
    user_id = request.args.get('id')
    if request.method != 'POST' and not user_id: return jsonify({"error": "User ID not provided"}), 400
    user = get_user("", user_id)
    if request.method == 'GET':
        return jsonify(user), 200
    elif request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('pass')
        name = request.form.get('name')
        role = request.form.get('role')
        industry = request.form.get('industry')
        reach = request.form.get('reach')
        category = request.form.get('category')
        if role not in ["Sponser", "Influencer"]: return jsonify({"error": "Invalid role"}), 400
        if role == "Sponser" and not industry: return jsonify({"error": "Invalid industry"}), 400
        if role == "Influencer" and not category: return jsonify({"error": "Invalid category"}), 400
        if not validate_form(name, email, password, password, reach, role): return jsonify({"error": "Invalid form"}), 400
        user = create_user(name, email, password, role, industry, reach, category)
        return jsonify(user), 201
    elif request.method == 'PUT':
        email = request.form.get('email')
        password = request.form.get('pass')
        if not email and not password: return jsonify({"error": "Invalid form"}), 400
        if not validate_user(email, password): return jsonify({"error": "Invalid user"}), 400
        cur_user = get_user(email)
        if cur_user.role != "Admin" or cur_user.id != user.id: return jsonify({"error": "Invalid user"}), 400
        name = request.form.get('name')
        industry = request.form.get('industry')
        reach = request.form.get('reach')
        category = request.form.get('category')
        user = update_user(email, {"name": name, "industry": industry, "reach": reach, "category": category})
        return jsonify(user), 200
    elif request.method == 'DELETE':
        email = request.form.get('email')
        if not email: return jsonify({"error": "Invalid form"}), 400
        cur_user = get_user(email)
        if cur_user.role != "Admin" or cur_user.id != user.id: return jsonify({"error": "Invalid user"}), 400
        delete_user(email)
        return jsonify({"message": "Deleted User Successfully"}), 200

@api.route('/api/campaigns', methods=['GET'])
def campaigns():
    campaigns = get_campaigns(-1)
    return jsonify(campaigns), 200

@api.route('/api/ad_requests', methods=['GET'])
def ad_requests():
    ad_requests = get_ad_requests(-1)
    return jsonify(ad_requests), 200        