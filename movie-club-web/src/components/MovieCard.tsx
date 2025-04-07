import React from 'react';
import { Link } from 'react-router-dom';
import { Movie } from '../types/movie';
import { getPosterUrl } from '../services/movieService';

interface MovieCardProps {
  movie: Movie;
}

const MovieCard: React.FC<MovieCardProps> = ({ movie }) => {
  return (
    <Link to={`/movie/${movie.id}`} className="block transition-transform hover:scale-105">
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="relative pb-[150%]">
          <img 
            src={getPosterUrl(movie.poster_path)} 
            alt={movie.title}
            className="absolute inset-0 w-full h-full object-cover"
          />
        </div>
        <div className="p-4">
          <h3 className="font-bold text-gray-900 truncate">{movie.title}</h3>
          <p className="text-sm text-gray-500">
            {movie.release_date ? new Date(movie.release_date).getFullYear() : 'Unknown'}
          </p>
          <div className="mt-2 flex items-center">
            <div className="flex items-center bg-gray-800 text-white rounded-full px-2 py-1 text-xs">
              <svg className="w-3 h-3 text-yellow-400 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118l-2.799-2.034c-.784-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
              </svg>
              {movie.vote_average.toFixed(1)}
            </div>
          </div>
        </div>
      </div>
    </Link>
  );
};

export default MovieCard;
