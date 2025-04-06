const express = require('express');
const fs = require('fs');
const path = require('path');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

// Serve static files from the React app
app.use(express.static(path.join(__dirname, 'movie-club-web/build')));

// API endpoint to get all movies
app.get('/api/movies', (req, res) => {
  const dataDir = path.join(__dirname, 'data');
  const movieFiles = fs.readdirSync(dataDir)
    .filter(file => file.match(/^\d+\.json$/));
  
  const movies = {};
  
  movieFiles.forEach(file => {
    const fileContent = fs.readFileSync(path.join(dataDir, file), 'utf8');
    try {
      const movieData = JSON.parse(fileContent);
      const movieId = path.basename(file, '.json');
      movies[movieId] = movieData;
    } catch (err) {
      console.error(`Error parsing ${file}:`, err);
    }
  });
  
  res.json(movies);
});

// The "catchall" handler: for any request that doesn't
// match one above, send back React's index.html file.
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'movie-club-web/build/index.html'));
});

app.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}`);
});
