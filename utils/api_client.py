import requests
import sqlite3
import logging
from pathlib import Path
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)


class MovieAPIClient:
    """
    Client for fetching movie data from OMDb API and storing it in SQLite.
    
    OMDb API (Open Movie Database) provides movie information including:
    - Title, Genre, Plot, and Poster URL
    
    Free tier available at: https://www.omdbapi.com/
    Register for a free API key to get started.
    """

    def __init__(self, api_key: str = "e5c96a17", db_path: str = "db/movies.db"):
        """
        Initialize the MovieAPIClient.
        
        Args:
            api_key: OMDb API key (default is a demo key with limited requests)
                    For production, get your own free key from https://www.omdbapi.com/apikey.aspx
            db_path: Path to SQLite database
        """
        self.api_key = api_key
        self.db_path = db_path
        self.base_url = "https://www.omdbapi.com/"
        self.timeout = 10

    def search_movies(self, query: str, year: Optional[int] = None, plot: str = "full") -> List[Dict]:
        """
        Search for movies by title using OMDb API.
        Falls back to sample data if API key is invalid.
        
        Args:
            query: Movie title or search query
            year: Optional release year to filter results
            plot: "short" or "full" (default "full" for more detail)
        
        Returns:
            List of movie dicts with keys: title, genre, plot, poster_url
        """
        movies = []
        
        params = {
            "apikey": self.api_key,
            "s": query,  # Search parameter
            "type": "movie",
            "plot": plot
        }
        
        if year:
            params["y"] = year
        
        try:
            logger.info(f"Searching OMDb API for: {query}")
            response = requests.get(self.base_url, params=params, timeout=self.timeout)
            
            # Check for 401 Unauthorized
            if response.status_code == 401:
                logger.warning("Invalid OMDb API key. Using sample data for search.")
                return self._search_sample_movies(query)
            
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("Response") == "True" and "Search" in data:
                search_results = data["Search"]
                logger.info(f"Found {len(search_results)} search results for '{query}'")
                
                # For each search result, fetch full details using IMDb ID
                for result in search_results[:5]:  # Limit to 5 to avoid excessive API calls
                    if result.get("Type") == "movie":
                        movie = self._fetch_movie_by_id(result.get("imdbID"))
                        if movie:
                            movies.append(movie)
            else:
                logger.warning(f"No results found for '{query}': {data.get('Error', 'Unknown error')}")
                return self._search_sample_movies(query)
        
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            logger.info("Using sample data...")
            return self._search_sample_movies(query)
        except Exception as e:
            logger.error(f"Error searching movies: {e}")
            return self._search_sample_movies(query)
        
        return movies

    def _fetch_movie_by_id(self, imdb_id: str, plot: str = "full") -> Optional[Dict]:
        """
        Fetch detailed movie information by IMDb ID.
        
        Args:
            imdb_id: IMDb ID (e.g., "tt1375666" for Inception)
            plot: "short" or "full" (default "full")
        
        Returns:
            Dict with keys: title, genre, plot, poster_url
        """
        params = {
            "apikey": self.api_key,
            "i": imdb_id,
            "plot": plot,
            "type": "movie"
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            if data.get("Response") == "True":
                movie = self._parse_movie_data(data)
                logger.debug(f"Fetched: {movie.get('title', 'Unknown')}")
                return movie
            else:
                logger.warning(f"Movie not found (ID: {imdb_id}): {data.get('Error', 'Unknown error')}")
        
        except Exception as e:
            logger.error(f"Error fetching movie {imdb_id}: {e}")
        
        return None

    def fetch_movie(self, title: str, year: Optional[int] = None, plot: str = "full") -> Optional[Dict]:
        """
        Fetch a single movie by title (most specific match from OMDb).
        Falls back to sample data if API key is invalid or request fails.
        
        Args:
            title: Movie title
            year: Optional release year
            plot: "short" or "full"
        
        Returns:
            Dict with keys: title, genre, plot, poster_url, or None if not found
        """
        params = {
            "apikey": self.api_key,
            "t": title,  # Title parameter (searches for exact/close match)
            "type": "movie",
            "plot": plot
        }
        
        if year:
            params["y"] = year
        
        try:
            logger.info(f"Fetching movie: {title}" + (f" ({year})" if year else ""))
            response = requests.get(self.base_url, params=params, timeout=self.timeout)
            
            # Check for 401 Unauthorized (invalid API key)
            if response.status_code == 401:
                logger.warning("Invalid OMDb API key. Falling back to sample data.")
                logger.info("To use live OMDb API:")
                logger.info("  1. Visit https://www.omdbapi.com/apikey.aspx")
                logger.info("  2. Register for a free API key")
                logger.info("  3. Update the api_key parameter in MovieAPIClient()")
                return self._get_sample_movie(title)
            
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("Response") == "True":
                movie = self._parse_movie_data(data)
                logger.info(f"Successfully fetched: {movie.get('title', 'Unknown')}")
                return movie
            else:
                logger.warning(f"Movie not found: {title} - {data.get('Error', 'Unknown error')}")
                return self._get_sample_movie(title)
        
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            logger.info("Using sample movie data...")
            return self._get_sample_movie(title)
        except Exception as e:
            logger.error(f"Error fetching movie: {e}")
            return self._get_sample_movie(title)

    def _parse_movie_data(self, data: Dict) -> Dict:
        """
        Parse OMDb API response into our standard movie format.
        
        Args:
            data: Response dict from OMDb API
        
        Returns:
            Dict with keys: title, genre, plot, poster_url
        """
        return {
            "title": data.get("Title", ""),
            "genre": data.get("Genre", ""),
            "plot": data.get("Plot", ""),
            "poster_url": data.get("Poster", "")
        }

    def _get_sample_movie(self, title: str) -> Optional[Dict]:
        """
        Return sample movie data for a given title.
        Used as fallback when OMDb API is unavailable or API key is invalid.
        
        Args:
            title: Movie title to search for in sample data
        
        Returns:
            Sample movie dict or None if title not found
        """
        sample_movies = {
            "Inception": {
                "title": "Inception",
                "genre": "Action, Sci-Fi, Thriller",
                "plot": "A skilled thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.",
                "poster_url": "https://upload.wikimedia.org/wikipedia/en/2/2e/Inception_%282010%29_theatrical_poster.jpg"
            },
            "The Matrix": {
                "title": "The Matrix",
                "genre": "Action, Sci-Fi",
                "plot": "A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.",
                "poster_url": "https://upload.wikimedia.org/wikipedia/en/c/c1/The_Matrix_Poster.jpg"
            },
            "Forrest Gump": {
                "title": "Forrest Gump",
                "genre": "Drama, Romance",
                "plot": "The presidencies of Kennedy and Johnson, the Vietnam War, the Watergate scandal and other historical events unfold from the perspective of an Alabama man with an IQ of 75.",
                "poster_url": "https://upload.wikimedia.org/wikipedia/en/6/67/Forrest_Gump_poster.jpg"
            },
            "Pulp Fiction": {
                "title": "Pulp Fiction",
                "genre": "Crime, Drama",
                "plot": "The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption.",
                "poster_url": "https://upload.wikimedia.org/wikipedia/en/8/8b/Pulp_Fiction_%282.jpg"
            },
            "Fight Club": {
                "title": "Fight Club",
                "genre": "Drama",
                "plot": "An insomniac office worker and a devil-may-care soapmaker form an underground fight club that evolves into much more.",
                "poster_url": "https://upload.wikimedia.org/wikipedia/en/f/fc/Fight_Club_poster.jpg"
            },
            "Goodfellas": {
                "title": "Goodfellas",
                "genre": "Crime, Drama",
                "plot": "The story of Henry Hill and his life in the mafia, covering his relationship with his wife Karen Hill and his mob partners, Tommy DeVito and Jimmy Conway.",
                "poster_url": "https://upload.wikimedia.org/wikipedia/en/0/0b/Goodfellas.jpg"
            },
            "The Shawshank Redemption": {
                "title": "The Shawshank Redemption",
                "genre": "Drama",
                "plot": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
                "poster_url": "https://upload.wikimedia.org/wikipedia/en/8/81/ShawshankRedemptionMoviePoster.jpg"
            },
            "The Godfather": {
                "title": "The Godfather",
                "genre": "Crime, Drama",
                "plot": "The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his youngest and most reluctant son.",
                "poster_url": "https://upload.wikimedia.org/wikipedia/en/1/1c/Godfather_1972_poster.png"
            },
            "Titanic": {
                "title": "Titanic",
                "genre": "Drama, Romance",
                "plot": "A seventeen-year-old aristocrat falls in love with a kind but poor artist aboard the luxurious, ill-fated R.M.S. Titanic.",
                "poster_url": "https://upload.wikimedia.org/wikipedia/en/2/2f/Titanic_%281997%29_theatrical_poster.jpg"
            },
            "Avatar": {
                "title": "Avatar",
                "genre": "Action, Adventure, Fantasy, Sci-Fi",
                "plot": "A paraplegic Marine dispatched to the moon Pandora on a unique mission becomes torn between following his orders and protecting the world he feels is his home.",
                "poster_url": "https://upload.wikimedia.org/wikipedia/en/b/b0/Avatar_%282009%29_poster.jpg"
            }
        }
        
        # Search for the movie (case-insensitive)
        for key, movie in sample_movies.items():
            if key.lower() == title.lower():
                logger.debug(f"Using sample data for: {title}")
                return movie
        
        return None

    def save_to_db(self, movies: List[Dict]) -> int:
        """
        Save movies to the api_movies table.
        Clears the table before inserting new data.
        
        Args:
            movies: List of movie dicts with keys: title, genre, plot, poster_url
        
        Returns:
            Number of movies inserted
        """
        if not Path(self.db_path).exists():
            raise FileNotFoundError(f"Database file not found: {self.db_path}")
        
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Clear existing data
            c.execute("DELETE FROM api_movies")
            
            # Insert new data
            inserted = 0
            for movie in movies:
                try:
                    c.execute(
                        "INSERT INTO api_movies (title, genre, plot, poster_url) VALUES (?, ?, ?, ?)",
                        (
                            movie.get("title", ""),
                            movie.get("genre", ""),
                            movie.get("plot", ""),
                            movie.get("poster_url", "")
                        )
                    )
                    inserted += 1
                except Exception as e:
                    logger.warning(f"Error inserting movie {movie.get('title', 'Unknown')}: {e}")
            
            conn.commit()
            logger.info(f"Inserted {inserted} movies into api_movies table")
            return inserted
        
        except Exception as e:
            logger.error(f"Error saving to database: {e}")
            raise
        
        finally:
            conn.close()

    def fetch_and_save_multiple(self, movie_list: List[str]) -> int:
        """
        Fetch multiple movies by title and save to database.
        
        Args:
            movie_list: List of movie titles to fetch
        
        Returns:
            Number of movies inserted into database
        """
        movies = []
        
        logger.info(f"Fetching {len(movie_list)} movies from OMDb API...")
        
        for title in movie_list:
            movie = self.fetch_movie(title, plot="full")
            if movie and movie.get("title"):
                movies.append(movie)
        
        if movies:
            inserted = self.save_to_db(movies)
            return inserted
        else:
            logger.warning("No movies were fetched")
            return 0

    def fetch_popular_movies(self) -> int:
        """
        Fetch a curated list of popular/well-known movies and save to database.
        Uses hardcoded popular titles to avoid excessive API calls.
        Falls back to sample data if OMDb API is unavailable.
        
        Returns:
            Number of movies inserted into database
        """
        popular_titles = [
            "Inception",
            "The Matrix",
            "Forrest Gump",
            "Pulp Fiction",
            "Fight Club",
            "Goodfellas",
            "The Shawshank Redemption",
            "The Godfather",
            "Titanic",
            "Avatar"
        ]
        
        logger.info(f"Fetching {len(popular_titles)} popular movies from OMDb API...")
        return self.fetch_and_save_multiple(popular_titles)

    def _search_sample_movies(self, query: str) -> List[Dict]:
        """
        Search sample movie data for a given query.
        Performs case-insensitive substring matching.
        
        Args:
            query: Search query
        
        Returns:
            List of matching sample movies
        """
        sample_movies_list = [
            {
                "title": "Inception",
                "genre": "Action, Sci-Fi, Thriller",
                "plot": "A skilled thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.",
                "poster_url": "https://upload.wikimedia.org/wikipedia/en/2/2e/Inception_%282010%29_theatrical_poster.jpg"
            },
            {
                "title": "The Dark Knight",
                "genre": "Action, Crime, Drama",
                "plot": "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest tests.",
                "poster_url": "https://upload.wikimedia.org/wikipedia/en/1/1a/The_Dark_Knight_%282008_film%29.jpg"
            },
            {
                "title": "Batman Begins",
                "genre": "Action, Crime, Drama",
                "plot": "When a crime in Gotham is too serious for the Gotham City Police Department, Batman is called upon to solve the case.",
                "poster_url": "https://upload.wikimedia.org/wikipedia/en/1/1d/Batman_begins_poster.jpg"
            }
        ]
        
        query_lower = query.lower()
        results = [m for m in sample_movies_list if query_lower in m["title"].lower()]
        logger.info(f"Found {len(results)} sample movies matching '{query}'")
        return results