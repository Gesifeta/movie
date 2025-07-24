from flask import Flask, render_template, request, redirect, url_for,json,jsonify

app = Flask(__name__)
with open("movies.json",'r',encoding='utf-8') as json_file:
    movies = json.load(json_file)['results']
@app.route('/')
def index():
    # Use a breakpoint in the code line below to debug your script.
    return render_template("index.html",movies=movies,show_details=False)

@app.route('/movie/add')
def add_new_movie():
    pass


@app.route('/movie/details/<int:rank>')
def movie_details(rank):
    movie = [movie for movie in movies if movie['rank'] == rank]

    return render_template("index.html", movie=movie[0],show_details=True )


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run(debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
