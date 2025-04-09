from fastapi import APIRouter, Path, Query, HTTPException, Depends
from typing import Dict, List, Optional

from app.schemas.movie import Movie
from app.services.movie_service import MovieService

router = APIRouter(tags=["movies"])

def get_movie_service():
    return MovieService()

@router.get("/movies", response_model=Dict[str, Movie])
def get_all_movies(movie_service: MovieService = Depends(get_movie_service)):
    """Get all movies in the database."""
    return movie_service.get_all_movies()

@router.get("/movies/{movie_id}", response_model=Movie)
def get_movie(
    movie_id: int = Path(..., description="The ID of the movie to retrieve"),
    movie_service: MovieService = Depends(get_movie_service)
):
    """Get a specific movie by ID."""
    movie = movie_service.get_movie(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail=f"Movie with ID {movie_id} not found")
    return movie

@router.get("/random", response_model=Movie)
def get_random_movie(movie_service: MovieService = Depends(get_movie_service)):
    """Get a random movie."""
    movie = movie_service.get_random_movie()
    if not movie:
        raise HTTPException(status_code=404, detail="No movies found in database")
    return movie

@router.get("/genres", response_model=List[Dict])
def get_all_genres(movie_service: MovieService = Depends(get_movie_service)):
    """Get all available genres with counts."""
    return movie_service.get_all_genres()

@router.get("/movies/genre/{genre_id}", response_model=List[Movie])
def get_movies_by_genre(
    genre_id: int = Path(..., description="The ID of the genre to filter by"),
    movie_service: MovieService = Depends(get_movie_service)
):
    """Get movies filtered by genre."""
    return movie_service.get_movies_by_genre(genre_id)
