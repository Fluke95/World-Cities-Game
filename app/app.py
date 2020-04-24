from flask import Flask, render_template, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from socket import gethostname
import numpy as np
import random

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///world_cities_db.db'
db = SQLAlchemy(app)

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

def get_random_cities(coordinate, game_type):

    if game_type == 'europe':
        current_session = db.session.execute("""
        SELECT c.id, city_name, ctr.country, {0}
        FROM cities AS c
        INNER JOIN countries AS ctr ON c.iso2 = ctr.iso2
        WHERE iso2_continent = 'EU'
        AND population > 500000
        ORDER BY RANDOM() LIMIT 2;
        """.format(coordinate))
    elif game_type == 'world':
        current_session = db.session.execute("""
        SELECT c.id, city_name, ctr.country, {0}
        FROM cities AS c
        INNER JOIN countries AS ctr ON c.iso2 = ctr.iso2
        AND population > 1000000
        ORDER BY RANDOM() LIMIT 2;
        """.format(coordinate))
    else:
        current_session = db.session.execute("""
        SELECT c.id, city_name, ctr.country, {0}
        FROM cities AS c
        INNER JOIN countries AS ctr ON c.iso2 = ctr.iso2
        WHERE capital = 1
        ORDER BY RANDOM() LIMIT 2;
        """.format(coordinate))

    random_cities = current_session.fetchall()
    db.session.commit()
    db.session.close()
    return random_cities

def right_city_answer(direction, cities):
    if direction in ['North', 'East']:
        right_number = np.array([cities[0][-1], cities[1][-1]]).max()
    else:
        right_number = np.array([cities[0][-1], cities[1][-1]]).min()
    return [x for x in cities if x[-1] == right_number]

def return_city_by_id(city_id):
    current_session = db.session.execute("""
    SELECT 
        city_name AS City, 
        ROUND(lat, 2) AS Latitude, 
        ROUND(lng, 2) AS Longitude,
        countries.country AS Country,
        countries.iso2_continent AS Continent
    FROM cities
    INNER JOIN countries ON cities.iso2 = countries.iso2
    WHERE id = {0};""".format(city_id))
    city_row = current_session.fetchall()
    db.session.commit()
    db.session.close()
    return city_row

# ----------------------------------------------------------------------------------------------------------------------
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# ----------------------------------------------------------------------------------------------------------------------
@app.route('/europe/game', methods=['GET', 'POST'])
def game_europe():

    coordinate, direction = get_direction_and_coord()
    cities = get_random_cities(coordinate, game_type='europe')
    right_city_id = right_city_answer(direction, cities)[0][0]
    wrong_city_id = [city[0] for city in cities if city[0] != right_city_id][0]
    return render_template('game.html', cities=cities, direction=direction,
                           right_city_id=right_city_id,
                           wrong_city_id=wrong_city_id,
                           game_type=request.path,
                           content_type='application/json')

# ----------------------------------------------------------------------------------------------------------------------
@app.route('/world/game', methods=['GET', 'POST'])
def game_world():

    coordinate, direction = get_direction_and_coord()
    cities = get_random_cities(coordinate, game_type='world')
    right_city_id = right_city_answer(direction, cities)[0][0]
    wrong_city_id = [city[0] for city in cities if city[0] != right_city_id][0]
    return render_template('game.html', cities=cities, direction=direction,
                           right_city_id=right_city_id,
                           wrong_city_id=wrong_city_id,
                           game_type=request.path,
                           content_type='application/json')

# ----------------------------------------------------------------------------------------------------------------------
@app.route('/capitals/game', methods=['GET', 'POST'])
def game_capitals():

    coordinate, direction = get_direction_and_coord()
    cities = get_random_cities(coordinate, game_type='capitals')
    right_city_id = right_city_answer(direction, cities)[0][0]
    wrong_city_id = [city[0] for city in cities if city[0] != right_city_id][0]
    return render_template('game.html', cities=cities, direction=direction,
                           right_city_id=right_city_id,
                           wrong_city_id=wrong_city_id,
                           game_type=request.path,
                           content_type='application/json')

# ----------------------------------------------------------------------------------------------------------------------
@app.route('/answer', methods=['GET', 'POST'])
def give_answer():

    user_answer = request.form["cities_form"]
    right_answer = request.form["right_answer"]
    wrong_answer = request.form["wrong_answer"]
    drawn_direction = request.form["drawn_direction"]
    previous_path = request.form["game_type"]
    right_city_return = return_city_by_id(right_answer)
    wrong_city_return = return_city_by_id(wrong_answer)
    return render_template('answer.html', user_answer=user_answer, right_city_return=right_city_return,
                           wrong_city_return=wrong_city_return, drawn_direction=drawn_direction,
                           previous_path=previous_path)

# ----------------------------------------------------------------------------------------------------------------------
@app.route('/dataset', methods=['GET'])
def dataset():
    return render_template('dataset.html')

# ----------------------------------------------------------------------------------------------------------------------
@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

# ----------------------------------------------------------------------------------------------------------------------
@app.route('/sitemap.xml', methods=['GET'])
def sitemap():
    return send_from_directory(app.static_folder, request.path[1:])

# ----------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    db.create_all()
    if 'liveconsole' not in gethostname():
        app.run()
        # app.run(debug=True)
