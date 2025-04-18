const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3001;

// Sample movie data - in production, this would come from a database
let moviesData = {};
let isConnectedToApi = false;
let connectionAttempts = 0;
const MAX_RETRY_ATTEMPTS = 10;

// Get movie data from the movie API
const fetchMoviesFromAPI = async () => {
  try {
    // Default URL for Docker environments uses the service name defined in docker-compose
    // For local development outside Docker, set MOVIE_API_URL environment variable
    const movieApiUrl = process.env.MOVIE_API_URL || "http://movie-api:8000";
    console.log(`Fetching movies from API: ${movieApiUrl}/movies`);
    
    const response = await fetch(`${movieApiUrl}/movies`, {
      // Adding a timeout to prevent long-hanging requests
      signal: AbortSignal.timeout(10000) // 10 second timeout
    });
    
    if (!response.ok) {
      throw new Error(`API responded with status: ${response.status}`);
    }
    
    const data = await response.json();
    console.log(`Loaded ${Object.keys(data).length} movies from API`);
    
    if (Object.keys(data).length === 0) {
      throw new Error("API returned an empty movie collection");
    }
    
    isConnectedToApi = true;
    connectionAttempts = 0;
    return data;
  } catch (err) {
    isConnectedToApi = false;
    connectionAttempts++;
    console.error(`Error fetching movie data from API (attempt ${connectionAttempts}/${MAX_RETRY_ATTEMPTS}):`, err);
    
    // If we already have movie data, keep using it instead of falling back to sample data
    if (Object.keys(moviesData).length > 0) {
      console.log("Using existing movie data as fallback");
      return moviesData;
    }
    
    console.log("Using sample movie data as fallback");
    // Use sample data as fallback - adding a few more movies to make it obvious this is sample data
    return {
      "1": {
        "id": 1,
        "title": "The Shawshank Redemption (SAMPLE DATA)",
        "original_title": "The Shawshank Redemption",
        "overview": "Framed in the 1940s for the double murder of his wife and her lover, upstanding banker Andy Dufresne begins a new life at the Shawshank prison, where he puts his accounting skills to work for an amoral warden. During his long stretch in prison, Dufresne comes to be admired by the other inmates -- including an older prisoner named Red -- for his integrity and unquenchable sense of hope.",
        "release_date": "1994-09-23",
        "poster_path": "/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg",
        "backdrop_path": "/kXfqcdQKsToO0OUXHcrrNCHDBzO.jpg",
        "popularity": 95.95,
        "vote_average": 8.7,
        "vote_count": 23825,
        "genres": [
          {
            "id": 18,
            "name": "Drama"
          },
          {
            "id": 80,
            "name": "Crime"
          }
        ],
        "runtime": 142
      },
      "2": {
        "id": 2,
        "title": "The Godfather (SAMPLE DATA)",
        "original_title": "The Godfather",
        "overview": "Spanning the years 1945 to 1955, a chronicle of the fictional Italian-American Corleone crime family. When organized crime family patriarch, Vito Corleone barely survives an attempt on his life, his youngest son, Michael steps in to take care of the would-be killers, launching a campaign of bloody revenge.",
        "release_date": "1972-03-14",
        "poster_path": "/3bhkrj58Vtu7enYsRolD1fZdja1.jpg",
        "backdrop_path": "/rSPw7tgCH9c6NqICZef4kZjFOQ5.jpg",
        "popularity": 76.942,
        "vote_average": 8.7,
        "vote_count": 17005,
        "genres": [
          {
            "id": 18,
            "name": "Drama"
          },
          {
            "id": 80,
            "name": "Crime"
          }
        ],
        "runtime": 175
      }
    };
  }
};

// Function to retry connecting to the API with exponential backoff
const setupApiConnection = async () => {
  try {
    const data = await fetchMoviesFromAPI();
    moviesData = data;
    
    if (!isConnectedToApi && connectionAttempts < MAX_RETRY_ATTEMPTS) {
      // Calculate backoff time (exponential with jitter)
      const baseDelay = Math.min(1000 * Math.pow(2, connectionAttempts), 30000);
      const jitter = Math.random() * 1000;
      const delay = baseDelay + jitter;
      
      console.log(`Will retry connecting to Movie API in ${Math.round(delay/1000)} seconds...`);
      
      setTimeout(setupApiConnection, delay);
    } else if (connectionAttempts >= MAX_RETRY_ATTEMPTS && !isConnectedToApi) {
      console.log(`Reached maximum retry attempts (${MAX_RETRY_ATTEMPTS}). Will stop trying to connect.`);
      // Set up a manual retry every 5 minutes
      setTimeout(setupApiConnection, 5 * 60 * 1000);
    }
  } catch (err) {
    console.error("Unexpected error in setupApiConnection:", err);
  }
};

// Initialize connection to API
setupApiConnection();

// Middleware
app.use(cors());
app.use(express.json());

// Function to reload all movie data from API
const reloadMovieData = async () => {
  try {
    const data = await fetchMoviesFromAPI();
    moviesData = data;
    console.log(`Reloaded ${Object.keys(moviesData).length} movies from API`);
    return true;
  } catch (err) {
    console.error("Error reloading movie data:", err);
    return false;
  }
};

// Routes
app.get('/api/movies', (req, res) => {
  res.json(moviesData);
});

// Endpoint to refresh movie data
app.post('/api/reload', async (req, res) => {
  try {
    const success = await reloadMovieData();
    if (success) {
      res.json({ success: true, message: `Reloaded ${Object.keys(moviesData).length} movies` });
    } else {
      res.status(500).json({ success: false, message: "Failed to reload movie data" });
    }
  } catch (error) {
    res.status(500).json({ success: false, message: `Error: ${error.message}` });
  }
});

app.get('/api/movies/:id', (req, res) => {
  const movieId = req.params.id;
  const movie = moviesData[movieId];
  
  if (movie) {
    res.json(movie);
  } else {
    res.status(404).json({ error: 'Movie not found' });
  }
});

// Add a new movie
app.post('/api/movies', async (req, res) => {
  const movie = req.body;
  if (!movie || !movie.id) {
    return res.status(400).json({ error: 'Invalid movie data' });
  }
  
  try {
    const movieApiUrl = process.env.MOVIE_API_URL || "http://movie-api:8000";
    const response = await fetch(`${movieApiUrl}/movies`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(movie)
    });
    
    if (!response.ok) {
      throw new Error(`API responded with status: ${response.status}`);
    }
    
    const addedMovie = await response.json();
    // Update local cache
    moviesData[movie.id] = addedMovie;
    res.status(201).json(addedMovie);
  } catch (error) {
    console.error('Error adding movie to API:', error);
    // Fall back to local operation if API is unavailable
    moviesData[movie.id] = movie;
    res.status(201).json(movie);
  }
});

// Add health check endpoint
app.get('/api/health', (req, res) => {
  res.json({
    status: 'ok',
    connectedToMovieApi: isConnectedToApi,
    moviesCount: Object.keys(moviesData).length,
    connectionAttempts
  });
});

// Start the server
app.listen(PORT, () => {
  console.log(`API server running on port ${PORT}`);
  console.log(`Expected Movie API URL: ${process.env.MOVIE_API_URL || "http://movie-api:8000"}`);
  console.log(`If you're not seeing all movies, check that the Movie API is running and accessible`);
  console.log(`You may need to set the MOVIE_API_URL environment variable to point to your Python API`);
  console.log(`The server will automatically retry connecting to the Movie API if it's not available`);

  // We're already attempting to connect via setupApiConnection so we don't need the explicit reload here
});
