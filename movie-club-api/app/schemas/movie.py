from pydantic import BaseModel
from typing import List, Dict, Optional, Any

class Movie(BaseModel):
    id: int
    title: str
    original_title: Optional[str] = ""
    overview: Optional[str] = ""
    release_date: Optional[str] = ""
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None
    popularity: float = 0.0
    vote_average: float = 0.0
    vote_count: int = 0
    genres: List[Dict[str, Any]] = []
    runtime: Optional[int] = None
    
    class Config:
        schema_extra = {
            "example": {
                "id": 550,
                "title": "Fight Club",
                "overview": "A ticking-time-bomb insomniac and a slippery soap salesman...",
                "release_date": "1999-10-15",
                "poster_path": "/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg",
                "genres": [{"id": 18, "name": "Drama"}],
                "vote_average": 8.4
            }
        }
