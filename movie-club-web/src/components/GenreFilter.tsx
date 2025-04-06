import React from 'react';
import { Movie } from '../types/movie';

interface Genre {
  id: number;
  name: string;
  count: number;
}

interface GenreFilterProps {
  movies: Movie[];
  selectedGenres: number[];
  onGenreToggle: (genreId: number) => void;
  onClearFilters: () => void;
}

const GenreFilter: React.FC<GenreFilterProps> = ({ 
  movies, 
  selectedGenres, 
  onGenreToggle,
  onClearFilters
}) => {
  // Extract all unique genres from the movies
  const allGenres: Genre[] = React.useMemo(() => {
    const genreMap = new Map<number, Genre>();
    
    movies.forEach(movie => {
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
    
    return Array.from(genreMap.values())
      .sort((a, b) => a.name.localeCompare(b.name));
  }, [movies]);

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
