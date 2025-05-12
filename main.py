import smtplib
from dotenv import load_dotenv
import os
load_dotenv()

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")
GMAIL_HOST_NAME = os.getenv("GMAIL_HOST_NAME")
PORT = int(os.getenv("PORT"))
TIMEOUT= int(os.getenv("TIMEOUT"))

from flask import Flask, render_template, request
import requests

app = Flask(__name__)

blog_url = 'https://api.npoint.io/3eba1fb773d75db0fe57'
resp = requests.get(blog_url)
posts = resp.json()

@app.route('/')
def home():
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
    username= "none"
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
    requested_post = None
    for blog_post in posts:
        if blog_post["id"] == uuid:
            requested_post = blog_post
    return render_template('post.html', post=requested_post)

if __name__ == "__main__":
    app.run(debug=True)
