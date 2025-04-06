import React, { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Movie, MovieCollection } from './types/movie';
import MovieGrid from './components/MovieGrid';
import { fetchAllMovies } from './services/movieService';

function App() {
  const [movies, setMovies] = useState<MovieCollection>({});
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const loadMovies = async () => {
      try {
        const movieData = await fetchAllMovies();
        setMovies(movieData);
      } catch (error) {
        console.error('Failed to load movies:', error);
      } finally {
        setLoading(false);
      }
    };

    loadMovies();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  const movieList = Object.values(movies);

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-100">
        <header className="bg-gray-800 text-white shadow-md">
          <div className="container mx-auto px-4 py-4 flex items-center">
            <h1 className="text-2xl font-bold">
              <a href="/">Movie Club</a>
            </h1>
          </div>
        </header>

        <main>
          <Routes>
            <Route path="/" element={<MovieGrid movies={movieList} title="Your Movies" />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
