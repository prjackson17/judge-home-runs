import os
from typing import Dict, List, Optional, Tuple
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

class MLBDataFetcher:
    """Fetches real-time MLB data from various sources"""
    
    def __init__(self):
        self.base_url = "https://statsapi.mlb.com/api/v1"
        self.judge_player_id = 592450  # Aaron Judge's MLB player ID
        
    def get_current_season_stats(self, player_id: int = None) -> Dict:
        """Fetch current season stats for Aaron Judge"""
        if player_id is None:
            player_id = self.judge_player_id
            
        current_year = datetime.now().year
        url = f"{self.base_url}/people/{player_id}/stats"
        
        params = {
            'stats': 'season',
            'season': current_year,
            'sportId': 1
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'stats' in data and len(data['stats']) > 0:
                hitting_stats = data['stats'][0]['splits'][0]['stat']
                return {
                    'home_runs': hitting_stats.get('homeRuns', 0),
                    'plate_appearances': hitting_stats.get('plateAppearances', 0),
                    'at_bats': hitting_stats.get('atBats', 0),
                    'hits': hitting_stats.get('hits', 0),
                    'games_played': hitting_stats.get('gamesPlayed', 0),
                    'hr_per_pa': hitting_stats.get('homeRuns', 0) / max(hitting_stats.get('plateAppearances', 1), 1)
                }
        except Exception as e:
            print(f"Error fetching current stats: {e}")
            
        # Return default/placeholder data if API fails
        return {
            'home_runs': 0,
            'plate_appearances': 0,
            'at_bats': 0,
            'hits': 0,
            'games_played': 0,
            'hr_per_pa': 0.0824  # 2024 rate as fallback
        }
    
    def get_home_away_splits(self, player_id: int = None) -> Dict:
        """Fetch home/away splits for current season"""
        if player_id is None:
            player_id = self.judge_player_id
            
        current_year = datetime.now().year
        url = f"{self.base_url}/people/{player_id}/stats"
        
        params = {
            'stats': 'homeAndAway',
            'season': current_year,
            'sportId': 1
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            home_stats = away_stats = {}
            
            if 'stats' in data and len(data['stats']) > 0:
                for split in data['stats'][0]['splits']:
                    stat = split['stat']
                    if split['split']['code'] == 'H':  # Home
                        home_stats = {
                            'home_runs': stat.get('homeRuns', 0),
                            'plate_appearances': stat.get('plateAppearances', 0),
                            'hr_per_pa': stat.get('homeRuns', 0) / max(stat.get('plateAppearances', 1), 1)
                        }
                    elif split['split']['code'] == 'A':  # Away
                        away_stats = {
                            'home_runs': stat.get('homeRuns', 0),
                            'plate_appearances': stat.get('plateAppearances', 0),
                            'hr_per_pa': stat.get('homeRuns', 0) / max(stat.get('plateAppearances', 1), 1)
                        }
                        
            return {'home': home_stats, 'away': away_stats}
            
        except Exception as e:
            print(f"Error fetching home/away splits: {e}")
            # Return 2024 data as fallback
            return {
                'home': {
                    'home_runs': 31,
                    'plate_appearances': 341,
                    'hr_per_pa': 0.0909
                },
                'away': {
                    'home_runs': 27,
                    'plate_appearances': 363,
                    'hr_per_pa': 0.0744
                }
            }
    
    def get_pitcher_handedness_splits(self, player_id: int = None) -> Dict:
        """Fetch splits vs LHP/RHP for current season"""
        if player_id is None:
            player_id = self.judge_player_id
            
        current_year = datetime.now().year
        url = f"{self.base_url}/people/{player_id}/stats"
        
        params = {
            'stats': 'vsLeft,vsRight',
            'season': current_year,
            'sportId': 1
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            vs_left = vs_right = {}
            
            if 'stats' in data and len(data['stats']) > 0:
                for split in data['stats'][0]['splits']:
                    stat = split['stat']
                    if 'Left' in split['split']['description']:
                        vs_left = {
                            'home_runs': stat.get('homeRuns', 0),
                            'plate_appearances': stat.get('plateAppearances', 0),
                            'hr_per_pa': stat.get('homeRuns', 0) / max(stat.get('plateAppearances', 1), 1)
                        }
                    elif 'Right' in split['split']['description']:
                        vs_right = {
                            'home_runs': stat.get('homeRuns', 0),
                            'plate_appearances': stat.get('plateAppearances', 0),
                            'hr_per_pa': stat.get('homeRuns', 0) / max(stat.get('plateAppearances', 1), 1)
                        }
                        
            return {'vs_left': vs_left, 'vs_right': vs_right}
            
        except Exception as e:
            print(f"Error fetching pitcher handedness splits: {e}")
            # Return 2024 data as fallback
            return {
                'vs_left': {
                    'home_runs': 16,
                    'plate_appearances': 184,
                    'hr_per_pa': 0.0870
                },
                'vs_right': {
                    'home_runs': 42,
                    'plate_appearances': 520,
                    'hr_per_pa': 0.0808
                }
            }
    
    def get_yankees_schedule(self) -> List[Dict]:
        """Fetch Yankees remaining schedule for the season"""
        current_year = datetime.now().year
        yankees_team_id = 147
        
        url = f"{self.base_url}/schedule"
        params = {
            'teamId': yankees_team_id,
            'season': current_year,
            'sportId': 1
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            schedule = []
            today = datetime.now().date()
            
            for date_entry in data.get('dates', []):
                for game in date_entry.get('games', []):
                    game_date = datetime.strptime(game['gameDate'][:10], '%Y-%m-%d').date()
                    
                    # Only include future games
                    if game_date >= today:
                        venue = game.get('venue', {})
                        schedule.append({
                            'date': game_date.isoformat(),
                            'venue_name': venue.get('name', ''),
                            'venue_id': venue.get('id', 0),
                            'is_home': game['teams']['home']['team']['id'] == yankees_team_id,
                            'opponent': game['teams']['away']['team']['name'] if game['teams']['home']['team']['id'] == yankees_team_id else game['teams']['home']['team']['name']
                        })
                        
            return schedule
            
        except Exception as e:
            print(f"Error fetching schedule: {e}")
            return []
    
    def get_ballpark_factors(self) -> Dict[str, float]:
        """Get ballpark factors for all MLB venues"""
        # This would ideally fetch from Baseball Savant or similar source
        # For now, using approximate factors based on your research
        return {
            'Yankee Stadium': 101,
            'Fenway Park': 96,
            'Tropicana Field': 92,
            'Rogers Centre': 95,
            'Oriole Park at Camden Yards': 105,
            'Progressive Field': 98,
            'Guaranteed Rate Field': 100,
            'Comerica Park': 94,
            'Kauffman Stadium': 96,
            'Target Field': 99,
            'Minute Maid Park': 103,
            'Angel Stadium': 97,
            'Oakland Coliseum': 89,
            'T-Mobile Park': 93,
            'Globe Life Field': 106,
            'Coors Field': 112,
            'Chase Field': 102,
            'Dodger Stadium': 95,
            'PETCO Park': 91,
            'Oracle Park': 88,
            'American Family Field': 102,
            'Wrigley Field': 104,
            'Great American Ball Park': 105,
            'PNC Park': 96,
            'Busch Stadium': 97,
            'Truist Park': 103,
            'loanDepot park': 95,
            'Citi Field': 94,
            'Citizens Bank Park': 107,
            'Nationals Park': 99,
            'Sutter Health Park': 113,  # Athletics temporary stadium
            'Steinbrenner Field': 108  # Rays temporary stadium
        }

# Example usage and testing
if __name__ == "__main__":
    fetcher = MLBDataFetcher()
    
    print("Current Season Stats:")
    current_stats = fetcher.get_current_season_stats()
    print(json.dumps(current_stats, indent=2))
    
    print("\nHome/Away Splits:")
    home_away = fetcher.get_home_away_splits()
    print(json.dumps(home_away, indent=2))
    
    print("\nPitcher Handedness Splits:")
    pitcher_splits = fetcher.get_pitcher_handedness_splits()
    print(json.dumps(pitcher_splits, indent=2))
    
    print("\nUpcoming Games:")
    schedule = fetcher.get_yankees_schedule()
    print(f"Found {len(schedule)} upcoming games")
