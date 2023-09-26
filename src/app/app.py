#----------------------------------------------------------------------------#
# Main module for the app.  Contains all routes to webpages
#----------------------------------------------------------------------------#

# Flask
from flask import Flask, render_template, request, redirect, send_file, after_this_request
from flask import session, flash, url_for
# from forms import *

# File Upload
from werkzeug.utils import secure_filename

# Utilities
import os
import shutil
from dotenv import load_dotenv

# Load environment variables
# load_dotenv('.env')

# Database
# from models.models import Users, SavedResults, Db
# from passlib.hash import sha256_crypt

# Configure logging
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(threadName)s -  %(levelname)s - %(message)s')

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

# Initialize app
app = Flask(__name__)
# app.database_key = os.environ.get('DATABASE_KEY')

# Initialize DB
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL").replace("postgres://", "postgresql://")
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.secret_key = os.environ.get('SECRET_KEY') # Make sure this is set in Heroku dashboard for this new app!
# Db.init_app(app)


# Pages
@app.route('/')
def home():

    return render_template('pages/home.html')

@app.route('/under_construction')
def under_construction():

    return render_template('pages/under_construction.html')


@app.route('/upload_photo')
def upload_photo():

    return render_template('pages/upload_photo.html')


@app.route('/results')
def results():

    return render_template('pages/results.html')
