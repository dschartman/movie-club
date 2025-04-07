import axios from 'axios';
import { Movie, MovieCollection } from '../types/movie';

// Use runtime config or fall back to environment variable or default to relative path
const API_BASE_URL = (window as any).MOVIE_CLUB_CONFIG?.API_URL || process.env.REACT_APP_API_URL || '/api';

export const fetchAllMovies = async (): Promise<MovieCollection> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/movies`);
    return response.data;
  } catch (error) {
    console.error('Error fetching movies:', error);
    console.log('API_BASE_URL:', API_BASE_URL);
    return {};
  }
};

export const fetchMovieById = async (id: number): Promise<Movie | null> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/movies/${id}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching movie ${id}:`, error);
    return null;
  }
};

export const getPosterUrl = (posterPath: string | null, size: string = 'w500'): string => {
  if (!posterPath) return '/placeholder-poster.jpg';
  return `https://image.tmdb.org/t/p/${size}${posterPath}`;
};

export const getBackdropUrl = (backdropPath: string | null, size: string = 'original'): string => {
  if (!backdropPath) return '/placeholder-backdrop.jpg';
  return `https://image.tmdb.org/t/p/${size}${backdropPath}`;
};
