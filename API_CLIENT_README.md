# MovieAPIClient Implementation Summary

## Overview
Implemented a complete `MovieAPIClient` class in `utils/api_client.py` that fetches movie data from the OMDb API and stores it in the SQLite `api_movies` table.

## Features

### `MovieAPIClient` Class
- **API**: OMDb API (Open Movie Database) - https://www.omdbapi.com/
- **Extracted Fields**:
  - `title`: Movie title
  - `genre`: Comma-separated genres
  - `plot`: Full plot description
  - `poster_url`: URL to movie poster image

### Methods

#### `fetch_movie(title, year=None, plot="full")`
- Fetches a single movie by title
- **Optional**: Filter by release year
- **Returns**: Movie dict or None
- **Fallback**: Returns sample data if OMDb API unavailable

#### `search_movies(query, year=None, plot="full")`
- Searches for movies matching query
- **Returns**: List of up to 5 matching movie dicts
- **Fallback**: Searches sample data if API unavailable

#### `fetch_and_save_multiple(movie_list)`
- Fetches multiple movies by title
- Automatically saves to database
- **Returns**: Number of movies inserted

#### `fetch_popular_movies()`
- Fetches 10 curated popular movies
- Includes: Inception, The Matrix, Forrest Gump, Pulp Fiction, Fight Club, Goodfellas, The Shawshank Redemption, The Godfather, Titanic, Avatar
- **Returns**: Number of movies inserted

#### `save_to_db(movies)`
- Saves movies to `api_movies` SQLite table
- Clears table before inserting new data
- **Returns**: Number of movies inserted

### Database Integration
- Connects to `db/movies.db`
- Clears the `api_movies` table before inserting new data
- Schema:
  ```sql
  CREATE TABLE api_movies (
      id INTEGER PRIMARY KEY,
      title TEXT,
      genre TEXT,
      plot TEXT,
      poster_url TEXT
  );
  ```

## Implementation Details

### OMDb API Integration
- **API Endpoint**: https://www.omdbapi.com/
- **Authentication**: API key required (free tier available)
- **Search Parameters**:
  - `t`: Exact title match (returns single movie)
  - `s`: Search query (returns up to 10 results)
  - `y`: Year filter (optional)
  - `plot`: "short" or "full"

### Fallback Strategy
The client gracefully falls back to sample data when:
- OMDb API key is invalid or missing (HTTP 401)
- Network request fails
- API returns no results for query

### Sample Data (Fallback)
10 well-known movies with real genre and plot information:
- Inception
- The Matrix
- Forrest Gump
- Pulp Fiction
- Fight Club
- Goodfellas
- The Shawshank Redemption
- The Godfather
- Titanic
- Avatar

Plus additional movies for search:
- Batman Begins
- The Dark Knight

## Getting Your Own API Key

To use live OMDb API data:

1. **Visit**: https://www.omdbapi.com/apikey.aspx
2. **Register**: Create a free account
3. **Copy API Key**: You'll receive a key via email
4. **Update Code**: Pass your key when initializing:
   ```python
   from utils.api_client import MovieAPIClient
   
   client = MovieAPIClient(api_key="your_actual_key_here")
   movies = client.fetch_popular_movies()
   ```

## Testing

### Test Script: `test_api_client.py`
Comprehensive test suite:
1. **Test 1**: Fetch single movie (Inception)
2. **Test 2**: Search for movies (Batman query)
3. **Test 3**: Fetch and save popular movies
4. **Test 4**: Verify data in database

**Sample Output**:
```
Total movies in api_movies table: 10

1. Inception
   Genre: Action, Sci-Fi, Thriller
   Plot: A skilled thief who steals corporate secrets...
   Poster: https://upload.wikimedia.org/...

2. The Matrix
   Genre: Action, Sci-Fi
   Plot: A computer hacker learns from mysterious rebels...
   Poster: https://upload.wikimedia.org/...
```

### To Run Tests
```bash
python test_api_client.py
```

## Requirements

### Python Packages (already installed)
- `requests` — HTTP requests to OMDb API

### Database
- SQLite 3 (standard library in Python)
- Database file: `db/movies.db`

## Usage Examples

### Fetch and display a single movie
```python
from utils.api_client import MovieAPIClient

client = MovieAPIClient()
movie = client.fetch_movie("Inception", year=2010)

if movie:
    print(f"Title: {movie['title']}")
    print(f"Genre: {movie['genre']}")
    print(f"Plot: {movie['plot']}")
    print(f"Poster: {movie['poster_url']}")
```

### Fetch and save multiple movies
```python
movies_to_fetch = ["The Matrix", "Fight Club", "Avatar"]
inserted = client.fetch_and_save_multiple(movies_to_fetch)
print(f"Inserted {inserted} movies into database")
```

### Fetch popular movies
```python
inserted = client.fetch_popular_movies()
print(f"Populated api_movies table with {inserted} movies")
```

### Search for movies
```python
results = client.search_movies("Batman")
for movie in results:
    print(f"{movie['title']} - {movie['genre']}")
```

## Integration with Flask App
The `api_movies` table is displayed on the Flask app's **API Movies** page. After running any of the fetch methods, refresh your browser to see updated data.

Quick command to populate the table:
```bash
python -c "from utils.api_client import MovieAPIClient; MovieAPIClient().fetch_popular_movies()"
```

Or use the test script:
```bash
python test_api_client.py
```

## Notes

### API Rate Limiting
- **Free Tier**: Approximately 1,000 requests per day
- **Paid Plans**: Higher limits available
- **Recommendations**: 
  - Cache results when possible
  - Limit API calls in production
  - Use fallback data during development

### Error Handling
All methods include robust error handling:
- Network timeouts (10 second default)
- Invalid API keys
- Missing movies
- Malformed responses

### Logging
All operations logged at appropriate levels (INFO, WARNING, ERROR) via Python's `logging` module for debugging and monitoring.

## Architecture

```
MovieAPIClient (utils/api_client.py)
├── fetch_movie()              # Single movie by title
├── search_movies()            # Search multiple results
├── fetch_and_save_multiple()  # Batch fetch and save
├── fetch_popular_movies()     # Pre-curated popular list
├── save_to_db()               # Store to SQLite
├── _fetch_movie_by_id()       # OMDb internal (IMDb ID lookup)
├── _parse_movie_data()        # Response parsing
├── _get_sample_movie()        # Fallback data
└── _search_sample_movies()    # Fallback search

Database: api_movies table in db/movies.db
├── id (INTEGER PRIMARY KEY)
├── title (TEXT)
├── genre (TEXT)
├── plot (TEXT)
└── poster_url (TEXT)
```
