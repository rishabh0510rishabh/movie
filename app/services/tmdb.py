import requests
import os
from dotenv import load_dotenv

load_dotenv()

class TMDBService:
    BASE_URL = "https://api.themoviedb.org/3"
    API_KEY = os.getenv('TMDB_API_KEY')
    
    @classmethod
    def get_popular_movies(cls, page=1):
        url = f"{cls.BASE_URL}/movie/popular?api_key={cls.API_KEY}&page={page}"
        response = requests.get(url)
        return response.json()
    
    @classmethod
    def get_movie_details(cls, movie_id):
        url = f"{cls.BASE_URL}/movie/{movie_id}?api_key={cls.API_KEY}"
        response = requests.get(url)
        return response.json()
    
    @classmethod
    def get_movie_credits(cls, movie_id):
        url = f"{cls.BASE_URL}/movie/{movie_id}/credits?api_key={cls.API_KEY}"
        response = requests.get(url)
        return response.json()
    
    @classmethod
    def search_movies(cls, query, page=1):
        url = f"{cls.BASE_URL}/search/movie?api_key={cls.API_KEY}&query={query}&page={page}"
        response = requests.get(url)
        return response.json()
    
    @classmethod
    def get_genres(cls):
        url = f"{cls.BASE_URL}/genre/movie/list?api_key={cls.API_KEY}"
        response = requests.get(url)
        return response.json()
    
    @classmethod
    def get_movie_videos(cls, movie_id):
        url = f"{cls.BASE_URL}/movie/{movie_id}/videos?api_key={cls.API_KEY}"
        response = requests.get(url)
        return response.json()

    # --- Methods for TV Shows ---
    @classmethod
    def get_popular_tv(cls, page=1):
        url = f"{cls.BASE_URL}/tv/popular?api_key={cls.API_KEY}&page={page}"
        response = requests.get(url)
        return response.json()

    @classmethod
    def get_tv_details(cls, tv_id):
        url = f"{cls.BASE_URL}/tv/{tv_id}?api_key={cls.API_KEY}"
        response = requests.get(url)
        return response.json()

    @classmethod
    def get_tv_videos(cls, tv_id):
        url = f"{cls.BASE_URL}/tv/{tv_id}/videos?api_key={cls.API_KEY}"
        response = requests.get(url)
        return response.json()
