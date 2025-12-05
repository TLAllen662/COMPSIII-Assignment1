#!/usr/bin/env python3
"""
Test script for MovieAPIClient class.
Fetches movies from OMDb API and verifies data is stored in the database.
"""

import sqlite3
import logging
from utils.api_client import MovieAPIClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_single_movie():
    """Test fetching a single movie."""
    logger.info("=" * 60)
    logger.info("Test 1: Fetching single movie (Inception)")
    logger.info("=" * 60)
    
    client = MovieAPIClient(db_path="db/movies.db")
    
    movie = client.fetch_movie("Inception", year=2010)
    if movie:
        logger.info(f"✓ Fetched: {movie['title']}")
        logger.info(f"  Genre: {movie['genre']}")
        logger.info(f"  Plot: {movie['plot'][:100]}...")
        logger.info(f"  Poster: {movie['poster_url'][:60]}..." if len(movie['poster_url']) > 60 else f"  Poster: {movie['poster_url']}")
    else:
        logger.warning("✗ Failed to fetch movie")


def test_multiple_movies():
    """Test fetching and saving multiple movies."""
    logger.info("\n" + "=" * 60)
    logger.info("Test 2: Fetching and saving multiple popular movies")
    logger.info("=" * 60)
    
    client = MovieAPIClient(db_path="db/movies.db")
    
    inserted = client.fetch_popular_movies()
    logger.info(f"✓ Inserted {inserted} movies into api_movies table")


def test_search_movies():
    """Test searching for movies."""
    logger.info("\n" + "=" * 60)
    logger.info("Test 3: Searching for movies (search query)")
    logger.info("=" * 60)
    
    client = MovieAPIClient(db_path="db/movies.db")
    
    results = client.search_movies("Batman", year=2008)
    if results:
        logger.info(f"✓ Found {len(results)} search results")
        for i, movie in enumerate(results[:3], 1):
            logger.info(f"  {i}. {movie['title']} - {movie['genre']}")
    else:
        logger.warning("✗ No search results found")


def test_database_verification():
    """Verify data in the database."""
    logger.info("\n" + "=" * 60)
    logger.info("Test 4: Verifying data in database")
    logger.info("=" * 60)
    
    try:
        conn = sqlite3.connect("db/movies.db")
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute("SELECT COUNT(*) as count FROM api_movies")
        count = c.fetchone()['count']
        logger.info(f"Total movies in api_movies table: {count}")
        
        if count > 0:
            # Show all movies
            c.execute("SELECT * FROM api_movies")
            movies = c.fetchall()
            
            logger.info("\nAll movies in api_movies table:")
            for i, movie in enumerate(movies, 1):
                logger.info(f"{i}. {movie['title']}")
                logger.info(f"   Genre: {movie['genre']}")
                logger.info(f"   Plot: {movie['plot'][:80]}..." if len(movie['plot']) > 80 else f"   Plot: {movie['plot']}")
                logger.info(f"   Poster: {movie['poster_url'][:60]}..." if len(movie['poster_url']) > 60 else f"   Poster: {movie['poster_url']}")
        
        conn.close()
        logger.info("=" * 60)
        logger.info("✓ Test completed successfully!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Error verifying data: {e}")
        return False
    
    return True


if __name__ == "__main__":
    logger.info("\n\n🎬 MovieAPIClient Test Suite 🎬\n")
    
    # Run tests
    test_single_movie()
    test_search_movies()
    test_multiple_movies()
    test_database_verification()
