import os
from flask import (
           Flask, flash, redirect, render_template, 
           request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)

@app.route("/")
@app.route("/home")
def home():
    get_recipes = list(mongo.db.recipes.find())
    return render_template("home.html", get_recipes=get_recipes)


@app.route("/recipes")
def recipes():
    recipes = list(mongo.db.recipes.find())
    return render_template("recipes.html", recipes=recipes)



@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        exist_user = mongo.db.users.find_one(
                              {"first_name": request.form.get("first_name").lower(),
                               "last_name": request.form.get("last_name").lower()})

        if exist_user:
            flash("The User Is Already Exists")
            return redirect(url_for("register"))

        register_user = {
            "first_name": request.form.get("first_name").lower(),
            "last_name": request.form.get("last_name").lower(),
            "e_mail": request.form.get("e_mail"),
            "password": generate_password_hash(request.form.get("password")) 
        } 
        mongo.db.users.insert_one(register_user)

        # Put the new user into session
        session["user"] = (request.form.get("first_name").lower(),
                           request.form.get("last_name").lower())

        flash("You have been successfully registered")
        return redirect(url_for("profile", e_mail=session["user"]))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        exist_user = mongo.db.users.find_one(
                              {"e_mail": request.form.get("e_mail")})

        if exist_user:
            #Check Password Matches
            if check_password_hash(
                    exist_user["password"], request.form.get("password")):
                    session["user"] = request.form.get("e_mail")
                    flash("Welcome, {}".format(request.form.get("e_mail")))
                    return redirect(url_for("profile", e_mail=session["user"]))

            else:
                #if the password not matches
                flash("email id and/or password is incorrect")
                return redirect(url_for("login"))

        else:
            #The user's email can not found
            flash("email id and/or password is incorrect")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<e_mail>", methods=["GET", "POST"])
def profile(e_mail):
    #grab the session user's username from the database.
    e_mail = mongo.db.users.find_one(
             {"e_mail": session["user"]})["e_mail"]
    if session["user"]:
        return render_template(
            "profile.html", e_mail=e_mail)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    #delete user from session
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))

    


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug= True)
