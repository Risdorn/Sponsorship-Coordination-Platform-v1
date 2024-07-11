from .models import *
from app import db

def login_user_man(email, password):
    user = User.query.filter_by(email=email, password=password).first()
    return user

def all_sponsors():
    sponsors = User.query.filter_by(role="Sponsor").all()
    return sponsors

def all_influencers():
    influencers = User.query.filter_by(role="Influencer").all()
    return influencers

def all_campaigns():
    campaigns = Campaign.query.all()
    return campaigns

def all_ad_requests():
    ad_requests = Ad_request.query.all()
    return ad_requests