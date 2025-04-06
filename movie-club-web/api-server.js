const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3001;

// Sample movie data - in production, this would come from a database
let moviesData = {};

// Load movie data from individual JSON files in the data directory
try {
  const dataDir = path.join(__dirname, '../data');
  
  if (fs.existsSync(dataDir)) {
    const files = fs.readdirSync(dataDir);
    const jsonFiles = files.filter(file => file.endsWith('.json'));
    
    for (const file of jsonFiles) {
      try {
        const filePath = path.join(dataDir, file);
        const rawData = fs.readFileSync(filePath, 'utf8');
        const movieData = JSON.parse(rawData);
        
        // Extract movie ID from filename (e.g., "123.json" -> "123")
        const movieId = path.basename(file, '.json');
        
        // Store movie by ID
        if (movieData && movieData.id) {
          moviesData[movieId] = movieData;
        }
      } catch (fileErr) {
        console.error(`Error loading movie from ${file}:`, fileErr);
      }
    }
    
    console.log(`Loaded ${Object.keys(moviesData).length} movies from data directory`);
  } else {
    console.log("Data directory not found, using sample data");
    // Use sample data
    moviesData = {
      "1": {
        "id": 1,
        "title": "The Shawshank Redemption",
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
      }
    };
  }
} catch (err) {
  console.error("Error loading movie data:", err);
  moviesData = {};
}

// Middleware
app.use(cors());
app.use(express.json());

// Function to reload all movie data
const reloadMovieData = () => {
  try {
    const dataDir = path.join(__dirname, '../data');
    moviesData = {}; // Clear existing data
    
    if (fs.existsSync(dataDir)) {
      const files = fs.readdirSync(dataDir);
      const jsonFiles = files.filter(file => file.endsWith('.json'));
      
      for (const file of jsonFiles) {
        try {
          const filePath = path.join(dataDir, file);
          const rawData = fs.readFileSync(filePath, 'utf8');
          const movieData = JSON.parse(rawData);
          
          // Extract movie ID from filename
          const movieId = path.basename(file, '.json');
          
          if (movieData && movieData.id) {
            moviesData[movieId] = movieData;
          }
        } catch (fileErr) {
          console.error(`Error loading movie from ${file}:`, fileErr);
        }
      }
      
      console.log(`Reloaded ${Object.keys(moviesData).length} movies from data directory`);
      return true;
    }
    return false;
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
app.post('/api/reload', (req, res) => {
  const success = reloadMovieData();
  if (success) {
    res.json({ success: true, message: `Reloaded ${Object.keys(moviesData).length} movies` });
  } else {
    res.status(500).json({ success: false, message: "Failed to reload movie data" });
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
app.post('/api/movies', (req, res) => {
  const movie = req.body;
  if (!movie || !movie.id) {
    return res.status(400).json({ error: 'Invalid movie data' });
  }
  
  moviesData[movie.id] = movie;
  res.status(201).json(movie);
});

// Start the server
app.listen(PORT, () => {
  console.log(`API server running on port ${PORT}`);
});
