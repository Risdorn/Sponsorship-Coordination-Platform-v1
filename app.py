# This is the main file for the Sponsorship Coordination Platform. It is a Flask application that serves the back-end

from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from components.models import db, User, Ad_request, Campaign

import os
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

# Create the database tables
with app.app_context():
    # If the database does not exist, create it
    db.create_all()

from components.sponsor_logic import *
from components.influencer_logic import *
from components.general_logic import *

# Home page, Gives a breif description of the platform and provides login and register options
@app.route('/', methods=['GET'])
def home():
    if request.method == 'GET':
        return render_template('home.html')

# Admin login page, Allows the admin to login to the platform
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET':
        # Get the admin login page
        return render_template('admin_login.html')
    elif request.method == 'POST':
        # Get the login credentials and check if they are correct
        email = request.form['email']
        password = request.form['password']
        # If the admin credentials are correct, redirect to the admin dashboard
        if email == 'admin@gmail.com' and password == 'admin':
            return redirect(url_for('admin'))
        return render_template('admin_login.html', error='Email or Password is incorrect, please try again')

# Admin dashboard, Allows the admin to view all the data in the platform
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'GET':
        # Get the admin dashboard
        sponsors = all_sponsors()
        influencers = all_influencers()
        ad_requests = all_ad_requests()
        campaigns = all_campaigns()
        '''
        for campaign in campaigns:
            sponsor = Sponsor.query.filter_by(sponsor_id=campaign.sponsor_id).first()
            campaign.sponsor_name = sponsor.name
        for ad_request in ad_requests:
            influencer = Influencer.query.filter_by(influencer_id=ad_request.influencer_id).first()
            campaign = Campaign.query.filter_by(campaign_id=ad_request.campaign_id).first()
            sponsor = Sponsor.query.filter_by(sponsor_id=campaign.sponsor_id).first()
            ad_request.influencer_name = influencer.name
            ad_request.campaign = campaign.name
            ad_request.sponsor_name = sponsor.name
        return render_template('admin.html', sponsors=sponsors, influencers=influencers, ad_requests=ad_requests, campaigns=campaigns)
    elif request.method == 'POST' and request.form['form_id'] == 'influencer':
        influencer_id = request.form['id']
        influencer = Influencer.query.filter_by(influencer_id=influencer_id).first()
        influencer.flagged = True
        influencer.reason = request.form['reason']
        db.session.commit()
        return redirect(url_for('admin'))
    elif request.method == 'POST' and request.form['form_id'] == 'sponsor':
        sponsor_id = request.form['id']
        sponsor = Sponsor.query.filter_by(sponsor_id=sponsor_id).first()
        sponsor.flagged = True
        sponsor.reason = request.form['reason']
        db.session.commit()
        return redirect(url_for('admin'))
    elif request.method == 'POST' and request.form['form_id'] == 'ad_request':
        ad_request_id = request.form['id']
        ad_request = Ad_request.query.filter_by(ad_request_id=ad_request_id).first()
        ad_request.flagged = True
        ad_request.reason = request.form['reason']
        db.session.commit()
        return redirect(url_for('admin'))
    elif request.method == 'POST' and request.form['form_id'] == 'campaign':
        campaign_id = request.form['id']
        campaign = Campaign.query.filter_by(campaign_id=campaign_id).first()
        campaign.flagged = True
        campaign.reason = request.form['reason']
        db.session.commit()
        return redirect(url_for('admin'))'''

# Login page, Allows users to login to the platform
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        # Get the login page
        return render_template('login.html')
    elif request.method == 'POST':
        # Get the login credentials and check if they are correct
        email = request.form['email']
        password = request.form['pass']
        user = login_user_man(email, password)
        if user is None:
            return render_template('login.html', error='Email or Password is incorrect, please try again')
        # If the user is a sponsor, redirect to the sponsor dashboard
        # If the user is an influencer, redirect to the influencer dashboard
        login_user(user)
        if user.role == 'Sponsor':
            return redirect(url_for('sponsor_dashboard'))
        elif user.role == 'Influencer':
            return redirect(url_for('influencer_dashboard'))

# Register page, Allows users to register to the platform
@app.route('/register', methods=['GET', 'POST'])
@app.route('/register/sponsor', methods=['GET', 'POST'])
def register_sponsor():
    if request.method == 'GET':
        # Get the register page
        return render_template('register_sponsor.html')
    elif request.method == 'POST':
        # Get the registration details and create a new user
        email = request.form['email']
        password = request.form['pass']
        confirm = request.form['con_pass']
        name = request.form['name']
        industry = request.form['industry']
        sponsor = sponsor_register(name, email, password, industry)
        login_user(sponsor)
        return redirect(url_for('sponsor_dashboard'))
        
# Register page, Allows users to register to the platform
@app.route('/register/influencer', methods=['GET', 'POST'])
def register_influencer():
    if request.method == 'GET':
        # Get the register page
        return render_template('register_influencer.html')
    elif request.method == 'POST':
        # Get the registration details and create a new user
        email = request.form['email']
        password = request.form['pass']
        name = request.form['name']
        category = request.form['category']
        reach = request.form['reach']
        influencer = influencer_register(name, email, password, category, reach)
        login_user(influencer)
        return redirect(url_for('influencer_dashboard'))

