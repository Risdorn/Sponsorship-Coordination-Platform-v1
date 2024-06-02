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

# Home page