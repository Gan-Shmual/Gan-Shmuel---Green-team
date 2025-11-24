from flask import Blueprint, request, jsonify
from flaskr.db import db
from flaskr.models.biling import Provider

bp = Blueprint('main', __name__)

#General
@bp.route('/health')
def health():
    return "ok"
