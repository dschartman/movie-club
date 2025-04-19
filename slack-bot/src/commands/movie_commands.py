from typing import Any, Callable, Dict, List, Optional

from src.api_client import ApiClient
from src.commands.command_base import SlackCommand, register_command
from src.handlers.cache_management import get_all_movie_users, get_cached_movies
from src.handlers.pagination import handle_pagination

class MovieCommand(SlackCommand):
    """Base class for movie-related commands."""
    
    def __init__(self, name: str, description: str, examples: List[str] = None):
        super().__init__(name, description, examples)
        self.api_client = ApiClient()
    
    def get_movies(self):
        """Get cached movies."""
        return get_cached_movies(self.api_client)
    
    def get_all_users(self, movies, client):
        """Get all users for a list of movies."""
        return get_all_movie_users(movies, client, self.api_client)

@register_command
class ListMoviesCommand(MovieCommand):
    """Command to list all movies."""
    
    def __init__(self):
        super().__init__(
            name="movies",
            description="List all movies in the database",
            examples=[
                "/movies",
                "/movies 2"  # Page 2
            ]
        )
    
    async def execute(self, ack: Callable, respond: Callable, command: Dict[str, Any], **kwargs) -> None:
        """Execute the command to list all movies."""
        # Acknowledge command request
        ack()
        
        # Get the Slack app client
        app_client = kwargs.get("app_client")
        if not app_client:
            respond("Error: Slack client not available")
            return
        
        # Parse command text for page number
        command_text = command.get("text", "").strip()
        try:
            page = int(command_text) if command_text else 1
            if page < 1:
                page = 1
        except ValueError:
            page = 1
        
        # Handle pagination
        handle_pagination(
            page,
            respond,
            app_client,
            lambda: self.get_movies(),
            lambda movies, client: self.get_all_users(movies, client)
        )

@register_command
class RandomMovieCommand(MovieCommand):
    """Command to pick a random movie."""
    
    def __init__(self):
        super().__init__(
            name="random",
            description="Pick a random movie to watch",
            examples=["/random"]
        )
    
    async def execute(self, ack: Callable, respond: Callable, command: Dict[str, Any], **kwargs) -> None:
        """Execute the command to get a random movie."""
        import time
        
        # Acknowledge command request
        ack()
        start_time = time.time()
        
        # Get the Slack app client
        app_client = kwargs.get("app_client")
        if not app_client:
            respond("Error: Slack client not available")
            return
        
        # Get a random movie
        movie = self.api_client.get_random_movie()
        
        if not movie:
            respond("No movies found in the database.")
            return
        
        # Get pre-fetched user data or create it for this single movie
        from src.handlers.cache_management import movie_users_cache
        
        if movie.id and movie.id in movie_users_cache:
            users_by_movie = movie_users_cache
        else:
            # For a single movie, we can fetch just its users
            users_by_movie = {}
            if movie.id:
                user_ids = self.api_client.get_movie_users(movie.id)
                if user_ids:
                    from src.handlers.cache_management import get_user_names
                    user_names = get_user_names(app_client, user_ids)
                    users_by_movie[movie.id] = user_names
        
        from src.handlers.pagination import format_movie_detail
        blocks = format_movie_detail(movie, app_client, users_by_movie)
        respond({"blocks": blocks})
        
        end_time = time.time()
        print(f"Random movie command took {end_time - start_time:.2f} seconds")

@register_command
class HelpCommand(SlackCommand):
    """Command to show help information."""
    
    def __init__(self):
        super().__init__(
            name="help",
            description="Show available commands and how to use them",
            examples=[
                "/help",
                "/help movies"
            ]
        )
    
    async def execute(self, ack: Callable, respond: Callable, command: Dict[str, Any], **kwargs) -> None:
        """Execute the command to show help information."""
        from src.commands.command_base import registry
        
        # Acknowledge command request
        ack()
        
        # Parse command text to see if user wants help with a specific command
        command_text = command.get("text", "").strip()
        
        if command_text:
            # Show help for specific command
            specific_command = registry.get_command(command_text)
            if specific_command:
                respond(specific_command.get_usage())
            else:
                respond(f"Command `{command_text}` not found. Try `/help` to see all available commands.")
            return
        
        # Show help for all commands
        all_commands = registry.list_commands()
        help_text = "*Available Commands:*\n\n"
        
        for cmd in sorted(all_commands, key=lambda x: x.name):
            help_text += f"• `/{cmd.name}`: {cmd.description}\n"
        
        help_text += "\nUse `/help [command]` for more details about a specific command."
        
        respond(help_text)

@register_command
class GenresCommand(MovieCommand):
    """Command to list movie genres."""
    
    def __init__(self):
        super().__init__(
            name="genres",
            description="List all available movie genres",
            examples=["/genres"]
        )
    
    async def execute(self, ack: Callable, respond: Callable, command: Dict[str, Any], **kwargs) -> None:
        """Execute the command to list all genres."""
        # Acknowledge command request
        ack()
        
        try:
            # Get all genres from the API
            response = self.api_client.get_all_genres()
            
            if not response or len(response) == 0:
                respond("No genres found in the database.")
                return
            
            # Sort genres by count (descending)
            sorted_genres = sorted(response, key=lambda x: x.get("count", 0), reverse=True)
            
            # Format response
            blocks = [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": "Movie Genres", "emoji": True}
                },
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"*{len(sorted_genres)} genres found*"}
                }
            ]
            
            # Create a formatted list of genres with counts
            genre_text = ""
            for genre in sorted_genres:
                genre_name = genre.get("name", "Unknown")
                genre_count = genre.get("count", 0)
                genre_text += f"• *{genre_name}*: {genre_count} movie{'s' if genre_count != 1 else ''}\n"
            
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": genre_text}
            })
            
            respond({"blocks": blocks})
            
        except Exception as e:
            print(f"Error fetching genres: {e}")
            respond(f"Error fetching genres: {str(e)}")
