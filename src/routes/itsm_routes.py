"""
ITSM related routes
"""
from flask import Blueprint, render_template, jsonify, request
import os
from datetime import datetime

itsm_bp = Blueprint('itsm', __name__, url_prefix='/itsm')

@itsm_bp.route('/')
def itsm():
    return render_template('itsm.html')


@itsm_bp.route('/scraper')
def itsm_scraper_page():
    return render_template('itsm_scraper.html')