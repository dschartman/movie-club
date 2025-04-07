import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Movie } from '../types/movie';

interface RandomMoviePickerProps {
  movies: Movie[];
}

const RandomMoviePicker: React.FC<RandomMoviePickerProps> = ({ movies }) => {
  const navigate = useNavigate();
  const [isAnimating, setIsAnimating] = useState(false);

  const pickRandomMovie = () => {
    if (movies.length === 0 || isAnimating) return;
    
    setIsAnimating(true);
    
    // Simulate spinning animation before selecting
    setTimeout(() => {
      const randomIndex = Math.floor(Math.random() * movies.length);
      const selectedMovie = movies[randomIndex];
      
      setIsAnimating(false);
      navigate(`/movie/${selectedMovie.id}`);
    }, 1000);
  };

  return (
    <div className="mb-6 flex items-center">
      <button
        onClick={pickRandomMovie}
        disabled={movies.length === 0 || isAnimating}
        className={`
          px-4 py-2 rounded-lg text-white font-semibold 
          flex items-center space-x-2
          ${movies.length === 0 
            ? 'bg-gray-400 cursor-not-allowed' 
            : isAnimating 
              ? 'bg-yellow-500' 
              : 'bg-gradient-to-r from-purple-500 to-indigo-600 hover:from-purple-600 hover:to-indigo-700'
          }
          transition-all duration-300
        `}
      >
        {isAnimating ? (
          <>
            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span>Picking...</span>
          </>
        ) : (
          <>
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 3a1 1 0 01.707.293l3 3a1 1 0 01-1.414 1.414L10 5.414 7.707 7.707a1 1 0 01-1.414-1.414l3-3A1 1 0 0110 3zm-3.707 9.293a1 1 0 011.414 0L10 14.586l2.293-2.293a1 1 0 011.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
            <span>Pick Random Movie{movies.length > 0 ? ` (${movies.length})` : ''}</span>
          </>
        )}
      </button>
    </div>
  );
};

export default RandomMoviePicker;
