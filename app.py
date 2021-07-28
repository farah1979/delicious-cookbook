import os
from flask import (
                   Flask, flash, redirect, render_template,
                   request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)

ADMIN_USER_NAME = 'adminfa'


#                                               Home-page-function
@app.route("/")
@app.route("/home")
def home():

    # Function render lastest four recipes from MongoDB
    # to home page

    recently_added_recipes = list(
                mongo.db.recipes.find().sort("_id", -1).limit(4))
    return render_template(
              "home.html", recently_added_recipes=recently_added_recipes)


#                                              Recipe-page-function
@app.route('/recipes')
def recipes():
    # Function render all recipes
    recipes = list(mongo.db.recipes.find().sort("_id", -1))
    return render_template('recipes.html', recipes=recipes)


#                                                   Search-function
@app.route("/search", methods=["GET", "POST"])
def search():
    # Function used for search method
    query = request.form.get("query")
    recipes = list(mongo.db.recipes.find({"$text": {"$search": query}}))
    return render_template("recipes.html", recipes=recipes)


#                                              Recipe-detial-page-function
@app.route("/recipe/<recipe_id>/view")
def recipe_detial(recipe_id):
    # Function render detial about a recipe

    try:
        recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
        if not recipe:
            return redirect(url_for("recipes"))
        return render_template("recipe_detial.html", recipe=recipe)
    except:
        return redirect(url_for("recipes"))


#                                              Addrecipe-page-function
@app.route("/recipe/add", methods=["GET", "POST"])
def add_recipe():

    # Function used to create new recipe by a user session
    # if the user has an acount
    # cheack if the admin logged in or not
    if not session["user"]:
        return redirect(url_for("home"))
    if request.method == "POST":
        is_veg = True if request.form.get("is_veg") else False
        recipe = {
                  "category_name": request.form.get("category_name"),
                  "recipe_name": request.form.get("recipe_name"),
                  "recipe_description": request.form.get("recipe_description"),
                  "ingredients": (request.form.getlist(
                            "ingredients")[0].replace(
                                 '\n', '')[:-1].split('\r')),
                  "instructions": (request.form.getlist(
                           "instructions")[0].replace(
                                 '\n', '')[:-1].split('\r')),
                  "prep_time": request.form.get("prep_time"),
                  "cooking_time": request.form.get("cooking_time"),
                  "serves": request.form.get("serves"),
                  "created_at": datetime.now(),
                  "updated_at": datetime.now(),
                  "image": request.form.get("image"),
                  "is_veg": is_veg,
                  "author": session['user']
        }
        mongo.db.recipes.insert_one(recipe)
        flash("Your recipe has been successfully added")
        return redirect(url_for("recipes"))

    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("add_recipe.html", categories=categories)


#                                                       Editrecipe-page-function
@app.route("/recipe/<recipe_id>/edit", methods=["GET", "POST"])
def edit_recipe(recipe_id):

    # cheack if the user has acount
    # function let the logged user to edit his/her recipes only
    if not session["user"]:
        return redirect(url_for("home"))
    if request.method == "POST":
        is_veg = True if request.form.get("is_veg") else False
        update = {
                  "category_name": request.form.get("category_name"),
                  "recipe_name": request.form.get("recipe_name"),
                  "recipe_description": request.form.get("recipe_description"),
                  "ingredients": (request.form.getlist(
                           "ingredients")[0].replace(
                               '\n', '')[:-1].split('\r')),
                  "instructions": (request.form.getlist(
                           "instructions")[0].replace(
                                '\n', '')[:-1].split('\r')),
                  "prep_time": request.form.get("prep_time"),
                  "cooking_time": request.form.get("cooking_time"),
                  "serves": request.form.get("serves"),
                  "created_at": datetime.now(),
                  "updated_at": datetime.now(),
                  "image": request.form.get("image"),
                  "is_veg": is_veg,
                  "author": session['user']
        }
        try:
            mongo.db.recipes.update({"_id": ObjectId(recipe_id)}, update)
            flash("Your recipe has been successfully updated")
        except:
            return redirect(url_for('recipes'))

    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    recipe['ingredients'] = '\n'.join(recipe['ingredients'])
    recipe['instructions'] = '\n'.join(recipe['instructions'])
    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template(
          "edit_recipe.html", recipe=recipe, categories=categories)


