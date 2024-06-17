# This is the main file for the Sponsorship Coordination Platform. It is a Flask application that serves the back-end

from flask import Flask, render_template, request, redirect, url_for

from components.models import db, Sponsor, Influencer, Ad_request, Campaign

import os
from datetime import datetime


app = Flask(__name__)

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance/sponsorship_platform.db')

# Initialize the database
db.init_app(app)

# Create the database tables
with app.app_context():
    # If the database does not exist, create it
    db.create_all()

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
        sponsors = Sponsor.query.all()
        influencers = Influencer.query.all()
        ad_requests = Ad_request.query.all()
        campaigns = Campaign.query.all()
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
        return redirect(url_for('admin'))

# Login page, Allows users to login to the platform
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        # Get the login page
        return render_template('login.html')
    elif request.method == 'POST':
        # Get the login credentials and check if they are correct
        email = request.form['email']
        password = request.form['password']
        sponsor = Sponsor.query.filter_by(email=email).first()
        influencer = Influencer.query.filter_by(email=email).first()
        # If the user is a sponsor, redirect to the sponsor dashboard
        # If the user is an influencer, redirect to the influencer dashboard
        if sponsor and sponsor.password == password:
            return redirect(url_for('sponsor_dashboard', sponsor_id=sponsor.sponsor_id))
        elif influencer and influencer.password == password:
            return redirect(url_for('influencer_dashboard', influencer_id=influencer.influencer_id))
        
        return render_template('login.html', error='Email or Password is incorrect, please try again')

# Register page, Allows users to register to the platform
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        # Get the register page
        return render_template('register.html')
    elif request.method == 'POST':
        # Get the registration details and create a new user
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        type = request.form['type']
        #print(type)
        if type == 'Sponsor':
            industry = request.form['industry']
            sponsor = Sponsor(email=email, password=password, name=name, industry=industry)
            db.session.add(sponsor)
            db.session.commit()
            return redirect(url_for('sponsor_dashboard', sponsor_id=sponsor.sponsor_id))
        elif type == 'Influencer':
            category = request.form['category']
            niche = request.form['niche']
            reach = request.form['reach']
            influencer = Influencer(email=email, password=password, name=name, category=category, niche=niche, reach=reach)
            db.session.add(influencer)
            db.session.commit()
            return redirect(url_for('influencer_dashboard', influencer_id=influencer.influencer_id))

# Sponsor dashboard, Allows sponsors to view their campaigns and create new campaigns
@app.route('/sponsor/<int:sponsor_id>', methods=['GET', 'POST'])
def sponsor_dashboard(sponsor_id):
    sponsor = Sponsor.query.filter_by(sponsor_id=sponsor_id).first()
    if request.method == 'GET':
        # Get the sponsor dashboard
        campaigns = Campaign.query.filter_by(sponsor_id=sponsor_id).all()
        ad_request_ids = [campaign.campaign_id for campaign in campaigns]
        ad_requests = Ad_request.query.filter(Ad_request.campaign_id.in_(ad_request_ids)).all()
        return render_template('sponsor_dashboard.html', sponsor=sponsor, campaigns=campaigns, ad_requests=ad_requests)
    elif request.method == 'POST' and request.form['form_id'] == 'edit_profile':
        sponsor = Sponsor.query.filter_by(sponsor_id=sponsor_id).first()
        sponsor.name = request.form['name']
        sponsor.industry = request.form['industry']
        db.session.commit()
        return redirect(url_for('sponsor_dashboard', sponsor_id=sponsor_id))
    elif request.method == 'POST' and request.form['form_id'] == 'campaign':
        # Create a new campaign
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
        budget = request.form['budget']
        visibility = request.form['visibility']
        goals = request.form['goals']
        name = request.form['name']
        campaign = Campaign(name=name, start_date=start_date, end_date=end_date, visibility=visibility, goals=goals, budget=budget, sponsor_id=sponsor_id)
        db.session.add(campaign)
        db.session.commit()
        return redirect(url_for('sponsor_dashboard', sponsor_id=sponsor_id))
    elif request.method == 'POST' and request.form['form_id'] == 'ad_request':
        ad_request_id = request.form['ad_request_id']
        status = request.form["status"]
        ad_request = Ad_request.query.filter_by(ad_request_id = ad_request_id).first()
        ad_request.status = status + "ed"
        ad_request.sent_to_influencer = True
        db.session.commit()
        return redirect(url_for('sponsor_dashboard', sponsor_id=sponsor_id))
    elif request.method == 'POST' and request.form['form_id'] == 'edit':
        # Edit a campaign
        campaign_id = request.form['campaign_id']
        campaign = Campaign.query.filter_by(campaign_id=campaign_id).first()
        campaign.start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        campaign.end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
        campaign.budget = request.form['budget']
        campaign.visibility = request.form['visibility']
        campaign.goals = request.form['goals']
        campaign.name = request.form['name']
        db.session.commit()
        return redirect(url_for('sponsor_dashboard', sponsor_id=sponsor_id))
    elif request.method == 'POST' and request.form['form_id'] == 'delete':
        # Delete a campaign
        campaign_id = request.form['campaign_id']
        campaign = Campaign.query.filter_by(campaign_id=campaign_id).first()
        db.session.delete(campaign)
        db.session.commit()
        return redirect(url_for('sponsor_dashboard', sponsor_id=sponsor_id))
    elif request.method == 'POST' and request.form['form_id'] == 'search':
        # Searching for Influencers
        return redirect(url_for('search', type='influencer', id=sponsor_id))

