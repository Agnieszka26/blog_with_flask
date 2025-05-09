from flask import Flask, render_template
import requests

app = Flask(__name__)

blog_url = 'https://api.npoint.io/c790b4d5cab58020d391'
resp = requests.get(blog_url)
posts = resp.json()

@app.route('/')
def home():
    return render_template("index.html", posts=posts)

@app.route("/post/<int:uuid>")
def get_post(uuid):
    return render_template('post.html', posts=posts, uuid=uuid)

if __name__ == "__main__":
    app.run(debug=True)
