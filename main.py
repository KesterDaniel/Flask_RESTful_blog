from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
import datetime as dt



app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
bootstrap = Bootstrap5(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.app_context().push()

##CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


##WTForm
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
    edit_post_form = CreatePostForm()
    if edit_post_form.validate_on_submit():
        pass
    return render_template("make-post.html", edit=True, form=edit_post_form)

if __name__ == "__main__":
    db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)