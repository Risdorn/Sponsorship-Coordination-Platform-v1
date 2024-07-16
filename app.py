# This is the main file for the Sponsorship Coordination Platform. It is a Flask application that serves the back-end

from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from components.models import db, User

import os
import sys
from datetime import datetime


app = Flask(__name__)

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance/sponsorship_platform.db')
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(user_id)
    return user

# Initialize the database
db.init_app(app)

# Need to import after db is initialized
from components.user import *
from components.ad_request import *
from components.campaign import *
from components.flag import *
from components.api import api

# Register the api blueprint
app.register_blueprint(api)

# Create the database tables
with app.app_context():
    # If the database does not exist, create it
    db.create_all()
    # Create the admin user if it does not exist
    # Index 1 is used to get the admin user
    admin = get_user("", 1)
    if not admin:
        create_user("Admin", "admin@gmail.com", "Admin@12", "Admin")
    elif admin.role != "Admin":
        print("Something went wrong, the admin user is not an admin")
        sys.exit()

# Login page, Allows users to login to the platform
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        # Get the login page
        return render_template('login.html', error="")
    elif request.method == 'POST':
        # Get the login credentials and check if they are correct
        email = request.form['email']
        password = request.form['pass']
        user = validate_user(email, password)
        if user is None:
            return render_template('login.html', error='Email or Password is incorrect, please try again')
        # If the user is a sponsor, redirect to the sponsor dashboard
        # If the user is an influencer, redirect to the influencer dashboard
        login_user(user)
        if user.role == 'Sponsor':
            return redirect(url_for('sponsor_dashboard'))
        elif user.role == 'Influencer':
            return redirect(url_for('influencer_dashboard'))
        elif user.role == 'Admin':
            return redirect(url_for('admin'))

# Admin dashboard, Allows the admin to view all the data in the platform
@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if request.method == 'GET':
        # Get the admin dashboard
        page_user = request.args.get('page_user', 1, type=int)
        page_ad_request = request.args.get('page_ad_request', 1, type=int)
        page_campaign = request.args.get('page_campaign', 1, type=int)
        page_flag = request.args.get('page_flag', 1, type=int)
        users = get_users(page_user)
        ad_requests = get_ad_requests(page_ad_request)
        campaigns = get_campaigns(page_campaign)
        flags = get_flags(page_flag)
        for i in range(len(flags.items)):
            flags.items[i] = get_user(None, flags.items[i].type_id)
        return render_template('admin.html', users=users, ad_requests=ad_requests, campaigns=campaigns, flagged=flags)
    elif request.method == 'POST' and request.form['form_id'] == 'flag':
        # Flag a user, or a campaign
        id = request.form['id']
        type = request.form['type']
        reason = request.form['reason']
        create_flag(type, id, reason)
        return redirect(url_for('admin'))
    elif request.method == 'POST' and request.form['form_id'] == "remove_flag":
        # Remove a flag
        id = request.form['id']
        type = request.form['type']
        delete_flag(type, id)
        return redirect(url_for('admin'))
    elif request.method == 'POST' and request.form['form_id'] == 'delete_user':
        # Delete a user
        delete_user(request.form['email'])
        return redirect(url_for('admin'))

# Register page, Allows users to register as a Sponsor
@app.route('/register', methods=['GET', 'POST'])
@app.route('/register/sponsor', methods=['GET', 'POST'])
def register_sponsor():
    if request.method == 'GET':
        # Get the register page
        return render_template('register_sponsor.html', error="")
    elif request.method == 'POST':
        # Get the registration details and create a new user
        name = request.form['name']
        email = request.form['email']
        password = request.form['pass']
        confirm = request.form['con_pass']
        industry = request.form['industry']
        # Check if the form is valid
        if not validate_form(name, email, password, confirm):
            return render_template('register_sponsor.html', error='Please fill all fields correctly')
        sponsor = create_user(name, email, password, 'Sponsor', industry=industry)
        login_user(sponsor)
        return redirect(url_for('sponsor_dashboard'))
        
