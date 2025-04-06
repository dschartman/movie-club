import React, { useEffect, useState } from 'react';
import { Routes, Route } from 'react-router-dom';
import { Movie, MovieCollection } from './types/movie';
import MovieGrid from './components/MovieGrid';
import MovieDetail from './components/MovieDetail';
import GenreFilter from './components/GenreFilter';
import RandomMoviePicker from './components/RandomMoviePicker';
import { fetchAllMovies } from './services/movieService';

function App() {
  const [movies, setMovies] = useState<MovieCollection>({});
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedGenres, setSelectedGenres] = useState<number[]>([]);

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

  const toggleGenre = (genreId: number) => {
    setSelectedGenres(prev => 
      prev.includes(genreId) 
        ? prev.filter(id => id !== genreId) 
        : [...prev, genreId]
    );
  };

  const clearFilters = () => {
    setSelectedGenres([]);
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  const allMovies = Object.values(movies);
  
  // Filter movies based on selected genres (movie must contain ANY of the selected genres)
  const filteredMovies = selectedGenres.length > 0
    ? allMovies.filter(movie => 
        movie.genres?.some(genre => selectedGenres.includes(genre.id))
      )
    : allMovies;

  return (
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
            <Route path="/" element={
              <div className="container mx-auto px-4 py-8">
                <div className="flex flex-col md:flex-row md:justify-between md:items-start gap-4">
                  <GenreFilter 
                    availableMovies={allMovies}
                    filteredMovies={filteredMovies}
                    selectedGenres={selectedGenres}
                    onGenreToggle={toggleGenre}
                    onClearFilters={clearFilters}
                  />
                  <RandomMoviePicker movies={filteredMovies} />
                </div>
                <MovieGrid 
                  movies={filteredMovies} 
                  title={`Movies${selectedGenres.length > 0 ? ' (Filtered)' : ''}`} 
                />
              </div>
            } />
            <Route path="/movie/:id" element={<MovieDetail />} />
          </Routes>
        </main>
      </div>
  );
}

export default App;
