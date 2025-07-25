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
        c.execute(''' CREATE TABLE IF NOT EXISTS rating
        (
            id
            INTEGER
            PRIMARY
            KEY,
            movie_title TEXT,
            comment TEXT,
            average_rating REAL,
            FOREIGN KEY (movie_title) REFERENCES movies (title))''')
        c.execute('''CREATE TABLE IF NOT EXISTS movies(id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                       title TEXT,summary TEXT, year VARCHAR(12),img_url TEXT,average_rating REAL) ''')
        conn.commit()
        return conn


@app.route('/')
def index():
    connection = init()
    cursor = connection.cursor()
    my_movies = cursor.execute('SELECT id, title, summary, year, average_rating, img_url FROM movies').fetchall()

    # Use a breakpoint in the code line below to debug your script.
    return render_template("index.html",my_movies=my_movies,show_details=False)


@app.route('/movie/add_new',methods=['POST','GET'])
def add_new_movie():
    heading = "Rate movies from the list"

    if request.method == "POST":
        show_movie_lists = True
        new_movies = [movie for movie in movies if movie.get('title')==request.form['title']][0]
        connection = init()
        cursor = connection.cursor()
        cursor.execute(''' INSERT INTO movies(title,summary,year,average_rating,img_url) VALUES (?,?,?,?,?) ''',(
                                         new_movies['title'],new_movies['overview'],new_movies['release_date'],round(new_movies['vote_average'],2),
                                    f'https://www.themoviedb.org/t/p/w600_and_h900_bestv2/{new_movies['poster_path']}'))
        my_movies = connection.execute('SELECT id, title, summary,average_rating, year, img_url FROM movies').fetchall()
        connection.commit()
    else:
        heading = "Add New Movie"
        show_movie_lists = False
        cursor = init().cursor()
        my_movies = cursor.execute('SELECT id, title, summary,average_rating, year,img_url FROM movies').fetchall()
    return render_template("add_movie_form.html",my_movies=my_movies,movies=movies,show_movie_lists=show_movie_lists,heading=heading)

@app.route('/movie/details/<string:title>')
def show_movie_details(title):
    connection = init()
    cursor = connection.cursor()
    my_movies = cursor.execute(''' SELECT DISTINCT movies.id, title, summary,comment, movies.average_rating, year, img_url FROM movies JOIN rating ON rating.movie_title = movies.title WHERE title = ? ''',(title,)).fetchall()
    rate = [movie for movie in my_movies if movie['title']==title ]

    return render_template("index.html", my_movies=my_movies,rate=rate, show_details=True )


@app.route("/movie/delete/<string:title>")
def delete_movie(title):
    connection = init()
    cursor = connection.cursor()
    cursor.execute(''' DELETE FROM movies WHERE title = ? ''',(title,))
    connection.commit()
    return f"<h1 style='color:green;text-align:center;margin-top:3rem'>The movie {title} has been deleted</h1>'"


@app.route('/movies/delete_all')
def delete_all_movie():
    connection = init()
    cursor = connection.cursor()
    cursor.execute('DELETE FROM movies')
    connection.commit()
    connection.close()
    return redirect(url_for('index'))


@app.route('/movies/rating/<string:title>',methods=['POST','GET'])
def add_new_rating(title):
    if request.method == "POST":
        movie_title = request.form['title']
        comment = request.form['comment']
        average_rating = request.form['rate']
        try:
            connection = init()
            cursor = connection.cursor()
            cursor.execute(''' INSERT INTO rating(movie_title,comment,average_rating) VALUES (?,?,?)  ''',(movie_title,comment,average_rating))
        except sqlite3.OperationalError as e:
            return f'Unable to connect to movies.db: {e}'
        else:
            connection.commit()
            return f'Successfully updated the rating.'
    return render_template("rating_form.html",title=title)


@app.route('/movie/rating/update/<title>',methods=['POST'])
def update_movie_rating(title):
    average_rating = request.form['rate']
    try:
        connection = init()
        cursor = connection.cursor()
        cursor.execute('''UPDATE movies SET average_rating=? WHERE title = ? ''',(average_rating,title))
    except sqlite3.OperationalError as e:
        return f'Unable to connect to movies.db: {e}'
    else:
        connection.commit()
        return f'Successfully updated the rating.'


@app.route('/movies/rating/update/<title>')
def update_movie_rating_form(title):
    connection = init()
    cursor = connection.cursor()
    movie = cursor.execute('''SELECT * FROM movies WHERE title = ? ''',(title,)).fetchall()[0]
    return render_template("update_movie_rating.html",movie=movie)

@app.route('/movies/rating/<title>',methods=['POST'])
def rating_form(title):
    return render_template("rating_form.html",title=title)





@app.errorhandler(404)
def page_not_found(e):
    return f'<h1>404</h1><p>The resource could not be found.</p>', 404


@app.errorhandler(500)
def internal_server_error(e):
    return f'<h1>500</h1><p>The server could not be served.</p>', 500

@app.errorhandler(403)
def forbidden(e):
    return f'<h1>403</h1><p>You do not have permission to access this resource.'





# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run(debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
