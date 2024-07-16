from .models import db, Ad_request
import re

def validate_ad_request(messages, requirements, payment_amount):
    # Check if all fields are filled
    if not messages or not requirements or not payment_amount: return False
    # Check if payment amount is a number
    if not re.search(r'^\d+(\.\d+)?$', payment_amount): return False
    return True

def create_ad_request(messages, requirements, payment_amount, status, negotiate, campaign_id, influencer_id = None):
    # Create ad request
    # Influencer_id is optional, empty ad requests which will be filled by influencers
    ad_request = Ad_request(campaign_id=campaign_id, influencer_id=influencer_id, messages=messages, 
                            requirements=requirements, payment_amount=payment_amount, status=status, negotiate=negotiate)
    db.session.add(ad_request)
    db.session.commit()
    return ad_request

def get_ad_request(ad_request_id):
    # Get ad request
    ad_request = Ad_request.query.filter_by(id=ad_request_id).first()
    return ad_request

def update_ad_request(ad_request_id, params):
    # Update ad request
    ad_request = get_ad_request(ad_request_id)
    for key in params:
        if not params[key]: continue
        setattr(ad_request, key, params[key])
    db.session.commit()
    return ad_request

def delete_ad_request(ad_request_id):
    # Delete ad request
    ad_request = get_ad_request(ad_request_id)
    db.session.delete(ad_request)
    db.session.commit()
    return ad_request

def get_ad_requests(page):
    # Get all ad requests
    if page == -1:
        ad_requests = Ad_request.query.all()
        return ad_requests
    ad_requests = Ad_request.query.paginate(page=page, per_page=5, error_out=False)
    return ad_requests

def get_campaign_ad_requests(campaign_id, page):
    # Get ad requests associated with campaign
    if page == -1:
        ad_requests = Ad_request.query.filter_by(campaign_id=campaign_id)
        return ad_requests
    ad_requests = Ad_request.query.filter(Ad_request.campaign_id.in_(campaign_id)).paginate(page=page, per_page=5, error_out=False)
    return ad_requests

def get_influencer_ad_requests(influencer_id, page):
    # Get ad requests associated with influencer
    if page == -1:
        ad_requests = Ad_request.query.filter_by(influencer_id=influencer_id)
        return ad_requests
    ad_requests = Ad_request.query.filter_by(influencer_id=influencer_id).paginate(page=page, per_page=5, error_out=False)
    return ad_requests