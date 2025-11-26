from flask import Blueprint, render_template

ui_bp = Blueprint("ui_bp", __name__)

@ui_bp.route("/")
def home():
    return render_template("billing_summary.html")

@ui_bp.route("/billing")
def billing_page():
    return render_template("billing_summary.html")

@ui_bp.route("/providers")
def providers_page():
    return render_template("providers.html")

@ui_bp.route("/trucks")
def trucks_page():
    return render_template("trucks.html")

@ui_bp.route("/ui/rates")
def rates_page():
    return render_template("rates.html")
