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
    get_recipes = list(mongo.db.recipes.find().sort("_id", -1).limit(4))
    return render_template("home.html", get_recipes=get_recipes)
 

@app.route('/recipes')
def recipes():
    """
    Function render all recipes in the page
    """

    recipes = list(mongo.db.recipes.find().sort("_id", -1))
    return render_template('recipes.html', recipes=recipes)


@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.form.get("query")
    recipes = list(mongo.db.recipes.find({"$text": {"$search": query}}))
    return render_template("recipes.html", recipes=recipes)


@app.route("/recipe_detial/<recipe_id>")
def recipe_detial(recipe_id):
    
    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})

    return render_template("recipe_detial.html",recipe=recipe)


@app.route("/add_recipe", methods=["GET","POST"])
def add_recipe():
    if request.method == "POST":
        is_veg = True if request.form.get("is_veg") else False
        recipe = {
                  "category_name": request.form.get("category_name"),
                  "recipe_name": request.form.get("recipe_name"),
                  "recipe_description": request.form.get("recipe_description"),
                  "ingredients": request.form.getlist("ingredients"),
                  "instructions": request.form.getlist("instructions"),
                  "Prep_time": request.form.get("Prep_time"),
                  "cooking_time": request.form.get("cooking_time"),
                  "serves": request.form.get("serves"),
                  "created_at": request.form.get("created_at"),
                  "updated_at": request.form.get("updated_at") ,
                  "image": request.form.get("image"),
                  "is_veg": is_veg,
                  "author": session['user']
        }
        mongo.db.recipes.insert_one(recipe)
        flash("Your recipe has been successfully added")
        return redirect(url_for("recipes"))
    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("add_recipe.html", categories=categories)


@app.route("/edit_recipe/<recipe_id>", methods=["GET","POST"])
def edit_recipe(recipe_id):
    if request.method == "POST":
        is_veg = True if request.form.get("is_veg") else False
        update = {
                  "category_name": request.form.get("category_name"),
                  "recipe_name": request.form.get("recipe_name"),
                  "recipe_description": request.form.get("recipe_description"),
                  "ingredients": request.form.getlist("ingredients"),
                  "instructions": request.form.getlist("instructions"),
                  "Prep_time": request.form.get("Prep_time"),
                  "cooking_time": request.form.get("cooking_time"),
                  "serves": request.form.get("serves"),
                  "created_at": request.form.get("created_at"),
                  "updated_at": request.form.get("updated_at") ,
                  "image": request.form.get("image"),
                  "is_veg": is_veg,
                  "author": session['user']
        }
        mongo.db.recipes.update({"_id": ObjectId(recipe_id)}, update)
        flash("Your recipe has been successfully updated")

    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("edit_recipe.html",recipe=recipe, categories=categories)


@app.route("/get_categories")
def get_categories():
    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("get_categories.html", categories=categories)


@app.route("/add_category", methods=["GET", "POST"])
def add_category():
    if request.method == "POST":
        category = {
            "category_name": request.form.get("category_name")
        }
        mongo.db.categories.insert_one(category)
        flash("Category has been added successfully")
        return redirect(url_for("get_categories"))

    return render_template("add_category.html")


@app.route("/edit_category/<category_id>", methods=["GET","POST"])
def edit_category(category_id):
    if request.method == "POST":
        submit= {
            "category_name": request.form.get("category_name")
        }
        mongo.db.categories.update({"_id": ObjectId(category_id)}, submit)
        flash("Category has been updated Successfully")
        return redirect(url_for("get_categories"))

    category= mongo.db.categories.find_one({"_id": ObjectId(category_id)})
    return render_template("edit_category.html", category=category)


@app.route("/delete_category/<category_id>")
def delete_category(category_id):
    mongo.db.categories.remove({"_id": ObjectId(category_id)})
    flash("Category successfully deleted")
    return redirect(url_for('get_categories'))


@app.route("/delete_recipe/<recipe_id>")
def delete_recipe(recipe_id):
    mongo.db.recipes.remove({"_id": ObjectId(recipe_id)})
    flash("Your recipe has been successfully deleted")
    return redirect(url_for('recipes'))


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
                           request.form.get("last_name").lower(),
                           request.form.get("e_mail"))

        flash("You have been successfully registered")
        
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
                    return redirect(url_for(
                            "profile", e_mail=session["user"]))

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
    e_mail = mongo.db.users.find_one(
        {"e_mail": session["user"]})["e_mail"]

    my_recipes = list(
            mongo.db.recipes.find({"author": e_mail}))
    if session['user']:
        return render_template(
            'profile.html', e_mail=e_mail, my_recipes=my_recipes)
    return redirect(url_for('login'))


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
