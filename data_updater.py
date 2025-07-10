import schedule
import time
import logging
from datetime import datetime
from data_fetcher import MLBDataFetcher
import json
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_updater.log'),
        logging.StreamHandler()
    ]
)

class DataUpdater:
    """Handles automatic data updates and caching"""
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        self.data_fetcher = MLBDataFetcher()
        
        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)
        
    def update_all_data(self):
        """Update all MLB data and cache results"""
        try:
            logging.info("Starting data update...")
            
            # Fetch all data
            current_stats = self.data_fetcher.get_current_season_stats()
            home_away_splits = self.data_fetcher.get_home_away_splits()
            pitcher_splits = self.data_fetcher.get_pitcher_handedness_splits()
            schedule = self.data_fetcher.get_yankees_schedule()
            ballpark_factors = self.data_fetcher.get_ballpark_factors()
            
            # Cache the data
            cache_data = {
                'current_stats': current_stats,
                'home_away_splits': home_away_splits,
                'pitcher_splits': pitcher_splits,
                'schedule': schedule,
                'ballpark_factors': ballpark_factors,
                'last_updated': datetime.now().isoformat()
            }
            
            # Save to cache file
            cache_file = os.path.join(self.cache_dir, 'mlb_data.json')
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            logging.info(f"Data update completed successfully. Stats: {current_stats['home_runs']} HRs in {current_stats['games_played']} games")
            
        except Exception as e:
            logging.error(f"Error updating data: {str(e)}")
    
    def load_cached_data(self):
        """Load data from cache if available"""
        cache_file = os.path.join(self.cache_dir, 'mlb_data.json')
        
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"Error loading cached data: {str(e)}")
                return None
        return None
    
    def start_scheduler(self):
        """Start the scheduled data updates"""
        # Update data every 4 hours during baseball season
        schedule.every(4).hours.do(self.update_all_data)
        
        # Initial update
        self.update_all_data()
        
        logging.info("Data updater scheduler started. Updates every 4 hours.")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

if __name__ == "__main__":
    updater = DataUpdater()
    
    # For testing, just run one update
    updater.update_all_data()
    
    # Uncomment to start continuous scheduler
    # updater.start_scheduler()
