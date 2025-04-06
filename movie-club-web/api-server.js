const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3001;

// Sample movie data - in production, this would come from a database
let moviesData = {};

// Try to load movie data from a JSON file if it exists
try {
  const dataPath = path.join(__dirname, 'movie-data.json');
  if (fs.existsSync(dataPath)) {
    const rawData = fs.readFileSync(dataPath, 'utf8');
    moviesData = JSON.parse(rawData);
    console.log(`Loaded ${Object.keys(moviesData).length} movies from file`);
  } else {
    // Sample data if no file exists
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
      },
      "2": {
        "id": 2,
        "title": "The Godfather",
        "original_title": "The Godfather",
        "overview": "Spanning the years 1945 to 1955, a chronicle of the fictional Italian-American Corleone crime family. When organized crime family patriarch, Vito Corleone barely survives an attempt on his life, his youngest son, Michael steps in to take care of the would-be killers, launching a campaign of bloody revenge.",
        "release_date": "1972-03-14",
        "poster_path": "/3bhkrj58Vtu7enYsRolD1fZdja1.jpg",
        "backdrop_path": "/tmU7GeKVybMWFButWEGl2M4GeiP.jpg",
        "popularity": 86.273,
        "vote_average": 8.7,
        "vote_count": 17845,
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
      },
      "3": {
        "id": 3,
        "title": "Pulp Fiction",
        "original_title": "Pulp Fiction",
        "overview": "A burger-loving hit man, his philosophical partner, a drug-addled gangster's moll and a washed-up boxer converge in this sprawling, comedic crime caper. Their adventures unfurl in three stories that ingeniously trip back and forth in time.",
        "release_date": "1994-09-10",
        "poster_path": "/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg",
        "backdrop_path": "/suaEOtk1N1sgg2MTM7oZd2cfVp3.jpg",
        "popularity": 85.826,
        "vote_average": 8.5,
        "vote_count": 25005,
        "genres": [
          {
            "id": 53,
            "name": "Thriller"
          },
          {
            "id": 80,
            "name": "Crime"
          }
        ],
        "runtime": 154
      }
    };
    console.log("Using sample movie data");
  }
} catch (err) {
  console.error("Error loading movie data:", err);
  moviesData = {};
}

// Middleware
app.use(cors());
app.use(express.json());

// Routes
app.get('/api/movies', (req, res) => {
  res.json(moviesData);
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
