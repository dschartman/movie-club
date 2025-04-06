from src.tmdb_api import search_movies, get_movie_details, get_popular_movies, save_to_json
from src.models.movie import Movie
import json

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

def main():
    print("Welcome to Movie Club!")
    print("----------------------")
    
    while True:
        print("\nOptions:")
        print("1. Search for a movie")
        print("2. Show popular movies")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ")
        
        if choice == '1':
            search_and_display()
        elif choice == '2':
            show_popular_movies()
        elif choice == '3':
            print("\nThanks for using Movie Club!")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
