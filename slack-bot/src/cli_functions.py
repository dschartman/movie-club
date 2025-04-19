"""
CLI utility functions for Movie Club bot administration and testing.
Provides functionality for searching movies, adding them from URLs,
and interacting with the Movie Club API.
"""

from src.tmdb_api import (
    search_movies, get_movie_details, get_popular_movies, 
    save_to_json, get_movie_by_url
)
from src.api_client import ApiClient
from src.slack_bot import start_slack_bot
from src.models.movie import Movie
import json
import os
from src.config import API_BASE_URL

# Initialize API client
api_client = ApiClient(base_url=API_BASE_URL)

def display_movie_info(movie):
    """Display formatted information about a movie."""
    print(f"\n{'=' * 50}")
    print(f"Title: {movie.title}")
    if movie.original_title != movie.title:
        print(f"Original Title: {movie.original_title}")
    print(f"Released: {movie.release_date}")
    print(f"Rating: {movie.vote_average}/10 ({movie.vote_count} votes)")
    if movie.genres:
        print(f"Genres: {', '.join(movie.genres)}")
    if movie.runtime:
        print(f"Runtime: {movie.runtime} minutes")
    print(f"\nOverview: {movie.overview}")
    if movie.get_poster_url():
        print(f"\nPoster: {movie.get_poster_url()}")
    
    # Try to get users who added this movie
    try:
        users = api_client.get_movie_users(movie.id)
        if users:
            print(f"\nAdded by: {', '.join(users)}")
    except Exception as e:
        print(f"Could not retrieve user info: {e}")
        
    print(f"{'=' * 50}")

def search_and_display():
    """Search for movies and display the results."""
    query = input("Enter a movie title to search: ")
    if not query:
        return
    
    print(f"\nSearching for '{query}'...")
    results = search_movies(query)
    
    if not results or 'results' not in results or not results['results']:
        print("No results found.")
        return
    
    movies = results['results']
    print(f"\nFound {len(movies)} results:")
    
    for i, movie_data in enumerate(movies[:10], 1):
        year = movie_data.get('release_date', '')[:4] if movie_data.get('release_date') else 'N/A'
        print(f"{i}. {movie_data['title']} ({year}) - ID: {movie_data['id']}")
    
    if len(movies) > 10:
        print(f"...and {len(movies) - 10} more.")
    
    try:
        selection = int(input("\nEnter a number to see details (0 to cancel): "))
        if 1 <= selection <= min(10, len(movies)):
            movie_id = movies[selection-1]['id']
            movie_details = get_movie_details(movie_id)
            if movie_details:
                movie = Movie(movie_details)
                display_movie_info(movie)
            else:
                print("Couldn't retrieve movie details.")
    except (ValueError, IndexError):
        print("Invalid selection.")

def show_popular_movies():
    """Display current popular movies."""
    print("\nFetching popular movies...")
    popular = get_popular_movies()
    
    if not popular or 'results' not in popular or not popular['results']:
        print("Couldn't retrieve popular movies.")
        return
    
    # Save the API response to a JSON file
    save_to_json(popular, "popular_movies.json")
    
    movies = popular['results']
    print("\nCurrent Popular Movies:")
    
    for i, movie_data in enumerate(movies[:10], 1):
        year = movie_data.get('release_date', '')[:4] if movie_data.get('release_date') else 'N/A'
        print(f"{i}. {movie_data['title']} ({year}) - {movie_data['vote_average']}/10")

def get_movie_from_url():
    """Get a movie from a TMDB URL and display its information."""
    url = input("\nEnter a TMDB movie URL (e.g., https://www.themoviedb.org/movie/550-fight-club): ")
    if not url:
        return
    
    print(f"\nFetching movie from URL: {url}")
    movie_data, error = get_movie_by_url(url)
    
    if error:
        print(f"Error: {error}")
        return
    
    if movie_data:
        movie = Movie(movie_data)
        display_movie_info(movie)
        
        # Ask if the user wants to add the movie to the API
        if input("\nWould you like to add this movie to the API? (y/n): ").lower() == 'y':
            try:
                added = api_client.add_movie(movie_data)
                if added:
                    print(f"Movie '{movie.title}' successfully added to the API!")
                else:
                    print("Failed to add movie to the API.")
            except Exception as e:
                print(f"Error adding movie to API: {e}")
    else:
        print("Couldn't retrieve movie details.")

def main():
    print("Welcome to Movie Club CLI!")
    print("-------------------------")
    
    while True:
        print("\nOptions:")
        print("1. Search for a movie")
        print("2. Show popular movies")
        print("3. Get movie from TMDB URL")
        print("4. Start Slack bot")
        print("5. Get random movie from API")
        print("6. List all movies in API")
        print("7. Exit")
        
        choice = input("\nEnter your choice (1-7): ")
        
        if choice == '1':
            search_and_display()
        elif choice == '2':
            show_popular_movies()
        elif choice == '3':
            get_movie_from_url()
        elif choice == '4':
            start_slack_bot()
        elif choice == '5':
            try:
                random_movie = api_client.get_random_movie()
                if random_movie:
                    display_movie_info(random_movie)
                else:
                    print("No movies available in the API.")
            except Exception as e:
                print(f"Error getting random movie: {e}")
        elif choice == '6':
            try:
                all_movies = api_client.get_all_movies()
                if all_movies:
                    print(f"\nFound {len(all_movies)} movies in the API:")
                    for movie_id, movie in all_movies.items():
                        print(f"- {movie.title} (ID: {movie.id})")
                else:
                    print("No movies available in the API.")
            except Exception as e:
                print(f"Error getting all movies: {e}")
        elif choice == '7':
            print("\nThanks for using Movie Club!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
