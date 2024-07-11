from .models import *
from app import db
from datetime import datetime, date


def sponsor_register(name, email, password, industry):
    sponsor = User(name=name, email=email, password=password, industry=industry, role="Sponsor")
    db.session.add(sponsor)
    db.session.commit()
    return sponsor

def get_sponsor(email):
    sponsor = User.query.filter_by(email=email).first()
    return sponsor

def update_sponsor(name, email, password, industry):
    sponsor = get_sponsor(email)
    sponsor.name = name
    sponsor.password = password
    sponsor.industry = industry
    db.session.commit()
    return sponsor

def get_campaigns(email):
    sponsor = User.query.filter_by(email=email).first()
    campaigns = Campaign.query.filter_by(sponsor_id=sponsor.id).all()
    for campaign in campaigns:
        today = date.today()
        if campaign.end_date > today and campaign.start_date < today:
            campaign.progress = (today - campaign.start_date) / (campaign.end_date - campaign.start_date) * 100
            campaign.progress = round(campaign.progress, 2)
        elif campaign.end_date < today:
            campaign.progress = 100
        else:
            campaign.progress = 0
    return campaigns

def get_public_campaigns():
    campaigns = Campaign.query.filter_by(visibility="Public").all()
    for campaign in campaigns:
        today = date.today()
        if campaign.end_date > today and campaign.start_date < today:
            campaign.progress = (today - campaign.start_date) / (campaign.end_date - campaign.start_date) * 100
            campaign.progress = round(campaign.progress, 2)
        elif campaign.end_date < today:
            campaign.progress = 100
        else:
            campaign.progress = 0
    return campaigns

def create_campaign(email, name, description, start_date, end_date, budget, visibility, goals):
    sponsor = get_sponsor(email)
    campaign = Campaign(sponsor_id=sponsor.id, name=name, description=description, start_date=start_date, end_date=end_date, budget=budget, visibility=visibility, goals=goals)
    db.session.add(campaign)
    db.session.commit()
    return campaign

def update_campaign(campaign_id, name, description, start_date, end_date, budget, visibility, goals):
    campaign = Campaign.query.filter_by(id=campaign_id).first()
    campaign.name = name
    campaign.description = description
    campaign.start_date = start_date
    campaign.end_date = end_date
    campaign.budget = budget
    campaign.visibility = visibility
    campaign.goals = goals
    db.session.commit()
    return campaign

def delete_campaign(campaign_id):
    campaign = Campaign.query.filter_by(id=campaign_id).first()
    db.session.delete(campaign)
    db.session.commit()

def get_ad_requests_campaign(email):
    campaigns = get_campaigns(email)
    ad_request_ids = [campaign.id for campaign in campaigns]
    ad_requests = Ad_request.query.filter(Ad_request.campaign_id.in_(ad_request_ids)).all()
    for ad_request in ad_requests:
        ad_request.name = Campaign.query.filter_by(id=ad_request.campaign_id).first().name
        ad_request.influencer_name = User.query.filter_by(id=ad_request.influencer_id).first().name
    return ad_requests

def create_ad_request(influencer_id, campaign_id, messages, requirements, payment_amount, status, negotiate):
    ad_request = Ad_request(influencer_id=influencer_id, campaign_id=campaign_id, messages=messages, requirements=requirements,
                            payment_amount=payment_amount, status=status, negotiate=negotiate)
    db.session.add(ad_request)
    db.session.commit()
    return ad_request

def update_ad_request(ad_request_id, status):
    ad_request = Ad_request.query.filter_by(id=ad_request_id).first()
    ad_request.status = status
    ad_request.negotiate = True
    db.session.commit()
    return ad_request

def delete_ad_request(ad_request_id):
    ad_request = Ad_request.query.filter_by(id=ad_request_id).first()
    db.session.delete(ad_request)
    db.session.commit()