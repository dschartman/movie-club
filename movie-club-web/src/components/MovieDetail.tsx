import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Movie } from '../types/movie';
import { fetchMovieById, getPosterUrl, getBackdropUrl } from '../services/movieService';

const MovieDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [movie, setMovie] = useState<Movie | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const loadMovie = async () => {
      if (id) {
        try {
          const movieData = await fetchMovieById(parseInt(id));
          setMovie(movieData);
        } catch (error) {
          console.error('Failed to load movie:', error);
        } finally {
          setLoading(false);
        }
      }
    };

    loadMovie();
  }, [id]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (!movie) {
    return (
      <div className="container mx-auto px-4 py-8 text-center">
        <h2 className="text-2xl font-bold mb-4">Movie not found</h2>
        <Link to="/" className="text-blue-500 hover:underline">
          Back to Movies
        </Link>
      </div>
    );
  }

  const releaseYear = movie.release_date
    ? new Date(movie.release_date).getFullYear()
    : 'Unknown';

  const formatRuntime = (minutes: number | null) => {
    if (!minutes) return 'Unknown';
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}h ${mins}m`;
  };

  return (
    <div>
      {/* Backdrop Image */}
      <div className="relative h-64 md:h-96 overflow-hidden">
        <div className="absolute inset-0 bg-black/50 z-10"></div>
        <img
          src={getBackdropUrl(movie.backdrop_path)}
          alt={movie.title}
          className="w-full h-full object-cover"
        />
      </div>

      {/* Movie Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="flex flex-col md:flex-row -mt-32 relative z-20">
          {/* Poster */}
          <div className="w-48 md:w-64 mx-auto md:mx-0 mb-6 md:mb-0">
            <img
              src={getPosterUrl(movie.poster_path)}
              alt={movie.title}
              className="w-full rounded-lg shadow-lg"
            />
          </div>

          {/* Details */}
          <div className="md:ml-8 md:mt-32 text-center md:text-left">
            <h1 className="text-3xl font-bold text-white md:text-gray-900">
              {movie.title} <span className="font-normal">({releaseYear})</span>
            </h1>
            
            {/* Movie Meta */}
            <div className="flex flex-wrap justify-center md:justify-start gap-4 mt-3 text-sm text-white md:text-gray-600">
              <div className="flex items-center bg-gray-800 md:bg-gray-200 rounded-full px-3 py-1">
                <span>{movie.release_date}</span>
              </div>
              {movie.genres && (
                <div className="flex items-center bg-gray-800 md:bg-gray-200 rounded-full px-3 py-1">
                  <span>{movie.genres.map(g => g.name).join(', ')}</span>
                </div>
              )}
              <div className="flex items-center bg-gray-800 md:bg-gray-200 rounded-full px-3 py-1">
                <span>{formatRuntime(movie.runtime)}</span>
              </div>
              <div className="flex items-center bg-gray-800 md:bg-gray-200 rounded-full px-3 py-1">
                <svg className="w-4 h-4 text-yellow-400 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118l-2.799-2.034c-.784-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
                <span>{movie.vote_average.toFixed(1)}</span>
              </div>
            </div>

            {/* Overview */}
            <div className="mt-6 bg-white md:bg-transparent p-4 md:p-0 rounded-lg">
              <h3 className="text-xl font-semibold mb-2">Overview</h3>
              <p className="text-gray-700">{movie.overview}</p>
            </div>
          </div>
        </div>

        {/* Back button */}
        <div className="mt-8">
          <Link
            to="/"
            className="inline-flex items-center text-blue-600 hover:text-blue-800"
          >
            <svg
              className="w-4 h-4 mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M10 19l-7-7m0 0l7-7m-7 7h18"
              ></path>
            </svg>
            Back to Movies
          </Link>
        </div>
      </div>
    </div>
  );
};

export default MovieDetail;
