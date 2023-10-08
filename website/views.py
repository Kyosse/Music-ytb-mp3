from flask import Blueprint, render_template

views = Blueprint('views', __name__)




@views.route('/')
def home():
    popular = update_popular()

    return render_template("home.html", user=current_user,popular=popular)



@views.route("/scan")
def scan():
    
    return render_template("scan.html", user=current_user)