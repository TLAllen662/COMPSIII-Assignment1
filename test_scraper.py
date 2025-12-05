#!/usr/bin/env python3
"""
Test script for MovieScraper class.
Scrapes IMDb top 250 and verifies data is stored in the database.
"""

import sqlite3
import logging
from utils.scraper import MovieScraper

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_scraper(limit: int = 10):
    """Test the MovieScraper class."""
    logger.info("=" * 60)
    logger.info("Starting MovieScraper test...")
    logger.info("=" * 60)
    
    scraper = MovieScraper(db_path="db/movies.db")
    
    # Scrape and save
    logger.info(f"Scraping up to {limit} movies from IMDb...")
    inserted = scraper.scrape_and_save(limit=limit)
    
    logger.info(f"Inserted {inserted} movies into the database")
    
    # Verify data in database
    logger.info("Verifying data in database...")
    try:
        conn = sqlite3.connect("db/movies.db")
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute("SELECT COUNT(*) as count FROM scraped_movies")
        count = c.fetchone()['count']
        logger.info(f"Total movies in scraped_movies table: {count}")
        
        # Show first 5 movies
        c.execute("SELECT * FROM scraped_movies LIMIT 5")
        movies = c.fetchall()
        
        logger.info("\nFirst 5 movies:")
        for i, movie in enumerate(movies, 1):
            logger.info(f"{i}. {movie['title']} ({movie['year']}) - Rating: {movie['rating']}")
            logger.info(f"   Poster: {movie['poster_url'][:60]}..." if len(movie['poster_url']) > 60 else f"   Poster: {movie['poster_url']}")
        
        conn.close()
        logger.info("=" * 60)
        logger.info("Test completed successfully!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Error verifying data: {e}")
        return False
    
    return True


if __name__ == "__main__":
    test_scraper(limit=10)
