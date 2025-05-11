from flask import Flask, render_template
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

@app.route("/post/<int:uuid>")
def get_post(uuid):
    requested_post = None
    for blog_post in posts:
        if blog_post["id"] == uuid:
            requested_post = blog_post
    return render_template('post.html', post=requested_post)

if __name__ == "__main__":
    app.run(debug=True)
