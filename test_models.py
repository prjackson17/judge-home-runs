import unittest
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from monte_carlo_simulator import MonteCarloSimulator, SimulationResult
from data_fetcher import MLBDataFetcher

class TestMonteCarloSimulator(unittest.TestCase):
    """Test cases for Monte Carlo simulation models"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.simulator = MonteCarloSimulator(num_trials=100)  # Small number for testing
        
    def test_basic_model(self):
        """Test basic Monte Carlo model"""
        result = self.simulator.basic_model(hr_per_pa=0.0824)
        
        self.assertIsInstance(result, SimulationResult)
        self.assertGreater(result.mean_hrs, 0)
        self.assertGreater(result.prob_over_40, 0)
        self.assertEqual(len(result.distribution), 100)
        
        # Check that results are reasonable for Judge's performance
        self.assertGreater(result.mean_hrs, 30)  # Should be at least 30 HRs
        self.assertLess(result.mean_hrs, 80)     # Should be less than 80 HRs
    
    def test_home_away_model(self):
        """Test home/away split model"""
        result = self.simulator.home_away_model(
            home_hr_per_pa=0.0909, 
            away_hr_per_pa=0.0744
        )
        
        self.assertIsInstance(result, SimulationResult)
        self.assertGreater(result.mean_hrs, 0)
        self.assertEqual(len(result.distribution), 100)
    
    def test_pitcher_handedness_model(self):
        """Test pitcher handedness model"""
        result = self.simulator.pitcher_handedness_model(
            vs_left_hr_per_pa=0.0870,
            vs_right_hr_per_pa=0.0808
        )
        
        self.assertIsInstance(result, SimulationResult)
        self.assertGreater(result.mean_hrs, 0)
        self.assertEqual(len(result.distribution), 100)
    
    def test_ballpark_factor_model(self):
        """Test ballpark factor model"""
        # Mock schedule data
        schedule = [
            {'venue_name': 'Yankee Stadium', 'is_home': True},
            {'venue_name': 'Fenway Park', 'is_home': False},
        ] * 81  # 162 games total
        
        ballpark_factors = {
            'Yankee Stadium': 101,
            'Fenway Park': 96
        }
        
        result = self.simulator.ballpark_factor_model(
            schedule=schedule,
            ballpark_factors=ballpark_factors,
            base_hr_per_pa=0.0824
        )
        
        self.assertIsInstance(result, SimulationResult)
        self.assertGreater(result.mean_hrs, 0)
        self.assertEqual(len(result.distribution), 100)
    
    def test_probability_calculations(self):
        """Test that probability calculations are correct"""
        result = self.simulator.basic_model(hr_per_pa=0.0824)
        
        # Probabilities should be between 0 and 1
        self.assertGreaterEqual(result.prob_over_40, 0)
        self.assertLessEqual(result.prob_over_40, 1)
        self.assertGreaterEqual(result.prob_over_50, 0)
        self.assertLessEqual(result.prob_over_50, 1)
        self.assertGreaterEqual(result.prob_over_60, 0)
        self.assertLessEqual(result.prob_over_60, 1)
        
        # Higher thresholds should have lower probabilities
        self.assertGreaterEqual(result.prob_over_40, result.prob_over_50)
        self.assertGreaterEqual(result.prob_over_50, result.prob_over_60)

class TestMLBDataFetcher(unittest.TestCase):
    """Test cases for MLB data fetching"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.fetcher = MLBDataFetcher()
    
    def test_current_season_stats_structure(self):
        """Test that current season stats return expected structure"""
        stats = self.fetcher.get_current_season_stats()
        
        required_keys = ['home_runs', 'plate_appearances', 'games_played', 'hr_per_pa']
        for key in required_keys:
            self.assertIn(key, stats)
            self.assertIsInstance(stats[key], (int, float))
    
    def test_home_away_splits_structure(self):
        """Test home/away splits structure"""
        splits = self.fetcher.get_home_away_splits()
        
        self.assertIn('home', splits)
        self.assertIn('away', splits)
        
        for split in ['home', 'away']:
            self.assertIn('home_runs', splits[split])
            self.assertIn('plate_appearances', splits[split])
            self.assertIn('hr_per_pa', splits[split])
    
    def test_pitcher_splits_structure(self):
        """Test pitcher handedness splits structure"""
        splits = self.fetcher.get_pitcher_handedness_splits()
        
        self.assertIn('vs_left', splits)
        self.assertIn('vs_right', splits)
        
        for split in ['vs_left', 'vs_right']:
            self.assertIn('home_runs', splits[split])
            self.assertIn('plate_appearances', splits[split])
            self.assertIn('hr_per_pa', splits[split])
    
    def test_ballpark_factors(self):
        """Test ballpark factors"""
        factors = self.fetcher.get_ballpark_factors()
        
        self.assertIsInstance(factors, dict)
        self.assertIn('Yankee Stadium', factors)
        self.assertGreater(len(factors), 25)  # Should have all MLB parks
        
        # All factors should be positive numbers
        for venue, factor in factors.items():
            self.assertGreater(factor, 0)
            self.assertLess(factor, 150)  # Reasonable upper bound

def run_tests():
    """Run all tests"""
    unittest.main(verbosity=2)

if __name__ == "__main__":
    run_tests()
