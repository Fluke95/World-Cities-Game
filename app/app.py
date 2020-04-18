from flask import Flask, render_template, request, redirect
# from flask_sqlalchemy import SQLAlchemy
from socket import gethostname
import numpy as np
import random
import pymysql

app = Flask(__name__)
# mysql = MySQL(app)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
# db = SQLAlchemy(app)

def get_direction_and_coord():
    """Draw random coordinate and direction"""
    direction_dict = {
        'lat': ['North', 'South'],
        'lng': ['East', 'West']
    }
    coordinate = random.choice(['lat', 'lng'])
    directions = direction_dict.get(coordinate)
    direction = random.choice(directions)
    return coordinate, direction

def right_city_answer(direction, coordinate, cities):
    if direction in ['North', 'East']:
        right_number = np.array([cities[0].get(coordinate), cities[1].get(coordinate)]).max()
    else:
        right_number = np.array([cities[0].get(coordinate), cities[1].get(coordinate)]).min()

    return [x for x in cities if x.get(coordinate) == right_number]

# database -------------------------------------------------------------------------------------------------------------
class Database:
    def __init__(self):
        host = "sql7.freemysqlhosting.net"
        user = "sql7333463"
        password = "AH3ZYs9WM7"
        db = "sql7333463"
        self.con = pymysql.connect(host=host, user=user,
                                   password=password, db=db, port=3306, cursorclass=pymysql.cursors.DictCursor)
        self.cur = self.con.cursor()

    def list_cities(self):
        self.cur.execute("SELECT * FROM cities LIMIT 10")
        result = self.cur.fetchall()
        return result

    def get_random_cities(self, coordinate):
        self.cur.execute("""
        SELECT c.id, city_name, ctr.country, {0}
        FROM cities AS c
        INNER JOIN countries AS ctr ON c.iso2 = ctr.iso2
        WHERE iso2_continent = 'EU' 
        AND population > 500000
        ORDER BY RAND() LIMIT 2;
        """.format(coordinate))
        random_citiies = self.cur.fetchall()
        return random_citiies

    def return_city_by_id(self, city_id):
        self.cur.execute("""
        SELECT city_name AS City, ROUND(lat, 2) AS Latitude, ROUND(lng, 2) AS Longitude, countries.country AS Country, countries.iso2_continent AS Continent
        FROM cities
        INNER JOIN countries ON cities.iso2 = countries.iso2
        WHERE id = {0};""".format(city_id))
        city_row = self.cur.fetchall()
        return city_row

# ----------------------------------------------------------------------------------------------------------------------
@app.route('/')
def index():
    return render_template('index.html')

# ----------------------------------------------------------------------------------------------------------------------
@app.route('/game', methods=['GET', 'POST'])
def game():

    coordinate, direction = get_direction_and_coord()

    def db_random_cities():
        db = Database()
        rand_cities = db.get_random_cities(coordinate)
        return rand_cities

    cities = db_random_cities()
    right_city_id = right_city_answer(direction, coordinate, cities)[0].get('id')
    wrong_city_id = [city.get('id') for city in cities if city.get('id') != right_city_id][0]
    # task_id = random.randint(1, 1000000)
    return render_template('game.html', cities=cities, direction=direction,
                           right_city_id=right_city_id,
                           wrong_city_id=wrong_city_id,
                           # task_id=task_id,
                           content_type='application/json')

# ----------------------------------------------------------------------------------------------------------------------
@app.route('/answer/', methods=['GET', 'POST'])
def give_answer():
    user_answer = request.form["cities_form"]
    right_answer = request.form["right_answer"]
    wrong_answer = request.form["wrong_answer"]
    drawn_direction = request.form["drawn_direction"]
    db = Database()
    right_city_return = db.return_city_by_id(right_answer)
    wrong_city_return = db.return_city_by_id(wrong_answer)
    return render_template('answer.html', user_answer=user_answer, right_city_return=right_city_return,
                           wrong_city_return=wrong_city_return, drawn_direction=drawn_direction)

# ----------------------------------------------------------------------------------------------------------------------
# @app.route('/posts', methods=['GET', 'POST'])
# def posts():
#
    # if request.method == 'POST':
    #     post_title = request.form['title']
    #     post_content = request.form['content']
    #     post_author = request.form['author']
    #     new_post = BlogPost(title=post_title, content=post_content, author=post_author)
    #     db.session.add(new_post)
    #     db.session.commit()
    #     return redirect('/posts')
    # else:
    #     all_posts = BlogPost.query.order_by(BlogPost.date_posted).all()
    #     return render_template('posts.html', posts=all_posts)
#
# @app.route('/posts/delete/<int:id>')
# def delete(id):
#     post = BlogPost.query.get_or_404(id)
#     db.session.delete(post)
#     db.session.commit()
#     return redirect('/posts')
#
# @app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
# def edit(id):
#     post = BlogPost.query.get_or_404(id)
#
#     if request.method == 'POST':
#         post.title = request.form['title']
#         post.author = request.form['author']
#         post.content = request.form['content']
#         db.session.commit()
#         return redirect('/posts')
#     else:
#         return render_template('edit.html', post=post)

# ----------------------------------------------------------------------------------------------------------------------
@app.route('/dataset')
def dataset():
    return render_template('dataset.html')

# ----------------------------------------------------------------------------------------------------------------------
@app.route('/about')
def about():
    return render_template('about.html')

# ----------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    # app.run(debug=True)
    # db.create_all()
    if 'liveconsole' not in gethostname():
        app.run(debug=True)
