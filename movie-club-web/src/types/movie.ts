export interface Movie {
  id: number;
  title: string;
  original_title: string;
  overview: string;
  release_date: string;
  poster_path: string | null;
  backdrop_path: string | null;
  popularity: number;
  vote_average: number;
  vote_count: number;
  genres: Array<{
    id: number;
    name: string;
  }>;
  runtime: number | null;
}

export interface MovieCollection {
  [id: string]: Movie;
}
