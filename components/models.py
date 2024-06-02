# This file contains the Roles and Terminologies used in the Sponsorship Coordination Platform.

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# These are the database models

# Sponsor class, A company/individual who wants to advertise their product
# Can have multiple Campaigns
class Sponsor(db.Model):
    __tablename__ = "sponsor"
    sponsor_id = db.Column(db.Integer, primary_key=True, unique = True, nullable=False)
    name = db.Column(db.String, nullable=False)
    industry = db.Column(db.String, nullable=False)
    budget = db.Column(db.String, nullable=False)

# Influencer class, A social media influencer who has a large following
# Can recieve multiple Ad_requests
class Influencer(db.Model):
    __tablename__ = "influencer"
    influencer_id = db.Column(db.Integer, primary_key=True, unique = True, nullable=False)
    name = db.Column(db.String, nullable=False, unique = True)
    category = db.Column(db.String, nullable=False)
    niche = db.Column(db.String, nullable=False)
    reach = db.Column(db.Float, nullable=False)

# Ad_request class, A request from a sponsor to an influencer to advertise their product
class Ad_request(db.Model):
    __tablename__ = "ad_request"
    ad_request_id = db.Column(db.Integer, primary_key=True, unique = True, nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.influencer_id'), nullable=False)
    #sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.sponsor_id'), nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.campaign_id'), nullable=False)
    messages = db.Column(db.String, nullable=False)
    requirements = db.Column(db.String, nullable=False)
    payment_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String, nullable=False)

# Campaign class, A marketing campaign created by a sponsor to promote their product
# Can contain multiple Ad_requests
class Campaign(db.Model):
    __tablename__ = "campaign"
    campaign_id = db.Column(db.Integer, primary_key=True, unique = True, nullable=False)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.sponsor_id'), nullable=False)
    #influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.influencer_id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    visibility = db.Column(db.String, nullable=False)
    goals = db.Column(db.String, nullable=False)


""" # Put this in app.py to create dummy data 
    # Dummy data
    sponsor1 = Sponsor(name="Company A", industry="Fashion", budget="1000")
    sponsor2 = Sponsor(name="Company B", industry="Tech", budget="2000")
    influencer1 = Influencer(name="Influencer X", category="Fashion", niche="Streetwear", reach=100000)
    influencer2 = Influencer(name="Influencer Y", category="Tech", niche="Gadgets", reach=50000)
    campaign1 = Campaign(sponsor_id=1, start_date=datetime(2021,1,1), end_date=datetime(2021,1,31), budget=500, visibility="public", goals="Increase brand awareness")
    campaign2 = Campaign(sponsor_id=2, start_date=datetime(2021,2,1), end_date=datetime(2021,2,28), budget=1000, visibility="private", goals="Drive sales")
    campaign3 = Campaign(sponsor_id=2, start_date=datetime(2021,3,1), end_date=datetime(2021,3,31), budget=1500, visibility="public", goals="Increase brand awareness")
    ad_request1 = Ad_request(influencer_id=1, campaign_id=1, messages="Hi, we would like to collaborate with you!", requirements="1 Instagram post, 1 Instagram story", payment_amount=100, status="Pending")
    ad_request2 = Ad_request(influencer_id=2, campaign_id=2, messages="Hello, we have a new product launch coming up!", requirements="1 YouTube video review", payment_amount=200, status="Accepted")

    # Add the data to the session
    db.session.add(sponsor1)
    db.session.add(sponsor2)
    db.session.add(influencer1)
    db.session.add(influencer2)
    db.session.add(campaign1)
    db.session.add(campaign2)
    db.session.add(campaign3)
    db.session.add(ad_request1)
    db.session.add(ad_request2)

    # Commit the changes
    db.session.commit()"""