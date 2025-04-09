from fastapi import APIRouter, Path, Query, HTTPException, Depends
from typing import List

from app.services.movie_service import MovieService

router = APIRouter(tags=["users"])

def get_movie_service():
    return MovieService()

@router.get("/movies/{movie_id}/users", response_model=List[str])
def get_movie_users(
    movie_id: int = Path(..., description="The ID of the movie"),
    movie_service: MovieService = Depends(get_movie_service)
):
    """Get users who have added this movie."""
    return movie_service.get_movie_users(movie_id)

@router.post("/movies/{movie_id}/users")
def add_user_to_movie(
    movie_id: int = Path(..., description="The ID of the movie"),
    user_id: str = Query(..., description="User ID to add to the movie"),
    movie_service: MovieService = Depends(get_movie_service)
):
    """Add a user to a movie."""
    success = movie_service.add_user_to_movie(movie_id, user_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to add user to movie")
    return {"status": "success"}
