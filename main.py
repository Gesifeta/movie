from flask import Flask, render_template, request, redirect, url_for,json,jsonify
import requests
import sqlite3
from  api import MDB_KEY, MDB_TOKEN

url = "https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&language=en-US&page=1&sort_by=popularity.desc"
headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {MDB_TOKEN}",
}

movies = requests.get(url, headers=headers).json()['results']
app = Flask(__name__)
# with open("movies.json",'r',encoding='utf-8') as json_file:
#     movies = json.load(json_file)['results']


@app.route('/init')
def init():
    try:
        conn = sqlite3.connect('movies.db')
        conn.row_factory=sqlite3.Row
    except sqlite3.OperationalError as e:
        return f'Unable to connect to movies.db: {e}'
    else:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS movies(id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                       title TEXT,summary TEXT, year VARCHAR(12),img_url TEXT,average_rating REAL) ''')
        conn.commit()
        return conn

@app.route('/')
def index():
    connection = init()
    cursor = connection.cursor()
    my_movies = cursor.execute('SELECT id, title, summary, year, img_url FROM movies').fetchall()

    # Use a breakpoint in the code line below to debug your script.
    return render_template("index.html",my_movies=my_movies,show_details=False)


@app.route('/movie/add_new',methods=['POST','GET'])
def add_new_movie():
    if request.method == "POST":
        show_movie_lists = True
        new_movies = [movie for movie in movies if movie.get('title')==request.form['title']][0]
        connection = init()
        cursor = connection.cursor()
        cursor.execute(''' INSERT INTO movies(title,summary,year,average_rating,img_url) VALUES (?,?,?,?,?) ''',(
                                         new_movies['title'],new_movies['overview'],new_movies['release_date'],new_movies['vote_average'],
                                    f'https://www.themoviedb.org/t/p/w600_and_h900_bestv2/{new_movies['poster_path']}'))
        my_movies = connection.execute('SELECT id, title, summary, year, img_url FROM movies').fetchall()
        connection.commit()
    else:
        show_movie_lists = False
        cursor = init().cursor()
        my_movies = cursor.execute('SELECT id, title, summary, year,img_url FROM movies').fetchall()

    return render_template("add_movie_form.html",my_movies=my_movies,movies=movies,show_movie_lists=show_movie_lists)

@app.route('/movie/details/<string:title>')
def show_movie_details(title):
    connection = init()
    cursor = connection.cursor()
    my_movies = cursor.execute(''' SELECT id, title, summary, year, img_url FROM movies WHERE title = ? ''',(title,)).fetchall()

    return render_template("index.html", my_movies=my_movies,show_details=True )


@app.route('/movies/delete')
def delete_movie():
    connection = init()
    cursor = connection.cursor()
    cursor.execute('DELETE FROM movies')
    connection.commit()
    return redirect(url_for('index'))

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run(debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
