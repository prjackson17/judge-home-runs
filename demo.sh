#!/bin/bash

# Aaron Judge HR Prediction API - Quick Demo Script

echo "🏠 Aaron Judge Home Run Prediction Demo"
echo "========================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

echo "📦 Installing dependencies..."
python3 -m pip install -r requirements.txt

echo ""
echo "🧪 Running tests..."
python3 test_models.py

echo ""
echo "📊 Running sample simulation..."
python3 -c "
from monte_carlo_simulator import MonteCarloSimulator
from data_fetcher import MLBDataFetcher

print('Fetching current Aaron Judge stats...')
fetcher = MLBDataFetcher()
stats = fetcher.get_current_season_stats()
print(f'Current: {stats[\"home_runs\"]} HRs in {stats[\"games_played\"]} games')
print(f'HR/PA Rate: {stats[\"hr_per_pa\"]:.4f}')

print('\nRunning Monte Carlo simulation...')
simulator = MonteCarloSimulator(num_trials=1000)
result = simulator.basic_model(stats['hr_per_pa'])

print(f'Predicted season total: {result.mean_hrs:.1f} HRs')
print(f'90% confidence interval: {result.percentile_5:.1f} - {result.percentile_95:.1f}')
print(f'Probability of 50+ HRs: {result.prob_over_50:.3f}')
print(f'Probability of 60+ HRs: {result.prob_over_60:.3f}')
"

echo ""
echo "🚀 Starting API server..."
echo "Visit http://localhost:8000/docs for interactive documentation"
echo "Press Ctrl+C to stop the server"
echo ""

python3 start_server.py
