import smtplib
from wsgiref.validate import validator
from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date, datetime
from flask import Flask, render_template, request
from dotenv import load_dotenv
import os

load_dotenv()

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")
GMAIL_HOST_NAME = os.getenv("GMAIL_HOST_NAME")
PORT = int(os.getenv("PORT"))
TIMEOUT = int(os.getenv("TIMEOUT"))

app = Flask(__name__)
bootstrap = Bootstrap5(app)
ckeditor = CKEditor(app)


class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SECRET_KEY'] = "powerful secretkey"
app.config['WTF_CSRF_SECRET_KEY'] = "a csrf secret key"
app.config['CKEDITOR_PKG_TYPE'] = 'basic'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CONFIGURE TABLE
class BlogPost(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)


with app.app_context():
    db.create_all()


@app.route('/')
def home():
    with app.app_context():
        posts = db.session.execute(db.select(BlogPost).order_by(BlogPost.date)).scalars().all()
    return render_template("index.html", posts=posts)


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/contact')
def contact():
    return render_template("contact.html")


@app.route('/login')
def login():
    return render_template("login.html")


@app.route('/dashboard', methods=["post"])
def dashboard():
    username = "none"
    password = "none"
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
    return render_template('dashboard.html', name=username, password=password)


@app.route("/form-entry", methods=["post"])
def receive_data():
    message = request.form['message']
    email = request.form['email']
    with smtplib.SMTP(GMAIL_HOST_NAME, PORT, timeout=TIMEOUT) as connection:
        connection.starttls()
        connection.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
        connection.sendmail(from_addr=email, to_addrs=GMAIL_ADDRESS, msg=f'Subject: From your webpage \n\n {message}')
    return render_template("message.html", message=message)


@app.route("/post/<int:uuid>")
def get_post(uuid):
    with app.app_context():
        requested_post = db.session.execute(db.select(BlogPost).where(BlogPost.id == uuid)).scalar()
    return render_template('post.html', post=requested_post)


# TODO: add_new_post() to create a new blog post
class NewPostForm(FlaskForm):
    title = StringField("title", validators=[DataRequired()])
    subtitle = StringField('subtitle', validators=[DataRequired()])
    author = StringField("author", validators=[DataRequired()])
    img_url = StringField("img url", validators=[DataRequired()])
    body = CKEditorField('Body')
    submit = SubmitField('Create new post')


@app.route("/new-post", methods=["POST", "GET"])
def add_new_post():
    form = NewPostForm()
    if form.validate_on_submit():
        with app.app_context():
            current_date = datetime.now().strftime("%B %d, %Y")
            new_post = BlogPost(title=form.title.data,
                                author=form.author.data,
                                subtitle=form.subtitle.data,
                                img_url=form.img_url.data,
                                body=form.body.data,
                                date=current_date)
            db.session.add(new_post)
            db.session.commit()
        return redirect('/')
    return render_template("make-post.html", form=form)


# TODO: edit_post() to change an existing blog post
@app.route("/edit-post/<uuid>", methods=["POST", "GET"])
def edit_post(uuid):
    edited_post = db.session.execute(db.select(BlogPost).where(BlogPost.id == uuid)).scalar()
    form = NewPostForm(title=edited_post.title,
                                author=edited_post.author,
                                subtitle=edited_post.subtitle,
                                img_url=edited_post.img_url,
                                body=edited_post.body)
    if form.validate_on_submit():
        edited_post.title=form.title.data
        edited_post.author=form.author.data
        edited_post.subtitle=form.subtitle.data
        edited_post.img_url=form.img_url.data
        edited_post.body=form.body.data
        db.session.commit()
        return redirect('/')
    return render_template("make-post.html", form=form)

# TODO: delete_post() to remove a blog post from the database
@app.route('/delete/<uuid>')
def delete_post(uuid):
    post = db.get_or_404(BlogPost, uuid)
    db.session.delete(post)
    db.session.commit()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
