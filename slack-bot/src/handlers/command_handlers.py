import time
from src.handlers.pagination import format_movie_detail

def handle_next_page(ack, body, respond, app_client, get_cached_movies, get_all_movie_users_func, handle_pagination_func):
    """Handle pagination next page button."""
    ack()
    page = int(body["actions"][0]["value"])
    handle_pagination_func(page, respond)

def handle_prev_page(ack, body, respond, app_client, get_cached_movies, get_all_movie_users_func, handle_pagination_func):
    """Handle pagination previous page button."""
    ack()
    page = int(body["actions"][0]["value"])
    handle_pagination_func(page, respond)
