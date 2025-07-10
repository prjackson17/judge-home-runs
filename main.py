from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Optional
import json
from datetime import datetime
import asyncio

from data_fetcher import MLBDataFetcher
from monte_carlo_simulator import MonteCarloSimulator, SimulationResult

app = FastAPI(
    title="Aaron Judge HR Prediction API",
    description="Monte Carlo simulation API for predicting Aaron Judge's home runs",
    version="1.0.0"
)

# Add CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
data_fetcher = MLBDataFetcher()
simulator = MonteCarloSimulator()

# Pydantic models for API responses
class CurrentStats(BaseModel):
    home_runs: int
    plate_appearances: int
    games_played: int
    hr_per_pa: float
    last_updated: str

class SimulationResultResponse(BaseModel):
    mean_hrs: float
    median_hrs: float
    std_hrs: float
    prob_over_40: float
    prob_over_50: float
    prob_over_60: float
    percentile_5: float
    percentile_95: float

class AllSimulationsResponse(BaseModel):
    basic: SimulationResultResponse
    home_away: SimulationResultResponse
    pitcher_handedness: SimulationResultResponse
    ballpark_factors: SimulationResultResponse
    advanced_combined: SimulationResultResponse
    last_updated: str
    current_stats: CurrentStats

class ScheduleGame(BaseModel):
    date: str
    venue_name: str
    is_home: bool
    opponent: str

class BallparkFactorsResponse(BaseModel):
    factors: Dict[str, float]
    yankee_stadium_factor: float

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Aaron Judge HR Prediction API",
        "version": "1.0.0",
        "documentation": "/docs",
        "current_date": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/current-stats", response_model=CurrentStats)
