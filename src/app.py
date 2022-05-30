from flask import Flask,render_template,request,session,logging,url_for,redirect,flash
from flask_login import LoginManager, login_user, logout_user, login_required
from flask_wtf import CSRFProtect
from functools import wraps
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

from config import config

# Models:
from models.ModelUser import ModelUser

# Entities:
from models.entities.User import User

app = Flask(__name__)
#Mysql Connection
db = MySQL(app)
#Variable to login manager
login_manager_app = LoginManager(app)
#Variable for CSRF token
csrf = CSRFProtect()

@login_manager_app.user_loader
def load_user(id):
    return ModelUser.get_by_id(db, id)       

#Register api
@app.route("/register", methods=["GET","POST"])
def register():
    # Check if POST requests exist (user submitted form)
    if request.method == "POST":
         # Create variables for easy access
        user = User(0,request.form["username"],request.form["password"],fullname = request.form["fullname"],email = request.form["email"],usertype = request.form["usertype"])
        username = request.form["username"]
        fullname = request.form["fullname"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        ##secure_password = sha256_crypt.encrypt(str(password))
        email = request.form["email"]
        usertype = request.form["usertype"]
        # Check if account exists using MySQL
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            flash("Account already exists!", "bg-red-100 text-center")
        # If is invalid email address
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash("Invalid email address!" , "bg-red-100 text-center")
        # If username contain especial caracters
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash("Username must contain only characters and numbers!", "bg-red-100")
        # If password is not the same
        elif password != confirm_password:
            flash("Password does not match", "bg-red-100")
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cur = db.connection.cursor()
            cur.execute('INSERT INTO users(username,fullname,password,email,usertype) VALUES (%s,%s,%s,%s,%s)',(username, fullname, password, email, usertype))
            db.connection.commit()
            flash("You have successfully registered!", "bg-green-100")
            return render_template("login.html")
    return render_template("register.html")

#Login api
@app.route("/")
@app.route("/login", methods=["GET", "POST"])
def login():
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == "POST":
        user = User(0,request.form['username'], request.form['password'])
        logged_user = ModelUser.login(db, user)
        # Account doesnt exist or username/password incorrect
        if logged_user != None:
            if logged_user.password:
                login_user(logged_user)
                return redirect(url_for("home"))
            else:
                flash("Invalid password!", "bgr-red-100")
        else:
            flash("User not found!", "bgr-red-100")
    # Show the login form with message (if any)
    return render_template("login.html")


#logout api
@app.route("/logout")
def logout():
    # Remove session data, this will log the user out
   logout_user()
   # Redirect to login page
   return redirect(url_for("login"))




#home api
@app.route("/login/home")
@login_required
def home():
    return render_template("home.html", user=User)
    
#new activity api
@app.route("/login/newactivity", methods=["GET", "POST"])
@login_required
def newactivity():
    if request.method == "POST":
        # Create variables for easy access
        useract=session["username"]
        start_date = request.form["start_date"]
        finish_date = request.form["finish_date"]
        activity = request.form["activity"]
        describe_activity = request.form["describe_activity"]
        #Insert new activity into activites table
        cur = db.connection.cursor()
        cur.execute('INSERT INTO activities(useract,start_date,finish_date,activity,describe_activity) VALUES (%s,%s,%s,%s,%s)',(useract,start_date,finish_date,activity,describe_activity))
        db.connection.commit()
        return flash("You have successfully save the activity!", "bg-green-100")   
    return render_template("newactivity.html") 
  
#consult activity apli
@app.route("/login/consultactivity", methods=["GET", "POST"])
@login_required
def consultact():
    if request.method == "POST":
        cur= db.connection.cursor()
        cur.execute('SELECT * FROM activities WHERE username = %s, status = NULL ')
        data = cur.fetch()
        activitys = data
        return activitys
    return render_template("consultactivity.html",)

#update activity api
@app.route('/edit/<id>', methods=['POST'])
def update_act(id):
    if request.method == 'POST':
        status = request.form['status']
        cur = db.connection.cursor()
        cur.execute(""" UPDATE activities SET status = %s """, (status))
        flash('Activity Updated Successfully')
        db.connection.commit()
        return redirect(url_for('consultactivity.html'))

#delete activity api
@app.route('/delete/<string:id>', methods = ['POST','GET'])
def delete_act(id):
    cur = db.connection.cursor()
    cur.execute('DELETE FROM activities WHERE id = {0}'.format(id))
    db.connection.commit()
    flash('Activity Removed Successfully')
    return redirect(url_for('consultactivity.html')) 

@app.route("/login/capturefeedback", methods=["GET", "POST"])
@login_required
def consultfeed():
    if request.method == "POST":
        cur= db.connection.cursor()
        cur.execute('SELECT * FROM activities WHERE username = %s, status = OK LIMIT 1 ')
        data = cur.fetch()
        activitys = data
        return activitys
    return render_template("capturefeedback.html",) 

def status_401(error):
    return redirect(url_for('login'))

def status_404(error):
    return "<h1> Pagina no encontrada</h1>", 404

if __name__=='__main__':
    app.config.from_object(config['develoment'])
    csrf.init_app(app)
    app.register_error_handler(401, status_401)
    app.register_error_handler(404, status_404)
    app.run()
