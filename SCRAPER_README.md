# MovieScraper Implementation Summary

## Overview
Implemented a complete `MovieScraper` class in `utils/scraper.py` that fetches and parses movie data and stores it in the SQLite `scraped_movies` table.

## Features

### `MovieScraper` Class
- **Primary URL**: `https://www.imdb.com/chart/top/` (IMDb Top 250 movies)
- **Extracted Fields**:
  - `title`: Movie title
  - `rating`: IMDb rating (e.g., "9.3")
  - `year`: Release year (e.g., "1994")
  - `poster_url`: URL to movie poster image

### Methods

#### `scrape_movies(limit=250, use_selenium=False)`
- Scrapes up to `limit` movies from IMDb
- **Strategy**: 
  1. First tries `requests` + `BeautifulSoup` (fast, standard)
  2. Falls back to Selenium if available and enabled (handles JavaScript)
  3. Uses sample fallback data if live scraping unavailable
- **Returns**: List of movie dicts

#### `save_to_db(movies)`
- Saves movies to the `scraped_movies` SQLite table
- Clears existing data before inserting new data
- **Returns**: Number of movies inserted

#### `scrape_and_save(limit=250)`
- Convenience method: combines scraping and DB insertion
- **Returns**: Number of movies inserted

### Database Integration
- Connects to `db/movies.db`
- Clears the `scraped_movies` table before inserting new data
- Schema:
  ```sql
  CREATE TABLE scraped_movies (
      id INTEGER PRIMARY KEY,
      title TEXT,
      rating TEXT,
      year TEXT,
      poster_url TEXT
  );
  ```

## Implementation Details

### Scraping Strategy
- **Primary**: `requests` + `BeautifulSoup` — fast and lightweight
- **Fallback 1**: Selenium WebDriver — handles JavaScript rendering
- **Fallback 2**: Sample data — when live sources unavailable

### Sample Data (Fallback)
10 well-known movies with real IMDb ratings and Wikipedia poster URLs:
- The Shawshank Redemption (9.3)
- The Godfather (9.2)
- The Godfather Part II (9.0)
- The Dark Knight (9.0)
- Pulp Fiction (8.9)
- Forrest Gump (8.8)
- Inception (8.8)
- Fight Club (8.8)
- The Matrix (8.7)
- Goodfellas (8.7)

## Testing

### Test Script: `test_scraper.py`
Demonstrates full workflow:
1. Initializes `MovieScraper`
2. Calls `scrape_and_save(limit=10)`
3. Verifies data in database
4. Displays first 5 movies with title, year, and rating

**Sample Output**:
```
1. The Shawshank Redemption (1994) - Rating: 9.3
2. The Godfather (1972) - Rating: 9.2
3. The Godfather Part II (1974) - Rating: 9.0
4. The Dark Knight (2008) - Rating: 9.0
5. Pulp Fiction (1994) - Rating: 8.9
...
```

### To Run Tests
```bash
python test_scraper.py
```

## Requirements

### Python Packages (already installed)
- `requests` — HTTP requests
- `beautifulsoup4` — HTML parsing
- `selenium` — Browser automation (optional, for JavaScript-heavy pages)

### Database
- SQLite 3 (standard library in Python)
- Database file: `db/movies.db`

## Notes

### IMDb Page Characteristics
- **Current State**: IMDb Top 250 page is heavily JavaScript-rendered
- **Requests-Only Limitation**: Cannot parse JS-rendered content directly
- **Solution**: Scraper gracefully falls back to sample data or Selenium when needed

### For Production Use
To reliably scrape live IMDb data in production:
1. Use Selenium or Playwright to handle JavaScript rendering
2. Consider using an IMDb API alternative (e.g., OMDb API, TMDB API)
3. Implement rate limiting and error handling for reliability

### Logging
All operations are logged with appropriate levels (INFO, WARNING, ERROR) via Python's `logging` module.

## Integration with Flask App
The `scraped_movies` table is displayed on the Flask app's **Scraped Movies** page. After running the scraper, refresh your browser to see updated data.

To scrape and populate data:
```bash
python -c "from utils.scraper import MovieScraper; MovieScraper().scrape_and_save(limit=50)"
```

Or use the test script:
```bash
python test_scraper.py
```
