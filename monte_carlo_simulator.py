import numpy as np
from scipy import stats
from typing import Dict, List, Tuple
import json
from dataclasses import dataclass

@dataclass
class SimulationResult:
    """Data class to store Monte Carlo simulation results"""
    mean_hrs: float
    median_hrs: float
    std_hrs: float
    prob_over_40: float
    prob_over_50: float
    prob_over_60: float
    percentile_5: float
    percentile_95: float
    distribution: List[int]

class MonteCarloSimulator:
    """Monte Carlo simulation engine for Aaron Judge home run predictions"""
    
    def __init__(self, num_trials: int = 2500):
        self.num_trials = num_trials
        np.random.seed(42)  # For reproducible results
    
    def basic_model(self, hr_per_pa: float, min_pa: int = 600, max_pa: int = 700) -> SimulationResult:
        """
        Basic Monte Carlo model using overall HR/PA rate
        
        Args:
            hr_per_pa: Home runs per plate appearance rate
            min_pa: Minimum plate appearances (uniform distribution)
            max_pa: Maximum plate appearances (uniform distribution)
        """
        results = []
        
        for _ in range(self.num_trials):
            # Generate random number of plate appearances
            pa = np.random.uniform(min_pa, max_pa)
            
            # Simulate home runs using binomial distribution
            home_runs = np.random.binomial(int(pa), hr_per_pa)
            results.append(home_runs)
        
        return self._calculate_statistics(results)
    
    def home_away_model(self, home_hr_per_pa: float, away_hr_per_pa: float, 
                       min_pa: int = 600, max_pa: int = 700) -> SimulationResult:
        """
        Monte Carlo model splitting home and away performance
        
        Args:
            home_hr_per_pa: Home runs per PA at home games
            away_hr_per_pa: Home runs per PA at away games
            min_pa: Minimum total plate appearances
            max_pa: Maximum total plate appearances
        """
        results = []
        
        for _ in range(self.num_trials):
            # Generate random total plate appearances
            total_pa = np.random.uniform(min_pa, max_pa)
            
            # Split roughly 50/50 between home and away
            home_pa = int(np.ceil(total_pa / 2))
            away_pa = int(np.floor(total_pa / 2))
            
            # Simulate home runs for each scenario
            home_hrs = np.random.binomial(home_pa, home_hr_per_pa)
            away_hrs = np.random.binomial(away_pa, away_hr_per_pa)
            
            total_hrs = home_hrs + away_hrs
            results.append(total_hrs)
        
        return self._calculate_statistics(results)
    
    def pitcher_handedness_model(self, vs_left_hr_per_pa: float, vs_right_hr_per_pa: float,
                                min_pa: int = 600, max_pa: int = 700,
                                min_rhp_pct: float = 0.70, max_rhp_pct: float = 0.80) -> SimulationResult:
        """
        Monte Carlo model accounting for pitcher handedness
        
        Args:
            vs_left_hr_per_pa: HR/PA rate vs left-handed pitching
            vs_right_hr_per_pa: HR/PA rate vs right-handed pitching
            min_pa: Minimum total plate appearances
            max_pa: Maximum total plate appearances
            min_rhp_pct: Minimum percentage of PAs vs RHP
            max_rhp_pct: Maximum percentage of PAs vs RHP
        """
        results = []
        
        for _ in range(self.num_trials):
            # Generate random total plate appearances
            total_pa = np.random.uniform(min_pa, max_pa)
            
            # Generate random percentage of PAs vs RHP
            rhp_pct = np.random.uniform(min_rhp_pct, max_rhp_pct)
            
            # Calculate PAs vs each handedness
            vs_right_pa = int(total_pa * rhp_pct)
            vs_left_pa = int(total_pa * (1 - rhp_pct))
            
            # Simulate home runs vs each handedness
            vs_right_hrs = np.random.binomial(vs_right_pa, vs_right_hr_per_pa)
            vs_left_hrs = np.random.binomial(vs_left_pa, vs_left_hr_per_pa)
            
            total_hrs = vs_right_hrs + vs_left_hrs
            results.append(total_hrs)
        
        return self._calculate_statistics(results)
    
    def ballpark_factor_model(self, schedule: List[Dict], ballpark_factors: Dict[str, float],
                             base_hr_per_pa: float, yankee_stadium_factor: float = 101,
                             pa_per_game: float = 4.45) -> SimulationResult:
        """
        Monte Carlo model incorporating ballpark factors
        
        Args:
            schedule: List of games with venue information
            ballpark_factors: Dictionary mapping venue names to park factors
            base_hr_per_pa: Base HR/PA rate (typically overall season rate)
            yankee_stadium_factor: Yankee Stadium park factor (baseline)
            pa_per_game: Average plate appearances per game
        """
        results = []
        
        # Calculate games at each ballpark
        ballpark_games = {}
        for game in schedule:
            venue = game.get('venue_name', 'Unknown')
            ballpark_games[venue] = ballpark_games.get(venue, 0) + 1
        
        for _ in range(self.num_trials):
            total_hrs = 0
            
            for venue, num_games in ballpark_games.items():
                # Get ballpark factor, default to 100 if not found
                park_factor = ballpark_factors.get(venue, 100)
                
                # Adjust HR/PA rate based on park factor relative to Yankee Stadium
                adjusted_hr_per_pa = base_hr_per_pa * (park_factor / yankee_stadium_factor)
                
                # Calculate expected PAs for this venue
                venue_pa = int(num_games * pa_per_game)
                
                # Simulate home runs at this venue
                venue_hrs = np.random.binomial(venue_pa, adjusted_hr_per_pa)
                total_hrs += venue_hrs
            
            results.append(total_hrs)
        
        return self._calculate_statistics(results)
    
    def advanced_combined_model(self, current_stats: Dict, home_away_splits: Dict,
                               pitcher_splits: Dict, schedule: List[Dict],
                               ballpark_factors: Dict[str, float]) -> SimulationResult:
        """
        Advanced model combining multiple factors with current season adjustments
        """
        results = []
        games_played = current_stats.get('games_played', 0)
        games_remaining = 162 - games_played
        
        # Estimate remaining PAs based on current pace
        current_pa_per_game = current_stats.get('plate_appearances', 0) / max(games_played, 1)
        if current_pa_per_game == 0:
            current_pa_per_game = 4.45  # Use historical average
        
        for _ in range(self.num_trials):
            total_hrs = current_stats.get('home_runs', 0)  # Start with current HRs
            
            # Simulate remaining games
            remaining_pa = int(games_remaining * current_pa_per_game * np.random.uniform(0.9, 1.1))
            
            # Use current season rates if available, otherwise fall back to historical
            current_hr_per_pa = current_stats.get('hr_per_pa', 0.0824)
            
            # Simple simulation for remaining season
            remaining_hrs = np.random.binomial(remaining_pa, current_hr_per_pa)
            total_hrs += remaining_hrs
            
            results.append(total_hrs)
        
        return self._calculate_statistics(results)
    
    def _calculate_statistics(self, results: List[int]) -> SimulationResult:
        """Calculate comprehensive statistics from simulation results"""
        results_array = np.array(results)
        
        return SimulationResult(
            mean_hrs=float(np.mean(results_array)),
            median_hrs=float(np.median(results_array)),
            std_hrs=float(np.std(results_array)),
            prob_over_40=float(np.mean(results_array > 40)),
            prob_over_50=float(np.mean(results_array > 50)),
            prob_over_60=float(np.mean(results_array > 60)),
            percentile_5=float(np.percentile(results_array, 5)),
            percentile_95=float(np.percentile(results_array, 95)),
            distribution=results
        )
    
    def run_all_models(self, current_stats: Dict, home_away_splits: Dict,
                      pitcher_splits: Dict, schedule: List[Dict],
                      ballpark_factors: Dict[str, float]) -> Dict[str, SimulationResult]:
        """Run all simulation models and return comprehensive results"""
        
        # Extract rates, use fallbacks if current season data not available
        overall_rate = current_stats.get('hr_per_pa', 0.0824)
        
        home_rate = home_away_splits.get('home', {}).get('hr_per_pa', 0.0909)
        away_rate = home_away_splits.get('away', {}).get('hr_per_pa', 0.0744)
        
        vs_left_rate = pitcher_splits.get('vs_left', {}).get('hr_per_pa', 0.0870)
        vs_right_rate = pitcher_splits.get('vs_right', {}).get('hr_per_pa', 0.0808)
        
        return {
            'basic': self.basic_model(overall_rate),
            'home_away': self.home_away_model(home_rate, away_rate),
            'pitcher_handedness': self.pitcher_handedness_model(vs_left_rate, vs_right_rate),
            'ballpark_factors': self.ballpark_factor_model(schedule, ballpark_factors, overall_rate),
            'advanced_combined': self.advanced_combined_model(
                current_stats, home_away_splits, pitcher_splits, schedule, ballpark_factors
            )
        }

# Example usage
if __name__ == "__main__":
    simulator = MonteCarloSimulator(num_trials=1000)  # Reduced for testing
    
    # Example with 2024 data
    basic_result = simulator.basic_model(hr_per_pa=0.0824)
    print(f"Basic Model - Mean HRs: {basic_result.mean_hrs:.1f}")
    print(f"P(>40 HRs): {basic_result.prob_over_40:.3f}")
    print(f"P(>50 HRs): {basic_result.prob_over_50:.3f}")
