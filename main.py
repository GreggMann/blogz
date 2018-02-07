from flask import Flask, request, redirect, render_template, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogzpassword@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key ="abc"


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1200))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(20))
    blog = db.relationship('Blog', backref='owner')

def __init__(self, username, password):
    self.username = username
    self.password = password

def is_empty(usr_string):
    empty = True
    if usr_string:
        empty = False
    return empty

def all_posts():
    posts = Blog.query.all()
    return posts

def user_posts(user):
    userposts = Blog.query.filter_by(owner_id = user.user_id).all()
    return userposts

@app.before_request
def require_login():
    allowed_routes = ['blog', 'signup', 'login', 'index']

    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route("/", methods = ["POST", "GET"])
def index():
    users = User.query.all()
    if users:
        return render_template('index.html', users=users)
    else:
        return redirect('/login')

    return render_template("newpost.html")
 
@app.route("/blog", methods = ["POST", "GET"])
def blog():
    blog_posts = Blog.query.all()
    blog_id = request.args.get('id')
    
    if blog_id: 
        blog_entry = Blog.query.filter_by(id = blog_id).all()
        return render_template("blog.html", posts = blog_entry)

    userID = request.args.get('userID')
    if userID:
        user_total_entries = Blog.query.filter_by(owner_id = userID).all()
        user = User.query.filter_by(id = userID).first()
        return render_template("singleUser.html",id = userID, posts = user_total_entries, username = user.username)
    
    return render_template("blog.html", posts = blog_posts)
        
@app.route("/newpost", methods = ["POST", "GET"])
def newpost(): 
    if request.method == "POST":
        blog_title_error = ""
        blog_post_error = ""
        blg_title = ""
        blg_post = ""
        if is_empty(request.form["title"]) or is_empty(request.form["body"]):
            if is_empty(request.form["title"]):
                blog_title_error = "Please fill in the title."
            else:
                blg_title = request.form["title"]
            if is_empty(request.form["body"]):
                blog_post_error = "Please fill in the body."
            else:
                blg_post = request.form["body"]

        if blog_title_error or blog_post_error: 
            return render_template("newpost.html", blg_title = blg_title, blg_post = blg_post, 
        blog_title_error = blog_title_error, body_error = blog_post_error)

        else:
            title = request.form["title"]
            body = request.form["body"]
            owner = User.query.filter_by(username=session['username']).first()
            new_blog = Blog(title, body, owner)
            db.session.add(new_blog)
            db.session.commit()
        
            return redirect(url_for("blog", id = [new_blog.id]))
    
    return render_template("newpost.html")

@app.route("/login", methods = ["POST", "GET"])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        username_error= ""
        password_error= ""

        user = User.query.filter_by(username = username).first()

        if not user:
            username_error="User doesn't exist."
            return render_template("login.html", username_error = username_error, 
                password_error = password_error, username = username)

        elif user.password == password:
            session['username'] = username
            return redirect(url_for("newpost"))

        elif user.password != password:
            password_error = "Invalid password"

            return render_template("login.html", username_error = username_error, 
            password_error = password_error, username = username)

    return render_template("login.html")
    
@app.route("/signup", methods = ["POST", "GET"])
def signup():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password_create']
        verify_password = request.form['password_verify']

        username_error= ""
        password_error= ""
        verify_error= ""

        if len(username) < 3 or len(username) > 20 or username.isalnum() == False:
            username_error = "Username must be between three and twenty alphanumeric characters."

        if len(password) < 3 or len(password) > 20:
            password_error = "Password must be between three and twenty alphanumeric characters."
            password = ""

        if verify_password == "" or verify_password != password:
            verify_error = "Both passwords must be identical."
            verify_password = ""

        if not username_error and not password_error and not verify_error:
            existing_user = User.query.filter_by(username = username).first()
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost')

            else:
                username_error = "User name already exists."
        else:
            return render_template("signup.html", username_error = username_error, 
            password_error = password_error, verify_error = verify_error, username = username)
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    if session['username']:
        del session['username']
    return redirect('/blog')
    
if __name__ == "__main__":
    app.run()