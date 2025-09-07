from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import sqlite3
import os
from dotenv import load_dotenv
from app.services.tmdb import TMDBService

# Load environment variables
load_dotenv()

app = Flask(
    __name__,
    template_folder="app/templates",
    static_folder="app/static"
)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')

# Database setup
def init_db():
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Movies table
    c.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tmdb_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            overview TEXT,
            release_date TEXT,
            poster_path TEXT,
            genre TEXT,
            rating REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # User interactions table
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            movie_id INTEGER NOT NULL,
            watched BOOLEAN DEFAULT FALSE,
            rating INTEGER DEFAULT 0,
            interested BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (movie_id) REFERENCES movies (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

# Home route
@app.route('/')
def index():
    try:
        # Get popular movies from TMDB
        popular_movies = TMDBService.get_popular_movies()
        movies = popular_movies.get('results', [])[:10]  # Get first 10 movies
        
        # Format movie data for template
        formatted_movies = []
        for movie in movies:
            formatted_movies.append({
                'id': movie['id'],
                'title': movie['title'],
                'poster_path': movie['poster_path'],
                'rating': movie['vote_average'],
                'overview': movie['overview'],
                'release_date': movie['release_date']
            })
        
        return render_template('index.html', movies=formatted_movies)
    except Exception as e:
        # Fallback to sample data if API fails
        print(f"Error fetching from TMDB: {e}")
        sample_movies = [
            {'id': 1, 'title': 'Avengers: Endgame', 'poster_path': '/or06FN3Dka5tukK1e9sl16pB3iy.jpg', 'rating': 8.4},
            {'id': 2, 'title': 'The Dark Knight', 'poster_path': '/qJ2tW6WMUDux911r6m7haRef0WH.jpg', 'rating': 9.0},
        ]
        return render_template('index.html', movies=sample_movies)

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']  # In real app, hash and verify password
        
        # Simple authentication (for demo only)
        if username == 'demo' and password == 'password':
            session['user_id'] = 1
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('login.html')

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

# Movie detail route
@app.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    try:
        # Get movie details from TMDB
        movie = TMDBService.get_movie_details(movie_id)
        credits = TMDBService.get_movie_credits(movie_id)
        
        # Format data for template
        formatted_movie = {
            'id': movie['id'],
            'title': movie['title'],
            'overview': movie['overview'],
            'release_date': movie['release_date'],
            'poster_path': movie['poster_path'],
            'rating': movie['vote_average'],
            'genres': [genre['name'] for genre in movie['genres']],
            'cast': []
        }
        
        # Get top 10 cast members
        for person in credits.get('cast', [])[:10]:
            formatted_movie['cast'].append({
                'name': person['name'],
                'character': person['character'],
                'profile_path': person['profile_path']
            })
        
        return render_template('movie_detail.html', movie=formatted_movie)
    except Exception as e:
        print(f"Error fetching movie details: {e}")
        flash('Error loading movie details', 'error')
        return redirect(url_for('index'))

# API route to get movies
@app.route('/api/movies')
def api_movies():
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    c.execute('SELECT * FROM movies LIMIT 10')
    movies = c.fetchall()
    conn.close()
    
    # Format movies as list of dictionaries
    movies_list = []
    for movie in movies:
        movies_list.append({
            'id': movie[0],
            'tmdb_id': movie[1],
            'title': movie[2],
            'overview': movie[3],
            'release_date': movie[4],
            'poster_path': movie[5],
            'genre': movie[6],
            'rating': movie[7]
        })
    
    return jsonify(movies_list)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    if query:
        try:
            results = TMDBService.search_movies(query)
            movies = results.get('results', [])
            return render_template('search.html', movies=movies, query=query)
        except Exception as e:
            print(f"Search error: {e}")
            flash('Error performing search', 'error')
    return render_template('search.html', movies=[], query=query)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
