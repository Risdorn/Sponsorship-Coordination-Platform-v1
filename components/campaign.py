from .models import db, Campaign
import re
from datetime import date

def validate_campaign(name, description, start_date, end_date, budget, goals):
    # Check if all fields are filled
    if not name or not description or not start_date or not end_date or not budget or not goals: return False
    # Check if start date is before end date
    if start_date > end_date: return False
    # Check if budget is a number
    if not re.search(r'^\d+(\.\d+)?$', budget): return False
    return True

def validate_budget(payment_amount, id):
    # Check if payment amount is less than or equal to budget
    campaign = get_campaign(id)
    if payment_amount > campaign.remaining: return False
    return True

def create_campaign(sponsor_id, name, description, start_date, end_date, niche, budget, visibility, goals):
    # Create campaign
    campaign = Campaign(sponsor_id=sponsor_id, name=name, description=description, start_date=start_date, 
                        end_date=end_date, niche=niche, budget=budget, remaining=budget, visibility=visibility, goals=goals)
    db.session.add(campaign)
    db.session.commit()
    return campaign

def get_campaign(campaign_id):
    # Get campaign
    campaign = Campaign.query.filter_by(id=campaign_id).first()
    return campaign

def update_campaign(campaign_id, params):
    # Update campaign
    campaign = get_campaign(campaign_id)
    for key in params:
        if not params[key]: continue
        if key == "budget" and params[key] != campaign.budget:
            campaign.remaining = params[key] - (campaign.budget - campaign.remaining)
        if key == "remaining":
            campaign.remaining = campaign.remaining - params[key]
        setattr(campaign, key, params[key])
    db.session.commit()
    return campaign

def delete_campaign(campaign_id):
    # Delete campaign
    campaign = get_campaign(campaign_id)
    db.session.delete(campaign)
    db.session.commit()
    return campaign

def get_campaigns(page):
    # Get all campaigns
    if page == -1:
        campaigns = Campaign.query.all()
        return campaigns
    campaigns = Campaign.query.paginate(page=page, per_page=10, error_out=False)
    return campaigns

def get_sponsor_campaigns(sponsor_id, page):
    # Get campaigns associated with sponsor
    if page == -1:
        campaigns = Campaign.query.filter_by(sponsor_id=sponsor_id)
        return campaigns
    campaigns = Campaign.query.filter_by(sponsor_id=sponsor_id).paginate(page=page, per_page=5, error_out=False)
    return campaigns

def search_campaign(name, budget, niche, page):
    # Search via name
    if name:
        campaigns = Campaign.query.filter(Campaign.name.like('%' + name + '%')).filter_by(visibility="Public").paginate(page=page, per_page=10, error_out=False)
    else:
        campaigns = Campaign.query.filter_by(visibility="Public").paginate(page=page, per_page=5, error_out=False)
    # Make sure end_date has not passed
    today = date.today()
    campaigns.items = [campaign for campaign in campaigns.items if campaign.end_date >= today]
    # Always sort based on end date
    campaigns.items = sorted(campaigns.items, key=lambda x: x.end_date)
    # Filter based on niche
    if niche:
        campaigns.items = [campaign for campaign in campaigns.items if campaign.niche == niche]
    # Sort based on budget
    if budget == "Low":
        campaigns.items = sorted(campaigns.items, key=lambda x: x.budget, reverse=True)
    elif budget == "High":
        campaigns.items = sorted(campaigns.items, key=lambda x: x.budget)
    return campaigns