import smtplib
from functools import wraps
from typing import List
from wsgiref.validate import validator
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text, ForeignKey
from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date, datetime
from dotenv import load_dotenv
import os
from forms import NewPostForm, RegisterForm, LoginForm
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

load_dotenv()

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")
GMAIL_HOST_NAME = os.getenv("GMAIL_HOST_NAME")
PORT = int(os.getenv("PORT"))
TIMEOUT = int(os.getenv("TIMEOUT"))

app = Flask(__name__)
bootstrap = Bootstrap5(app)
ckeditor = CKEditor(app)
login_manager = LoginManager()
login_manager.init_app(app)

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
    __tablename__ = "blog_post"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # Create Foreign Key, "users.id" the users refers to the tablename of User.
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    # Create reference to the User object. The "posts" refers to the posts property in the User class.
    author = relationship("User", back_populates="posts")

    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # This will act like a List of BlogPost objects attached to each User.
    # The "author" refers to the author property in the BlogPost class.
    email: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(250), nullable=False)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    posts = relationship("BlogPost", back_populates="author")

with app.app_context():
    db.create_all()

def get_author(post):
    post_dict = post.__dict__.copy()
    post_dict.pop('_sa_instance_state', None)
    author = db.session.execute(db.select(User).where(User.id == post.author_id)).scalar()
    post_dict["author_name"] = author.name
    return post_dict

def get_posts_with_author():
    posts_arr = []
    with app.app_context():
        posts = db.session.execute(db.select(BlogPost).order_by(BlogPost.date)).scalars().all()
        for post in posts:
            print(post.author.name) #PROŚCIEJ Xd
            post_dict = get_author(post)
            posts_arr.append(post_dict)
    return posts_arr

def get_post_with_author(uuid):
    with app.app_context():
        requested_post = db.session.execute(db.select(BlogPost).where(BlogPost.id == uuid)).scalar()
        post_dict = get_author(requested_post)
    return post_dict

def admin_only(f):
    @wraps(f)
    def is_admin(*args, **kwargs):
        if not current_user.id == 1:
            return redirect(url_for('login'))
        return  f(*args, **kwargs)
    return is_admin

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

@app.route('/')
def home():
    posts = get_posts_with_author()
    return render_template("index.html", posts=posts, current_user=current_user)

@app.route('/about')
def about():
    return render_template("about.html", current_user=current_user)

@app.route('/contact')
def contact():
    return render_template("contact.html", current_user=current_user)

@app.route('/login', methods=["POST", "GET"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('You were successfully logged in')
            return redirect(url_for("dashboard"))
        else:
            flash('Invalid credentials')

    return render_template("login.html", form=form, current_user=current_user)

@app.route('/register', methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        password = generate_password_hash(password=form.password.data, method='pbkdf2:sha256', salt_length=8)
        name = form.name.data
        email = form.email.data

        user_exists = db.session.execute(db.select(User).where(User.email == email)).scalar()
        if user_exists:
            flash("User already exist, please login.")
            return redirect(url_for("login"))
        else:
            flash("You have registered, please login.")
            new_user = User(email= form.email.data, name=name, password=password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("login"))
    return render_template("register.html", form=form, current_user=current_user)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', current_user=current_user)

@app.route("/form-entry", methods=["POST", "GET"])
def receive_data():
    message = request.form['message']
    email = request.form['email']
    with smtplib.SMTP(GMAIL_HOST_NAME, PORT, timeout=TIMEOUT) as connection:
        connection.starttls()
        connection.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
        connection.sendmail(from_addr=email, to_addrs=GMAIL_ADDRESS, msg=f'Subject: From your webpage \n\n {message}')
    return render_template("message.html", message=message, current_user=current_user)

@app.route("/post/<int:uuid>")
def get_post(uuid):
    requested_post = get_post_with_author(uuid)
    return render_template('post.html', post=requested_post, current_user=current_user)

@app.route("/new-post", methods=["POST", "GET"])
@admin_only
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
    return render_template("make-post.html", form=form, current_user=current_user)

@app.route("/edit-post/<int:uuid>", methods=["POST", "GET"])
@admin_only
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
    return render_template("make-post.html", form=form, current_user=current_user)

@app.route('/delete/<int:uuid>')
@admin_only
def delete_post(uuid):
    post = db.get_or_404(BlogPost, uuid)
    db.session.delete(post)
    db.session.commit()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