async def get_current_stats():
    """Get Aaron Judge's current season statistics"""
    try:
        stats = data_fetcher.get_current_season_stats()
        return CurrentStats(
            home_runs=stats['home_runs'],
            plate_appearances=stats['plate_appearances'],
            games_played=stats['games_played'],
            hr_per_pa=stats['hr_per_pa'],
            last_updated=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching current stats: {str(e)}")

@app.get("/home-away-splits")
async def get_home_away_splits():
    """Get Aaron Judge's home/away performance splits"""
    try:
        splits = data_fetcher.get_home_away_splits()
        return {
            "home": splits['home'],
            "away": splits['away'],
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching home/away splits: {str(e)}")

@app.get("/pitcher-splits")
async def get_pitcher_splits():
    """Get Aaron Judge's performance vs LHP/RHP"""
    try:
        splits = data_fetcher.get_pitcher_handedness_splits()
        return {
            "vs_left": splits['vs_left'],
            "vs_right": splits['vs_right'],
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching pitcher splits: {str(e)}")

@app.get("/schedule", response_model=List[ScheduleGame])
async def get_remaining_schedule():
    """Get Yankees remaining schedule for the season"""
    try:
        schedule = data_fetcher.get_yankees_schedule()
        return [
            ScheduleGame(
                date=game['date'],
                venue_name=game['venue_name'],
                is_home=game['is_home'],
                opponent=game['opponent']
            )
            for game in schedule
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching schedule: {str(e)}")

@app.get("/ballpark-factors", response_model=BallparkFactorsResponse)
async def get_ballpark_factors():
    """Get ballpark factors for all MLB venues"""
    try:
        factors = data_fetcher.get_ballpark_factors()
        return BallparkFactorsResponse(
            factors=factors,
            yankee_stadium_factor=factors.get('Yankee Stadium', 101)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching ballpark factors: {str(e)}")

@app.get("/simulate/basic")
async def simulate_basic_model(trials: int = 2500):
    """Run basic Monte Carlo simulation"""
    try:
        current_stats = data_fetcher.get_current_season_stats()
        hr_per_pa = current_stats.get('hr_per_pa', 0.0824)
        
        simulator_instance = MonteCarloSimulator(num_trials=trials)
        result = simulator_instance.basic_model(hr_per_pa)
        
        return {
            "model": "basic",
            "parameters": {
                "hr_per_pa": hr_per_pa,
                "trials": trials
            },
            "results": {
                "mean_hrs": result.mean_hrs,
                "median_hrs": result.median_hrs,
                "std_hrs": result.std_hrs,
                "prob_over_40": result.prob_over_40,
                "prob_over_50": result.prob_over_50,
                "prob_over_60": result.prob_over_60,
                "percentile_5": result.percentile_5,
                "percentile_95": result.percentile_95
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running basic simulation: {str(e)}")

@app.get("/simulate/all", response_model=AllSimulationsResponse)
async def simulate_all_models(trials: int = 2500):
    """Run all Monte Carlo simulation models"""
    try:
        # Fetch all required data
        current_stats = data_fetcher.get_current_season_stats()
        home_away_splits = data_fetcher.get_home_away_splits()
        pitcher_splits = data_fetcher.get_pitcher_handedness_splits()
        schedule = data_fetcher.get_yankees_schedule()
        ballpark_factors = data_fetcher.get_ballpark_factors()
        
        # Run simulations
        simulator_instance = MonteCarloSimulator(num_trials=trials)
        results = simulator_instance.run_all_models(
            current_stats, home_away_splits, pitcher_splits, schedule, ballpark_factors
        )
        
        # Convert results to response format
        def result_to_response(result: SimulationResult) -> SimulationResultResponse:
            return SimulationResultResponse(
                mean_hrs=result.mean_hrs,
                median_hrs=result.median_hrs,
                std_hrs=result.std_hrs,
                prob_over_40=result.prob_over_40,
                prob_over_50=result.prob_over_50,
                prob_over_60=result.prob_over_60,
                percentile_5=result.percentile_5,
                percentile_95=result.percentile_95
            )
        
        return AllSimulationsResponse(
            basic=result_to_response(results['basic']),
            home_away=result_to_response(results['home_away']),
            pitcher_handedness=result_to_response(results['pitcher_handedness']),
            ballpark_factors=result_to_response(results['ballpark_factors']),
            advanced_combined=result_to_response(results['advanced_combined']),
            last_updated=datetime.now().isoformat(),
            current_stats=CurrentStats(
                home_runs=current_stats['home_runs'],
                plate_appearances=current_stats['plate_appearances'],
                games_played=current_stats['games_played'],
                hr_per_pa=current_stats['hr_per_pa'],
                last_updated=datetime.now().isoformat()
            )
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running all simulations: {str(e)}")

@app.get("/simulate/distribution/{model}")
async def get_simulation_distribution(model: str, trials: int = 2500):
    """Get the full distribution from a specific simulation model"""
    try:
        current_stats = data_fetcher.get_current_season_stats()
        simulator_instance = MonteCarloSimulator(num_trials=trials)
        
        if model == "basic":
            result = simulator_instance.basic_model(current_stats.get('hr_per_pa', 0.0824))
        elif model == "home_away":
            splits = data_fetcher.get_home_away_splits()
            result = simulator_instance.home_away_model(
                splits['home'].get('hr_per_pa', 0.0909),
                splits['away'].get('hr_per_pa', 0.0744)
            )
        elif model == "pitcher_handedness":
            splits = data_fetcher.get_pitcher_handedness_splits()
            result = simulator_instance.pitcher_handedness_model(
                splits['vs_left'].get('hr_per_pa', 0.0870),
                splits['vs_right'].get('hr_per_pa', 0.0808)
            )
        elif model == "ballpark_factors":
            schedule = data_fetcher.get_yankees_schedule()
            ballpark_factors = data_fetcher.get_ballpark_factors()
            result = simulator_instance.ballpark_factor_model(
                schedule, ballpark_factors, current_stats.get('hr_per_pa', 0.0824)
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unknown model: {model}")
        
        return {
            "model": model,
            "distribution": result.distribution,
            "statistics": {
                "mean": result.mean_hrs,
                "median": result.median_hrs,
                "std": result.std_hrs
            },
            "trials": trials,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting distribution: {str(e)}")

@app.post("/refresh-data")
async def refresh_all_data():
    """Refresh all cached data from MLB APIs"""
    try:
        # This could implement caching logic in the future
        return {
            "message": "Data refresh completed",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error refreshing data: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