# Register page, Allows users to register as an Influencer
@app.route('/register/influencer', methods=['GET', 'POST'])
def register_influencer():
    if request.method == 'GET':
        # Get the register page
        return render_template('register_influencer.html', error="")
    elif request.method == 'POST':
        # Get the registration details and create a new user
        name = request.form['name']
        email = request.form['email']
        password = request.form['pass']
        reach = request.form['reach']
        category = request.form['category']
        # Check if the form is valid
        if not validate_form(name, email, password, password, reach, 'Influencer'):
            return render_template('register_influencer.html', error='Please fill all fields correctly')
        influencer = create_user(name, email, password, 'Influencer', category=category, reach=reach)
        login_user(influencer)
        return redirect(url_for('influencer_dashboard'))

# Sponsor dashboard, Allows sponsors to view their campaigns and create new campaigns
@app.route('/sponsor/', methods=['GET', 'POST'])
@login_required
def sponsor_dashboard():
    sponsor = current_user
    # Get the sponsor's campaigns and ad requests
    page_campaign = request.args.get('page_campaign', 1, type=int)
    page_ad_request = request.args.get('page_ad_request', 1, type=int)
    error = request.args.get('error', '')
    campaigns = get_sponsor_campaigns(sponsor.id, page_campaign)
    campaign_id = [campaign.id for campaign in campaigns.items]
    ad_requests = get_campaign_ad_requests(campaign_id, page_ad_request)
    for ad_request in ad_requests.items:
        campaign = get_campaign(ad_request.campaign_id)
        ad_request.name = campaign.name
        if not ad_request.influencer_id:
            ad_request.influencer_name = "Not Assigned"
            continue
        influencer = get_user(None, ad_request.influencer_id)
        ad_request.influencer_name = influencer.name
    flag = get_flag(sponsor.id, sponsor.role)
    if request.method == 'GET':
        # Get the sponsor dashboard
        return render_template('sponsor_dashboard.html', sponsor=sponsor, campaigns=campaigns, ad_requests=ad_requests, error=error, flag=flag)
    elif request.method == 'POST' and request.form['form_id'] == 'edit_profile':
        # Update the sponsor profile
        update_user(sponsor.email, {"name": request.form.get('name'), "password": request.form.get('password'), "industry": request.form.get('industry')})
        return redirect(url_for('sponsor_dashboard', error="Profile updated successfully"))
    elif request.method == 'POST' and request.form['form_id'] == 'add_campaign':
        # Create a new campaign
        name = request.form['name']
        description = request.form['description']
        goals = request.form['goals']
        niche = request.form['niche']
        budget = request.form['budget']
        visibility = request.form['visibility']
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
        # Check if the form is valid
        if not validate_campaign(name, description, start_date, end_date, budget, goals):
            return redirect(url_for('sponsor_dashboard.html', error='Please fill all fields correctly'))
        create_campaign(sponsor.id, name, description, start_date, end_date, niche, budget, visibility, goals)
        return redirect(url_for('sponsor_dashboard', error="Campaign created successfully"))
    elif request.method == 'POST' and request.form['form_id'] == 'edit_campaign':
        # Edit a campaign
        campaign_id = request.form.get('id')
        start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d')
        end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d')
        update_campaign(campaign_id, {"name": request.form.get('name'), "description": request.form.get('description'), "start_date": start_date, "end_date": end_date, 
                                      "budget": request.form.get('budget'), "visibility": request.form.get('visibility'), "goals": request.form.get('goals'), "niche": request.form.get('niche')})
        return redirect(url_for('sponsor_dashboard', error="Campaign updated successfully"))
    elif request.method == 'POST' and request.form['form_id'] == 'delete_campaign':
        # Delete a campaign and all its ad requests
        ad_requests = get_campaign_ad_requests([request.form['id']], -1)
        for ad_request in ad_requests:
            delete_ad_request(ad_request.id)
        delete_campaign(request.form['id'])
        return redirect(url_for('sponsor_dashboard', error="Campaign deleted successfully"))
    elif request.method == 'POST' and request.form['form_id'] == 'revert_ad':
        # Accept or Reject an ad request and update the campaign budget
        ad_request = get_ad_request(request.form['id'])
        status = request.form['status']
        # Check if the payment amount is less than or equal to the campaign budget
        if status == 'Accept' and not validate_budget(ad_request.payment_amount, ad_request.campaign_id):
            # If the payment amount exceeds the budget, delete the ad request
            delete_ad_request(ad_request.id)
            return redirect(url_for('sponsor_dashboard', error='Payment amount exceeds budget, deleting ad request'))
        update_ad_request(ad_request.id, {"status": status})
        if status == 'Accept': update_campaign(ad_request.campaign_id, {"remaining": ad_request.payment_amount})
        return redirect(url_for('sponsor_dashboard', error="Ad request updated successfully"))
    elif request.method == 'POST' and request.form['form_id'] == 'edit_ad':
        # Edit an ad request
        if not validate_ad_request(request.form['messages'], request.form['requirements'], request.form['payment_amount']):
            return redirect(url_for('sponsor_dashboard', error='Please fill all fields correctly'))
        update_ad_request(request.form['id'], {"messages": request.form['messages'], "requirements": request.form['requirements'], 
                                               "payment_amount": request.form['payment_amount']})
        return redirect(url_for('sponsor_dashboard', error="Ad request updated successfully"))
    elif request.method == 'POST' and request.form['form_id'] == 'withdraw_ad':
        # Withdraw an ad request
        delete_ad_request(request.form['id'])
        return redirect(url_for('sponsor_dashboard', error="Ad request deleted successfully"))
        

