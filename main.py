from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
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
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///movies.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- NEW: Initialize extensions ---
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# --- NEW: User Model for Database ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

# --- NEW: User Loader for Flask-Login ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Home route
@app.route('/')
def index():
    try:
        popular_movies = TMDBService.get_popular_movies().get('results', [])[:10]
        popular_tv = TMDBService.get_popular_tv().get('results', [])[:10]
        return render_template('index.html', movies=popular_movies, tv_shows=popular_tv)
    except Exception as e:
        print(f"Error fetching from TMDB: {e}")
        return render_template('index.html', movies=[], tv_shows=[])

# --- NEW: Registration Route ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Check if user already exists
        user_exists = User.query.filter_by(username=username).first()
        email_exists = User.query.filter_by(email=email).first()
        
        if user_exists:
            flash('Username already exists. Please choose a different one.', 'error')
        elif email_exists:
            flash('Email address is already registered.', 'error')
        else:
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
            
    return render_template('register.html')

# --- UPDATED: Login Route ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=True)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

# --- UPDATED: Logout Route ---
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# Movie detail route
@app.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    try:
        movie = TMDBService.get_movie_details(movie_id)
        videos = TMDBService.get_movie_videos(movie_id).get('results', [])
        trailer = next((v for v in videos if v['type'] == 'Trailer'), None)
        return render_template('movie_detail.html', movie=movie, trailer=trailer)
    except Exception as e:
        print(f"Error fetching movie details: {e}")
        flash('Error loading movie details.', 'error')
        return redirect(url_for('index'))
    
# TV show detail route
@app.route('/tv/<int:tv_id>')
def tv_detail(tv_id):
    try:
        tv_show = TMDBService.get_tv_details(tv_id)
        videos = TMDBService.get_tv_videos(tv_id).get('results', [])
        trailer = next((v for v in videos if v['type'] == 'Trailer'), None)
        # Use a generic detail template for now
        return render_template('content_detail.html', content=tv_show, trailer=trailer, content_type='tv')
    except Exception as e:
        print(f"Error fetching TV details: {e}")
        flash('Error loading TV show details.', 'error')
        return redirect(url_for('index'))

# Search route
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
    with app.app_context():
        db.create_all() # Create database tables if they don't exist
    app.run(debug=True, host='0.0.0.0', port=5000)