# Influencer dashboard, Allows influencers to view their ad requests and create new ad requests
@app.route('/influencer/<int:influencer_id>', methods=['GET', 'POST'])
def influencer_dashboard(influencer_id):
    influencer = Influencer.query.filter_by(influencer_id=influencer_id).first()
    if request.method == 'GET':
        # Get the influencer dashboard
        ad_requests = Ad_request.query.filter_by(influencer_id=influencer_id).all()
        return render_template('influencer_dashboard.html', influencer=influencer, ad_requests=ad_requests)
    elif request.method == 'POST' and request.form['form_id'] == 'edit_profile':
        influencer = Influencer.query.filter_by(influencer_id=influencer_id).first()
        influencer.name = request.form['name']
        influencer.category = request.form['category']
        influencer.niche = request.form['niche']
        influencer.reach = request.form['reach']
        db.session.commit()
        return redirect(url_for('influencer_dashboard', influencer_id=influencer_id))
    elif request.method == 'POST' and request.form['form_id'] == 'ad_request':
        # Accept or Reject an ad request
        ad_request_id = request.form['ad_request_id']
        status = request.form["status"] + "ed"
        ad_request = Ad_request.query.filter_by(ad_request_id = ad_request_id).first()
        ad_request.status = status
        db.session.commit()
        return redirect(url_for('influencer_dashboard', influencer_id=influencer_id))
    elif request.method == 'POST' and request.form['form_id'] == 'negotiate':
        ad_request_id = request.form['ad_request_id']
        ad_request = Ad_request.query.filter_by(ad_request_id = ad_request_id).first()
        ad_request.payment_amount = request.form['payment_amount']
        ad_request.messages = request.form['messages']
        ad_request.requirements = request.form['requirements']
        ad_request.status = "Pending"
        ad_request.sent_to_influencer = False
        db.session.commit()
        return redirect(url_for('influencer_dashboard', influencer_id=influencer_id))
    elif request.method == 'POST' and request.form['form_id'] == 'search':
        # Searching for Campaigns
        return redirect(url_for('search', type='campaign', id=influencer_id))

# Search page, Allows users to search for influencers and sponsors
@app.route('/search/<string:type>/<int:id>', methods=['GET', 'POST'])
def search(type, id):
    if request.method == 'GET':
        # Get the search page
        if type == 'influencer':
            influencers = Influencer.query.all()
            campaigns = Campaign.query.filter_by(sponsor_id=id).all()
        elif type == 'campaign':
            influencers = []
            campaigns = Campaign.query.filter_by(visibility="public").all()
        return render_template('search.html', type = type, id=id, influencers=influencers, campaigns=campaigns)
    elif request.method == 'POST' and request.form['form_id'] == 'search':
        # Get the search query and return the search results
        query = request.form['query']
        sort = request.form['sort']
        if type == 'influencer':
            influencers = Influencer.query.all()
            campaigns = Campaign.query.filter_by(sponsor_id=id).all()
        elif type == 'campaign':
            influencers = None
            campaigns = Campaign.query.filter_by(visibility="public").all()
        
        if sort == 'reach':
            influencers = Influencer.query.filter(Influencer.name.like('%' + query + '%')).order_by(Influencer.reach.desc()).all()
        elif sort == 'category':
            influencers = Influencer.query.filter(Influencer.name.like('%' + query + '%')).order_by(Influencer.category).all()
        elif sort == 'budget':
            campaigns = Campaign.query.filter(Campaign.name.like('%' + query + '%')).filter_by(visibility="public").order_by(Campaign.budget.desc()).all()
        return render_template('search.html', type=type, id=id, influencers=influencers, campaigns = campaigns)
    
    elif request.method == 'POST' and request.form['form_id'] == 'ad_request':
        # Create a new ad request
        influencer_id = request.form.get('influencer_id')
        campaign_id = request.form['campaign_id']
        messages = request.form['message']
        requirements = request.form['requirements']
        payment_amount = request.form['payment_amount']
        ad_request = Ad_request(influencer_id=influencer_id, campaign_id=campaign_id, messages=messages, requirements=requirements, payment_amount=payment_amount, sent_to_influencer=True, status='Pending')
        db.session.add(ad_request)
        db.session.commit()
        return redirect(url_for('search', id=id, type=type))

if __name__ == '__main__':
    app.run(debug=True)