import axios from 'axios';
import { Movie, MovieCollection } from '../types/movie';

export const fetchAllMovies = async (): Promise<MovieCollection> => {
  try {
    const response = await axios.get('http://localhost:3001/api/movies');
    return response.data;
  } catch (error) {
    console.error('Error fetching movies:', error);
    return {};
  }
};

export const fetchMovieById = async (id: number): Promise<Movie | null> => {
  try {
    const response = await axios.get(`http://localhost:3001/api/movies/${id}`);
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