#                                               Get Ctaegories-page-function
@app.route("/categories")
def get_categories():

    # Check here is user is admin, else redirect to home page

    if not (session["user"] and session["user"] == ADMIN_USER_NAME):
        return redirect(url_for("home"))

    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("get_categories.html", categories=categories)


#                                                 Add category-page-function
@app.route("/category/add", methods=["GET", "POST"])
def add_category():
    # Check here is user is admin, else redirect to home page

    if not (session["user"] and session["user"] == ADMIN_USER_NAME):
        return redirect(url_for("home"))

    if request.method == "POST":
        category = {
            "category_name": request.form.get("category_name")
        }
        mongo.db.categories.insert_one(category)
        flash("Category has been added successfully")
        return redirect(url_for("get_categories"))

    return render_template("add_category.html")


#                                                  Edit category-page-function
@app.route("/category/<category_id>/edit", methods=["GET", "POST"])
def edit_category(category_id):
    # Check here is user is admin, else redirect to home page
    if not (session["user"] and session["user"] == ADMIN_USER_NAME):
        return redirect(url_for("home"))

    if request.method == "POST":
        submit = {
            "category_name": request.form.get("category_name")
        }
        try:
            mongo.db.categories.update({"_id": ObjectId(category_id)}, submit)
            flash("Category has been updated Successfully")
            return redirect(url_for("get_categories"))
        except:
            return redirect(url_for('get_categories'))

    category = mongo.db.categories.find_one({"_id": ObjectId(category_id)})
    return render_template("edit_category.html", category=category)


#                                               Delete category-page-function
@app.route("/category/<category_id>/delete")
def delete_category(category_id):
    # Check here is user is admin, else redirect to home page
    if not (session["user"] and session["user"] == ADMIN_USER_NAME):
        return redirect(url_for("home"))
    try:
        mongo.db.categories.remove({"_id": ObjectId(category_id)})
        flash("Category successfully deleted")
        return redirect(url_for('get_categories'))
    except:
        return redirect(url_for('get_categories'))


#                                                Delete recipe-page-function
@app.route("/recipe/<recipe_id>/delete")
def delete_recipe(recipe_id):

    # function used to delete a recipe
    try:
        mongo.db.recipes.remove({"_id": ObjectId(recipe_id)})
        flash("Your recipe has been successfully deleted")
        return redirect(url_for('recipes'))
    except:
        return redirect(url_for('recipes'))


#                                               Register-page-function
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        exist_user = mongo.db.users.find_one(
                              {"username": request.form.get(
                                      "username").lower()})

        if exist_user:
            flash("The User Is Already Exists")
            return redirect(url_for("register"))
        register_user = {
            "first_name": request.form.get("first_name").lower(),
            "last_name": request.form.get("last_name").lower(),
            "username": request.form.get("username").lower(),
            "e_mail": request.form.get("e_mail"),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register_user)
        # Put the new user into session
        session["user"] = request.form.get("username").lower()
        flash("You have been successfully registered")
        return redirect(url_for('profile'))

    return render_template("register.html")


#                                                    Login-page-function
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        exist_user = mongo.db.users.find_one(
                              {"username": request.form.get(
                                     "username").lower()})

        if exist_user:
            # Check Password Matches
            if check_password_hash(
                    exist_user["password"], request.form.get("password")):
                    session["user"] = request.form.get("username").lower()
                    flash("Welcome, {}".format(request.form.get("username")))
                    return redirect(url_for("profile"))
            else:
                # if the password not matches
                flash("Firstname and/or password is incorrect")
                return redirect(url_for("login"))
        else:
            # The user's email can not found
            flash("Firstname and/or password is incorrect")
            return redirect(url_for("login"))

    return render_template("login.html")


#                                                  Profile-page-function
@app.route("/profile", methods=["GET", "POST"])
def profile():

    # cheack if the user session or not redirect to home page
    if not session["user"]:
        return redirect(url_for("home"))
    username = session['user']
    first_name = mongo.db.users.find_one(
        {'username': username})['first_name']
    my_recipes = list(
            mongo.db.recipes.find({"author": username}).sort([("_id", -1)]))
    if username:
        return render_template(
            'profile.html', first_name=first_name, my_recipes=my_recipes)

    return redirect(url_for('login'))


#                                                     Logout-page-function
@app.route("/logout")
def logout():

    # delete user from session
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=False)
