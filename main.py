from flask import Flask, render_template
import random
import requests
from datetime import datetime
app = Flask(__name__)


@app.route('/')
def home():
    random_number = random.randint(1,10)
    current_year = datetime.now().year

    return render_template("index.html", num=random_number, current_year=current_year )

@app.route('/guess/<name>')
def guess(name):
    url_gender = f'https://api.genderize.io?name={name}'
    url_age = f'https://api.agify.io?name={name}'
    resp_gender = requests.get(url_gender).json()
    resp_age = requests.get(url_age).json()
    age = resp_age['age']
    gender = resp_gender['gender']
    return render_template("guess.html", name=name, age=age, gender=gender)

@app.route("/blog/<num>")
def get_blog(num):
    print(num)
    blog_url = 'https://api.npoint.io/c790b4d5cab58020d391'
    resp = requests.get(blog_url)
    posts = resp.json()
    return render_template('blog.html', posts=posts)

if __name__ == "__main__":
    app.run(debug=True)


