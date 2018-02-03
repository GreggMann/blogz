from flask import Flask, request, redirect, render_template, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:buildapassword@localhost:3306/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1200))

    def __init__(self, title, body):
        self.title = title
        self.body = body

def is_empty(usr_string):
    empty = True
    if usr_string != "":
        empty = False
    return empty

@app.route("/", methods = ["POST", "GET"])
def index():
    return render_template("newpost.html")
 
@app.route("/blog", methods = ["POST", "GET"])
def blog():
    blog_posts = Blog.query.all()

    blog_id = request.args.get('id')
    if blog_id is None: 
        return render_template("entry.html", title = "Build a Blog", blogposts = blog_posts)
    else:
        blog_entry = Blog.query.get(blog_id)
        return render_template("blog.html", title = blog_entry.title, blog_content = blog_entry.body)

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
            new_blog = Blog(title, body)
            db.session.add(new_blog)
            db.session.commit()
        
            return redirect(url_for("blog", id = [new_blog.id]))
    
    return render_template("newpost.html")
    
if __name__ == "__main__":
    app.run()