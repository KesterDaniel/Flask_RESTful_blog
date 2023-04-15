from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager, login_remembered, login_user, logout_user, current_user
from wtforms import StringField, SubmitField, EmailField, PasswordField
from wtforms.validators import DataRequired, URL, Email
from flask_ckeditor import CKEditor, CKEditorField
import datetime as dt


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
bootstrap = Bootstrap5(app)
login_manager = LoginManager()
login_manager.init_app(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.app_context().push()

##CONFIGURE BLOG TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


# CONFIGURE USER TABLE
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))

##WTForm
class CreateRegisterForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    name = StringField("Name", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])

class CreateLoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])


class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


@app.route('/')
def get_all_posts():
    posts = db.session.query(BlogPost).all()
    return render_template("index.html", all_posts=posts)

@app.route("/login", methods=["GET", "POST"])
def login():
    login_form = CreateLoginForm()
    if login_form.validate_on_submit():
        pass
    return render_template("login.html", form=login_form)


@app.route("/post/<int:index>")
def show_post(index):
    requested_post = None
    posts = db.session.query(BlogPost).all()
    for blog_post in posts:
        if blog_post.id == index:
            requested_post = blog_post
    return render_template("post.html", post=requested_post)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/newpost", methods=["GET", "POST"])
def new_post():
    new_post_form = CreatePostForm()
    if new_post_form.validate_on_submit():
        new_blog_post = BlogPost(
            title = new_post_form.title.data,
            subtitle = new_post_form.subtitle.data,
            author = new_post_form.author.data,
            date = dt.datetime.now().date().strftime("%B %d, %Y"),
            img_url = new_post_form.img_url.data,
            body = new_post_form.body.data
        )
        db.session.add(new_blog_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=new_post_form, edit=False)


@app.route("/editpost/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    post = BlogPost.query.filter_by(id=post_id).first()
    edit_post_form = CreatePostForm(
        title = post.title,
        subtitle = post.subtitle,
        img_url = post.img_url,
        author = post.author,
        body = post.body
    )
    if edit_post_form.validate_on_submit():
        post.title = edit_post_form.title.data
        post.subtitle = edit_post_form.subtitle.data
        post.img_url = edit_post_form.img_url.data
        post.author = edit_post_form.author.data
        post.body = edit_post_form.body.data
        db.session.commit()

        return redirect(url_for("show_post", index=post_id))

    return render_template("make-post.html", edit=True, form=edit_post_form)

@app.route("/delete/<int:post_id>")
def delete(post_id):
    post = BlogPost.query.filter_by(id=post_id).first()
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for("get_all_posts"))


if __name__ == "__main__":
    db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)