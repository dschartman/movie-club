import React from 'react';
import { Movie } from '../types/movie';

interface Genre {
  id: number;
  name: string;
  count: number;
}

interface GenreFilterProps {
  availableMovies: Movie[];
  filteredMovies: Movie[];
  selectedGenres: number[];
  onGenreToggle: (genreId: number) => void;
  onClearFilters: () => void;
}

const GenreFilter: React.FC<GenreFilterProps> = ({ 
  availableMovies,
  filteredMovies, 
  selectedGenres, 
  onGenreToggle,
  onClearFilters
}) => {
  // Extract all unique genres from the movies
  const allGenres: Genre[] = React.useMemo(() => {
    const genreMap = new Map<number, Genre>();
    
    // First pass: count all genres from available movies
    availableMovies.forEach(movie => {
      if (movie.genres) {
        movie.genres.forEach(genre => {
          if (!genreMap.has(genre.id)) {
            genreMap.set(genre.id, { ...genre, count: 1 });
          } else {
            const existingGenre = genreMap.get(genre.id)!;
            genreMap.set(genre.id, { ...existingGenre, count: existingGenre.count + 1 });
          }
        });
      }
    });
    
    // Create a set of genre IDs that exist in the filtered movies
    const availableGenreIds = new Set<number>();
    filteredMovies.forEach(movie => {
      if (movie.genres) {
        movie.genres.forEach(genre => {
          availableGenreIds.add(genre.id);
        });
      }
    });

    // Only return genres that exist in the filtered movies or are already selected
    return Array.from(genreMap.values())
      .filter(genre => availableGenreIds.has(genre.id) || selectedGenres.includes(genre.id))
      .sort((a, b) => a.name.localeCompare(b.name));
  }, [availableMovies, filteredMovies, selectedGenres]);

  return (
    <div className="mb-6">
      <div className="flex justify-between items-center mb-2">
        <h3 className="text-lg font-semibold">Filter by Genre</h3>
        {selectedGenres.length > 0 && (
          <button 
            onClick={onClearFilters}
            className="text-blue-600 hover:text-blue-800 text-sm"
          >
            Clear all filters
          </button>
        )}
      </div>
      <div className="flex flex-wrap gap-2">
        {allGenres.map(genre => (
          <button
            key={genre.id}
            onClick={() => onGenreToggle(genre.id)}
            className={`px-3 py-1 rounded-full text-sm flex items-center ${
              selectedGenres.includes(genre.id)
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 hover:bg-gray-300 text-gray-800'
            }`}
          >
            {genre.name} ({genre.count})
            {selectedGenres.includes(genre.id) && (
              <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            )}
          </button>
        ))}
      </div>
    </div>
  );
};

export default GenreFilter;
