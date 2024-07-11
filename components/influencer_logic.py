from .models import User, Ad_request
from app import db


def influencer_register(name, email, password, category, reach):
    influencer = User(name=name, email=email, password=password, category=category, reach=reach, role="Influencer")
    db.session.add(influencer)
    db.session.commit()
    return influencer

def get_influencer(email):
    influencer = User.query.filter_by(email=email).first()
    return influencer

def all_influencers():
    influencers = User.query.filter_by(role="Influencer").all()
    return influencers

def update_influencer(name, email, password, category, reach):
    influencer = get_influencer(email)
    influencer.name = name
    influencer.password = password
    influencer.category = category
    influencer.reach = reach
    db.session.commit()
    return influencer

def get_ad_requests_influencer(email):
    influencer = User.query.filter_by(email=email).first()
    ad_requests = Ad_request.query.filter_by(influencer_id=influencer.id).all()
    return ad_requests

def negotiate_ad_request(ad_request_id, payment_amount):
    ad_request = Ad_request.query.filter_by(id = ad_request_id).first()
    ad_request.negotiate = True
    ad_request.payment_amount = payment_amount
    db.session.commit()
    return ad_request