# Influencer dashboard, Allows influencers to view their ad requests and create new ad requests
@app.route('/influencer/', methods=['GET', 'POST'])
@login_required
def influencer_dashboard():
    influencer = current_user
    # Get the influencer's ad requests
    page = request.args.get('page', 1, type=int)
    error = request.args.get('error', '')
    ad_requests = get_influencer_ad_requests(influencer.id, page)
    for ad_request in ad_requests.items:
        campaign = get_campaign(ad_request.campaign_id)
        ad_request.name = campaign.name
        ad_request.influencer_name = influencer.name
    flag = get_flag(influencer.id, influencer.role)
    if request.method == 'GET':
        # Get the influencer dashboard
        return render_template('influencer_dashboard.html', influencer=influencer, ad_requests=ad_requests, error="", flag=flag)
    elif request.method == 'POST' and request.form['form_id'] == 'edit_profile':
        # Update the influencer profile
        update_user(influencer.email, {"name": request.form.get('name'), "password": request.form.get('password'), "category": request.form.get('category'), 
                                       "reach": request.form.get('reach')})
        return redirect(url_for('influencer_dashboard', error="Profile updated successfully"))
    elif request.method == 'POST' and request.form['form_id'] == 'revert_ad':
        # Accept or Reject an ad request and update the campaign budget
        ad_request = get_ad_request(request.form['id'])
        status = request.form['status']
        # Check if the payment amount is less than or equal to the campaign budget
        if status == 'Accept' and not validate_budget(ad_request.payment_amount, ad_request.campaign_id):
            # If the payment amount exceeds the budget, delete the ad request
            delete_ad_request(ad_request.id)
            return redirect(url_for("influencer_dashboard", error='Payment amount exceeds budget, deleting ad request'))
        update_ad_request(ad_request.id, {"status": status})
        if status == 'Accept': update_campaign(ad_request.campaign_id, {"remaining": ad_request.payment_amount})
        return redirect(url_for('influencer_dashboard', error="Ad request updated successfully"))
    elif request.method == 'POST' and request.form['form_id'] == 'negotiate_ad':
        # Negotiate an ad request
        update_ad_request(request.form['id'], {"payment_amount": request.form['payment_amount'], "negotiate": True, "status": "Pending"})
        return redirect(url_for('influencer_dashboard', error="Ad request updated successfully"))

