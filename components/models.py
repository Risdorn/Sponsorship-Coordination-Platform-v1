# This file contains the Roles and Terminologies used in the Sponsorship Coordination Platform.

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

# These are the database models

# Sponsor class, A company/individual who wants to advertise their product
# Can have multiple Campaigns

# Influencer class, A social media influencer who has a large following
# Can recieve multiple Ad_requests
  
class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, unique = True, nullable=False)
    role = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique = True)
    password = db.Column(db.String, nullable=False)
    industry = db.Column(db.String)
    category = db.Column(db.String)
    reach = db.Column(db.Float)
    
# Ad_request class, A request from a sponsor to an influencer to advertise their product
class Ad_request(db.Model):
    __tablename__ = "ad_request"
    id = db.Column(db.Integer, primary_key=True, unique = True, nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    #sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.sponsor_id'), nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    messages = db.Column(db.String, nullable=False)
    requirements = db.Column(db.String, nullable=False)
    payment_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String, nullable=False)
    negotiate = db.Column(db.Boolean, nullable=False, default=False)

# Campaign class, A marketing campaign created by a sponsor to promote their product
# Can contain multiple Ad_requests
class Campaign(db.Model):
    __tablename__ = "campaign"
    id = db.Column(db.Integer, primary_key=True, unique = True, nullable=False)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    #influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.influencer_id'), nullable=False)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    goals = db.Column(db.String, nullable=False)
    niche = db.Column(db.String, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    remaining = db.Column(db.Float, nullable=False)
    visibility = db.Column(db.String, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)

class Flagged(db.Model):
    __tablename__ = "flagged"
    id = db.Column(db.Integer, primary_key=True, unique = True, nullable=False)
    type = db.Column(db.String, nullable=False)
    type_id = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String, nullable=False)