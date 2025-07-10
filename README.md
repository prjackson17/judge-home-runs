# Aaron Judge Home Run Prediction API

A comprehensive Monte Carlo simulation system for predicting Aaron Judge's home run totals, featuring real-time MLB data integration and multiple statistical models.

## Features

- **Real-time Data Integration**: Fetches current MLB statistics using official APIs
- **Multiple Simulation Models**:
  - Basic model (overall HR/PA rate)
  - Home vs Away performance splits
  - Left-handed vs Right-handed pitcher matchups
  - Ballpark factor adjustments
  - Advanced combined model with current season weighting

- **Comprehensive API**: RESTful endpoints for all models and data
- **Automatic Updates**: Scheduled data refreshes during baseball season
- **Statistical Analysis**: Monte Carlo simulations with confidence intervals
- **Visualization Support**: Generate charts and distribution plots

## Quick Start

### Installation

1. Clone or download this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the API Server

```bash
python start_server.py
```

The API will be available at `http://localhost:8000`

### API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.

## API Endpoints

### Data Endpoints
- `GET /current-stats` - Aaron Judge's current season statistics
- `GET /home-away-splits` - Home vs away performance splits  
- `GET /pitcher-splits` - Performance vs LHP/RHP
- `GET /schedule` - Yankees remaining schedule
- `GET /ballpark-factors` - MLB ballpark factors

### Simulation Endpoints
- `GET /simulate/basic` - Run basic Monte Carlo model
- `GET /simulate/all` - Run all simulation models
- `GET /simulate/distribution/{model}` - Get full distribution data
- `POST /refresh-data` - Refresh cached MLB data

### Example Response

```json
{
  "basic": {
    "mean_hrs": 53.2,
    "median_hrs": 53.0,
    "prob_over_40": 0.968,
    "prob_over_50": 0.657,
    "prob_over_60": 0.185,
    "percentile_5": 44.0,
    "percentile_95": 63.0
  },
  "current_stats": {
    "home_runs": 15,
    "plate_appearances": 180,
    "games_played": 45,
    "hr_per_pa": 0.0833
  }
}
```

## Models Explained

### Basic Model
Uses Judge's overall HR/PA rate with a uniform distribution of 600-700 plate appearances over the season. Based on binomial distribution simulation.

### Home vs Away Model  
Splits performance between home games (typically better) and away games, using separate HR/PA rates for each scenario.

### Pitcher Handedness Model
Accounts for performance differences against left-handed vs right-handed pitching, with approximately 75% of PAs against RHP.

### Ballpark Factor Model
Adjusts predictions based on the specific ballparks where games are played, using Baseball Savant's park factors relative to Yankee Stadium.

### Advanced Combined Model
Integrates current season performance with multiple factors, adjusting historical rates based on year-to-date statistics.

## Data Sources

- **MLB Stats API**: Official MLB statistics and player data
- **Baseball Savant**: Advanced metrics and ballpark factors
- **Yankees Schedule**: Official team schedule for ballpark factor calculations

## Development

### Running Tests
```bash
python test_models.py
```

### Manual Data Update
```bash
python data_updater.py
```

### Generate Visualizations
```bash
python visualization.py
```

## Project Structure

```
├── main.py                    # FastAPI application
├── data_fetcher.py           # MLB data collection
├── monte_carlo_simulator.py  # Simulation models
├── data_updater.py          # Automated data updates
├── visualization.py         # Chart generation
├── test_models.py           # Unit tests
├── start_server.py          # Startup script
├── requirements.txt         # Dependencies
└── README.md               # This file
```

## Configuration

The system uses sensible defaults but can be customized:

- **Number of Monte Carlo trials**: Default 2500 (adjustable via API parameter)
- **Plate appearance range**: 600-700 (uniform distribution)
- **Data update frequency**: Every 4 hours during season
- **Cache directory**: `./cache/` for storing fetched data

## Statistical Background

The Monte Carlo method simulates thousands of possible season outcomes based on:

1. **Binomial Distribution**: Models home run hitting as success/failure trials
2. **Uniform Distribution**: Accounts for variability in total plate appearances
3. **Historical Data**: Uses 2024 performance as baseline when current data unavailable
4. **Park Factors**: Adjusts for hitting environment differences across MLB stadiums

Each simulation runs 2,500 trials by default, providing robust statistical confidence in the predictions.

## Future Enhancements

- **Weather Integration**: Account for weather effects on home run hitting
- **Pitcher Quality**: Adjust for strength of opposing pitching
- **Injury Risk**: Model potential games missed due to injury
- **Historical Comparison**: Compare predictions to other great seasons
- **Real-time Updates**: Live updates during games

## License

This project is for educational and research purposes. MLB data is used under fair use principles.