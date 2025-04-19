import time
import os
from functools import wraps
from cachetools import TTLCache

# Cache for user information to reduce API calls - TTL 24 hours
user_cache = TTLCache(maxsize=1000, ttl=86400)

# Cache for movie data - TTL 2 minutes
movie_cache = TTLCache(maxsize=100, ttl=120)

# Cache for movie users data - TTL 5 minutes
movie_users_cache = TTLCache(maxsize=100, ttl=300)

def ttl_cached(cache_obj, key_func=None):
    """
    Decorator that uses a specified TTLCache object for caching
    
    Args:
        cache_obj: The TTLCache object to use
        key_func: Optional function to generate cache key from function args
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate key based on function arguments
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                # Default key generation using function name and arguments
                key = str(func.__name__) + str(args) + str(sorted(kwargs.items()))
                
            if key in cache_obj:
                return cache_obj[key]
                
            result = func(*args, **kwargs)
            cache_obj[key] = result
            return result
        return wrapper
    return decorator

# Helper to generate user cache key based on user_id
def _user_key(client, user_ids):
    if isinstance(user_ids, list):
        return ','.join(sorted(user_ids))
    return str(user_ids)

# Helper to generate movie users cache key
def _movie_users_key(movies, client, api_client):
    # Use the first few movie IDs as the key
    movie_ids = sorted([str(movie.id) for movie in movies if movie.id])[:5]
    return ','.join(movie_ids)

@ttl_cached(user_cache, key_func=_user_key)
def get_user_names(client, user_ids):
    """Convert user IDs to display names with caching."""
    user_names = []
    
    for user_id in user_ids:
        try:
            # This function will only be called on cache miss
            if os.getenv("DEBUG_SLACK_API"):
                print(f"Cache miss for user {user_id}, fetching from Slack API")
                
            user_info = client.users_info(user=user_id)

            # Debug the response if needed
            if os.getenv("DEBUG_SLACK_API"):
                print(f"User info for {user_id}: {user_info.data}")

            # Try different fields in order of preference
            user_data = user_info.get("user", {})
            profile = user_data.get("profile", {})

            # Try several name options in order of preference
            display_name = profile.get("display_name_normalized") or profile.get(
                "display_name"
            )
            if not display_name or display_name == "":
                display_name = user_data.get("real_name") or profile.get("real_name")
            if not display_name or display_name == "":
                display_name = user_data.get("name")  # Fallback to username

            # If still nothing, use a better formatted fallback
            if not display_name or display_name == "":
                display_name = f"@{user_id.replace('U', '')}"
            
            user_names.append(display_name)

        except Exception as e:
            print(f"Error getting user info for {user_id}: {str(e)}")
            # Use a more friendly fallback
            user_names.append("@unknown-user")

    return user_names

@ttl_cached(movie_users_cache, key_func=_movie_users_key)
def get_all_movie_users(movies, client, api_client):
    """Get all users for a list of movies with efficient caching."""
    print("Prefetching all movie users data...")
    fetch_start = time.time()
    
    result = {}
    all_user_ids = set()
    movie_user_map = {}
    
    # First, collect all user IDs for all movies in one pass
    for movie in movies:
        if movie.id:
            user_ids = api_client.get_movie_users(movie.id)
            if user_ids:
                movie_user_map[movie.id] = user_ids
                all_user_ids.update(user_ids)
    
    fetch_api_time = time.time()
    print(f"API fetching took {fetch_api_time - fetch_start:.2f} seconds")
    
    # Now get user names for all users at once
    all_user_names = {}
    if all_user_ids:
        user_names_list = get_user_names(client, list(all_user_ids))
        all_user_names = dict(zip(all_user_ids, user_names_list))
    
    fetch_names_time = time.time()
    print(f"User name fetching took {fetch_names_time - fetch_api_time:.2f} seconds")
    
    # Map user IDs to names for each movie
    for movie_id, user_ids in movie_user_map.items():
        result[movie_id] = [all_user_names.get(user_id, "@unknown") for user_id in user_ids]
    
    print(f"Total user data prefetch took {time.time() - fetch_start:.2f} seconds")
    return result

@ttl_cached(movie_cache)
def get_cached_movies(api_client):
    """Get all movies from the API with caching."""
    # This function will only be called on cache miss
    movies_dict = api_client.get_all_movies()
    return list(movies_dict.values())