# Campaign page, Allows users to view the details of a campaign
@app.route('/campaign/<id>', methods=['GET', 'POST'])
@login_required
def campaign(id):
    user = current_user
    name = user.name
    page = request.args.get('page', 1, type=int)
    error = request.args.get('error', '')
    # Get the campaign details and ad requests
    campaign = get_campaign(id)
    ad_requests = get_campaign_ad_requests([id], page)
    for ad_request in ad_requests.items:
        if not ad_request.influencer_id:
            ad_request.influencer_name = "Not Assigned"
            ad_request.name = campaign.name
            continue
        influencer = get_user(None, ad_request.influencer_id)
        ad_request.influencer_name = influencer.name
        ad_request.name = campaign.name
    if request.method == 'GET':
        # Get the campaign page
        return render_template('campaign.html', type=user.role, name = name, campaign=campaign, ad_requests=ad_requests, error="")
    elif request.method == 'POST' and request.form['form_id'] == 'add_ad_request':
        # Create a new ad request
        messages = request.form['messages']
        requirements = request.form['requirements']
        payment_amount = request.form['payment_amount']
        # Check if the form is valid
        if not validate_ad_request(messages, requirements, payment_amount):
            return redirect(url_for('campaign', id = id, error='Please fill all fields correctly'))
        create_ad_request(messages, requirements, payment_amount, 'Pending', False, id)
        return redirect(url_for('campaign', id=id))
    elif request.method == 'POST' and request.form['form_id'] == 'send_request':
        # Send a request to an influencer only for Influencers
        payment_amount = request.form['payment_amount']
        update_ad_request(request.form['id'], {"payment_amount": payment_amount, "status": "Pending", "negotiate": True, "influencer_id": user.id})
        return redirect(url_for('campaign', id=id, error="Ad request sent successfully"))
    elif request.method == 'POST' and request.form['form_id'] == 'revert_ad':
        # Accept or Reject an ad request only for Sponsors
        ad_request = get_ad_request(request.form['id'])
        status = request.form['status']
        # Check if the payment amount is less than or equal to the campaign budget
        if status == 'Accept' and not validate_budget(ad_request.payment_amount, ad_request.campaign_id):
            # If the payment amount exceeds the budget, delete the ad request
            delete_ad_request(ad_request.id)
            return redirect(url_for('campaign', id=id, error='Payment amount exceeds budget, deleting ad request'))
        update_ad_request(ad_request, {"status": status})
        if status == 'Accept': update_campaign(ad_request.campaign_id, {"remaining": ad_request.payment_amount})
        return redirect(url_for('campaign', id=id, error="Ad request updated successfully"))
    elif request.method == 'POST' and request.form['form_id'] == 'edit_ad':
        # Edit an ad request only for Sponsors
        update_ad_request(request.form['id'], {"messages": request.form['messages'], "requirements": request.form['requirements'], 
                                              "payment_amount": request.form['payment_amount']})
        return redirect(url_for('campaign', id=id, error="Ad request updated successfully"))
    elif request.method == 'POST' and request.form['form_id'] == 'withdraw_ad':
        # Withdraw an ad request only for Sponsors
        delete_ad_request(request.form['id'])
        return redirect(url_for('campaign', id=id, error="Ad request deleted successfully"))

# Search page, Allows users to search for influencers and sponsors
@app.route('/search/', methods=['GET', 'POST'])
@login_required
def search():
    user = current_user
    # Get the search page
    # Get the search results based on the user's role
    campaign = []
    page = request.args.get('page', 1, type=int)
    if request.method == 'GET' and user.role == 'Influencer':
        campaigns = search_campaign(None, None, None, page)
        return render_template('search.html', type=user.role, results=campaigns, campaign=campaign, id=user.id, error="")
    elif request.method == 'GET' and user.role == 'Sponsor':
        influencers = search_user(None, None, None, page)
        campaign = get_sponsor_campaigns(user.id, -1)
        return render_template('search.html', type=user.role, results=influencers, campaign=campaign, id=None, error="")
    elif request.method == 'POST' and request.form['form_id'] == 'search_name':
        # Search for influencers or campaigns
        name = request.form.get('search')
        sort = request.form.get('sort')
        category = request.form.get('category')
        niche = request.form.get('niche')
        if user.role == 'Sponsor':
            # Search for influencers
            results = search_user(name, sort, category, page)
            campaign = get_sponsor_campaigns(user.id, -1)
        elif user.role == 'Influencer':
            # Search for campaigns
            results = search_campaign(name, sort, niche, page)
        return render_template('search.html', type=user.role, results=results, campaign=campaign, id=user.id, error="")
    elif request.method == 'POST' and request.form['form_id'] == 'ad_request':
        results = search_user(None, None, None, page)
        # Create a new ad request
        influencer_id = request.form.get('id')
        campaign_id = request.form['campaign_id']
        messages = request.form['message']
        requirements = request.form['requirement']
        payment_amount = request.form['payment_amount']
        # Check if the form is valid
        if not validate_ad_request(messages, requirements, payment_amount):
            return redirect(url_for('search', error='Please fill all fields correctly'))
        create_ad_request(messages, requirements, payment_amount, 'Pending', False, campaign_id, influencer_id)
        return redirect(url_for('search', error="Ad request sent successfully"))

@app.route('/logout')
@login_required
def logout():
    # Logout the user
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)