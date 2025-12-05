#!/usr/bin/env python3
"""
Setup script to populate both scraped_movies and api_movies tables.
Run this once to populate the database before accessing the Flask endpoints.
"""

import logging
from utils.scraper import MovieScraper
from utils.api_client import MovieAPIClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    logger.info("=" * 70)
    logger.info("🎬 Setting up movie data for Flask app 🎬")
    logger.info("=" * 70)
    
    # Populate scraped_movies table
    logger.info("\n[1/2] Populating scraped_movies table...")
    logger.info("-" * 70)
    scraper = MovieScraper(db_path="db/movies.db")
    scraped_count = scraper.scrape_and_save(limit=10)
    logger.info(f"✓ Scraped {scraped_count} movies\n")
    
    # Populate api_movies table
    logger.info("[2/2] Populating api_movies table...")
    logger.info("-" * 70)
    api_client = MovieAPIClient(db_path="db/movies.db")
    api_count = api_client.fetch_popular_movies()
    logger.info(f"✓ Fetched {api_count} movies from OMDb API (or sample data)\n")
    
    logger.info("=" * 70)
    logger.info("✅ Setup Complete!")
    logger.info("=" * 70)
    logger.info(f"Total scraped movies: {scraped_count}")
    logger.info(f"Total API movies: {api_count}")
    logger.info("\nYou can now access:")
    logger.info("  • /scraped     - View scraped movies")
    logger.info("  • /api         - View API movies")
    logger.info("=" * 70)


if __name__ == "__main__":
    main()
