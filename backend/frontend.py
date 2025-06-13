from flask import Blueprint, redirect, url_for

frontend_bp = Blueprint("frontend", __name__, static_folder="static")

@frontend_bp.route("/")
def index():
    return redirect(url_for("frontend.static", filename="index.html"))

@frontend_bp.route("/home")
def home():
    return redirect(url_for("frontend.static", filename="home.html"))