# Sponsor dashboard, Allows sponsors to view their campaigns and create new campaigns
@app.route('/sponsor/', methods=['GET', 'POST'])
@login_required
def sponsor_dashboard():
    sponsor = current_user
    sponsor_email = sponsor.email
    print(sponsor_email)
    if request.method == 'GET':
        # Get the sponsor dashboard
        campaigns = get_campaigns(sponsor_email)
        ad_requests = get_ad_requests_campaign(sponsor_email)
        return render_template('sponsor_dashboard.html', sponsor=sponsor, campaigns=campaigns, ad_requests=ad_requests)
    elif request.method == 'POST' and request.form['form_id'] == 'edit_profile':
        # Update the sponsor profile
        update_sponsor(request.form['name'], sponsor_email, request.form['password'], request.form['industry'])
        return redirect(url_for('sponsor_dashboard'))
    elif request.method == 'POST' and request.form['form_id'] == 'add_campaign':
        # Create a new campaign
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
        budget = request.form['budget']
        visibility = request.form['visibility']
        goals = request.form['goals']
        name = request.form['name']
        description = request.form['description']
        create_campaign(sponsor_email, name, description, start_date, end_date, budget, visibility, goals)
        return redirect(url_for('sponsor_dashboard'))
    elif request.method == 'POST' and request.form['form_id'] == 'edit_campaign':
        # Edit a campaign
        campaign_id = request.form['id']
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
        update_campaign(campaign_id, request.form['name'], request.form['description'], start_date, end_date, request.form['budget'],
                        request.form['visibility'], request.form['goals'])
        return redirect(url_for('sponsor_dashboard'))
    elif request.method == 'POST' and request.form['form_id'] == 'delete_campaign':
        # Delete a campaign
        delete_campaign(request.form['id'])
        return redirect(url_for('sponsor_dashboard'))
    elif request.method == 'POST' and request.form['form_id'] == 'revert_ad':
        update_ad_request(request.form['id'], request.form['status'])
        return redirect(url_for('sponsor_dashboard'))
    elif request.method == 'POST' and request.form['form_id'] == 'withdraw_ad':
        delete_ad_request(request.form['id'])
        return redirect(url_for('sponsor_dashboard'))
        

# Influencer dashboard, Allows influencers to view their ad requests and create new ad requests
@app.route('/influencer/', methods=['GET', 'POST'])
@login_required
def influencer_dashboard():
    influencer = current_user
    influencer_email = influencer.email
    print(influencer_email)
    if request.method == 'GET':
        # Get the influencer dashboard
        ad_requests = get_ad_requests_influencer(influencer_email)
        return render_template('influencer_dashboard.html', influencer=influencer, ad_requests=ad_requests)
    elif request.method == 'POST' and request.form['form_id'] == 'edit_profile':
        # Update the influencer profile
        update_influencer(request.form['name'], influencer_email, request.form['password'], request.form['category'], request.form['reach'])
        return redirect(url_for('influencer_dashboard'))
    elif request.method == 'POST' and request.form['form_id'] == 'revert_ad':
        update_ad_request(request.form['id'], request.form['status'])
        return redirect(url_for('influencer_dashboard'))
    elif request.method == 'POST' and request.form['form_id'] == 'negotiate_ad':
        negotiate_ad_request(request.form['id'], request.form['payment_amount'])
        return redirect(url_for('influencer_dashboard'))

# Search page, Allows users to search for influencers and sponsors
@app.route('/search/', methods=['GET', 'POST'])
@login_required
def search():
    user = current_user
    influencer = get_influencer(user.email)
    if influencer.role != 'Influencer':
        influencer = None
    if request.method == 'GET' and influencer:
        type = "campaigns"
        campaigns = get_public_campaigns()
        return render_template('search.html', type=type, results=campaigns, campaign=[], id=influencer.id)
    elif request.method == 'GET' and not influencer:
        type = "influencers"
        influencers = all_influencers()
        campaign = get_campaigns(user.email)
        return render_template('search.html', type=type, results=influencers, campaign=campaign, id=None)
    elif request.method == 'POST' and request.form['form_id'] == 'search_name':
        name = request.form['search']
        type = request.form['type']
        if type == 'influencers':
            results = User.query.filter(User.name.like('%' + name + '%')).filter_by(role="Influencer").all()
            campaign = get_campaigns(user.email)
        elif type == 'campaigns':
            results = Campaign.query.filter(Campaign.name.like('%' + name + '%')).all()
            influencer = influencer.id
        return render_template('search.html', type=type, results=results, campaign=campaign, id=influencer)
    elif request.method == 'POST' and request.form['form_id'] == 'ad_request':
        # Create a new ad request
        influencer_id = request.form.get('id')
        campaign_id = request.form['campaign_id']
        messages = request.form['message']
        requirements = request.form['requirement']
        payment_amount = request.form['payment_amount']
        create_ad_request(influencer_id, campaign_id, messages, requirements, payment_amount, 'Pending', False)
        return redirect(url_for('search'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)