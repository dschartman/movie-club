import time

def format_movie_list(movies, client=None, page=1, page_size=25, users_by_movie=None):
    """Format movie list for slack display with pagination."""
    if not movies:
        return "No movies found in the database."

    # Sort movies alphabetically
    movies.sort(key=lambda x: x.title)
    
    # Calculate total pages
    total_pages = (len(movies) + page_size - 1) // page_size
    
    # Get movies for current page
    start_idx = (page - 1) * page_size
    end_idx = min(start_idx + page_size, len(movies))
    page_movies = movies[start_idx:end_idx]
    
    movie_lines = []
    
    # Add page info header
    movie_lines.append(f"*Page {page}/{total_pages} (Showing movies {start_idx+1}-{end_idx} of {len(movies)})*")
    movie_lines.append("")  # Empty line for spacing
    
    for i, movie in enumerate(page_movies, start_idx + 1):
        year = movie.release_date[:4] if movie.release_date else "N/A"
        rating = f"{movie.vote_average}/10" if movie.vote_average else "N/A"
        line = f"{i}. *{movie.title}* ({year}) - {rating}"

        # Add user information if available
        if users_by_movie and movie.id in users_by_movie and users_by_movie[movie.id]:
            line += f" - Added by: {', '.join(users_by_movie[movie.id])}"

        movie_lines.append(line)

    return "\n".join(movie_lines)

def format_movie_detail(movie, client=None, users_by_movie=None):
    """Format a single movie for detailed slack display."""
    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": movie.title, "emoji": True},
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Year:* {movie.release_date[:4] if movie.release_date else 'N/A'}",
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Rating:* {movie.vote_average}/10 ({movie.vote_count} votes)",
                },
            ],
        },
    ]

    # Add genres if available
    if movie.genres:
        blocks.append(
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Genres:* {', '.join(movie.genres)}"}
                ],
            }
        )

    # Add users who added this movie
    # First check if pre-fetched user data is available
    if users_by_movie and movie.id in users_by_movie and users_by_movie[movie.id]:
        blocks.append(
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Added by:* {', '.join(users_by_movie[movie.id])}",
                    }
                ],
            }
        )
    # Fallback to fetching users if needed and client is provided
    elif client and movie.id:
        from src.handlers.cache_management import get_user_names
        from src.api_client import ApiClient
        
        api_client = ApiClient()
        user_ids = api_client.get_movie_users(movie.id)
        if user_ids:
            user_names = get_user_names(client, user_ids)
            blocks.append(
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Added by:* {', '.join(user_names)}",
                        }
                    ],
                }
            )

    # Add overview if available
    if movie.overview:
        blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Overview:*\n{movie.overview[:300]}{'...' if len(movie.overview) > 300 else ''}",
                },
            }
        )

    # Add poster if available
    if movie.get_poster_url():
        blocks.append(
            {
                "type": "image",
                "image_url": movie.get_poster_url(),
                "alt_text": movie.title,
            }
        )

    # Add TMDB link
    blocks.append(
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"<https://www.themoviedb.org/movie/{movie.id}|View on TMDB>",
                }
            ],
        }
    )

    return blocks

def handle_pagination(page, respond, app_client, get_all_movies_func, get_all_movie_users_func):
    """Common handler for pagination."""
    start_time = time.time()
    movies = get_all_movies_func()
    page_size = 25
    
    # Pre-fetch all user data for these movies
    users_by_movie = get_all_movie_users_func(movies, app_client)
    print(f"User data prefetch completed in {time.time() - start_time:.2f} seconds")
    
    # Format the movie list with pre-fetched user data
    format_start = time.time()
    movie_list = format_movie_list(movies, app_client, page, page_size, users_by_movie)
    print(f"Formatting took {time.time() - format_start:.2f} seconds")
    
    total_pages = (len(movies) + page_size - 1) // page_size
    
    # Create page navigation buttons
    actions = []
    if page > 1:
        actions.append({
            "type": "button",
            "text": {"type": "plain_text", "text": "◀️ Previous", "emoji": True},
            "value": f"{page-1}",
            "action_id": "movie_prev_page"
        })
    
    if page < total_pages:
        actions.append({
            "type": "button",
            "text": {"type": "plain_text", "text": "Next ▶️", "emoji": True},
            "value": f"{page+1}",
            "action_id": "movie_next_page"
        })
    
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Movie List ({len(movies)} movies)*",
            },
        },
        {"type": "section", "text": {"type": "mrkdwn", "text": movie_list}}
    ]
    
    if actions:
        blocks.append({"type": "actions", "elements": actions})
    
    # Update the original message
    respond({"blocks": blocks, "replace_original": True})
    
    # Log performance
    end_time = time.time()
    print(f"Page {page} took {end_time - start_time:.2f} seconds to generate")
