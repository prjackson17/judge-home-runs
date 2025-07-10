import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple
import json
from monte_carlo_simulator import SimulationResult

class VisualizationGenerator:
    """Generate visualizations for Monte Carlo simulation results"""
    
    def __init__(self):
        # Set up plotting style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
    
    def plot_distribution_histogram(self, result: SimulationResult, title: str, 
                                  filename: str = None) -> str:
        """Create histogram of simulation distribution"""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Create histogram
        n, bins, patches = ax.hist(result.distribution, bins=30, alpha=0.7, 
                                 density=True, edgecolor='black')
        
        # Add vertical lines for key statistics
        ax.axvline(result.mean_hrs, color='red', linestyle='--', linewidth=2, 
                  label=f'Mean: {result.mean_hrs:.1f}')
        ax.axvline(result.median_hrs, color='orange', linestyle='--', linewidth=2,
                  label=f'Median: {result.median_hrs:.1f}')
        ax.axvline(result.percentile_5, color='gray', linestyle=':', 
                  label=f'5th percentile: {result.percentile_5:.1f}')
        ax.axvline(result.percentile_95, color='gray', linestyle=':', 
                  label=f'95th percentile: {result.percentile_95:.1f}')
        
        # Add key probability markers
        ax.axvline(40, color='green', linestyle='-', alpha=0.5,
                  label=f'P(>40 HRs): {result.prob_over_40:.3f}')
        ax.axvline(50, color='blue', linestyle='-', alpha=0.5,
                  label=f'P(>50 HRs): {result.prob_over_50:.3f}')
        ax.axvline(60, color='purple', linestyle='-', alpha=0.5,
                  label=f'P(>60 HRs): {result.prob_over_60:.3f}')
        
        ax.set_xlabel('Home Runs')
        ax.set_ylabel('Probability Density')
        ax.set_title(title)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        if filename:
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close()
            return filename
        else:
            plt.show()
            return ""
    
    def plot_model_comparison(self, results: Dict[str, SimulationResult], 
                            filename: str = None) -> str:
        """Compare results from different models"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        models = list(results.keys())
        means = [results[model].mean_hrs for model in models]
        prob_40 = [results[model].prob_over_40 for model in models]
        prob_50 = [results[model].prob_over_50 for model in models]
        prob_60 = [results[model].prob_over_60 for model in models]
        
        # Mean home runs comparison
        bars1 = ax1.bar(models, means, alpha=0.7)
        ax1.set_title('Mean Predicted Home Runs by Model')
        ax1.set_ylabel('Home Runs')
        ax1.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar, mean in zip(bars1, means):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    f'{mean:.1f}', ha='center', va='bottom')
        
        # Probability comparisons
        x = np.arange(len(models))
        width = 0.25
        
        bars2 = ax2.bar(x - width, prob_40, width, label='P(>40 HRs)', alpha=0.7)
        bars3 = ax2.bar(x, prob_50, width, label='P(>50 HRs)', alpha=0.7)
        bars4 = ax2.bar(x + width, prob_60, width, label='P(>60 HRs)', alpha=0.7)
        
        ax2.set_title('Probability Comparisons by Model')
        ax2.set_ylabel('Probability')
        ax2.set_xticks(x)
        ax2.set_xticklabels(models, rotation=45)
        ax2.legend()
        
        # Confidence intervals
        conf_low = [results[model].percentile_5 for model in models]
        conf_high = [results[model].percentile_95 for model in models]
        errors = [np.array(conf_high) - np.array(means), 
                 np.array(means) - np.array(conf_low)]
        
        ax3.errorbar(models, means, yerr=errors, fmt='o', capsize=5, capthick=2)
        ax3.set_title('90% Confidence Intervals (5th-95th percentile)')
        ax3.set_ylabel('Home Runs')
        ax3.tick_params(axis='x', rotation=45)
        ax3.grid(True, alpha=0.3)
        
        # Distribution comparison (box plot style)
        distributions = [results[model].distribution for model in models]
        ax4.boxplot(distributions, labels=models)
        ax4.set_title('Distribution Comparison')
        ax4.set_ylabel('Home Runs')
        ax4.tick_params(axis='x', rotation=45)
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if filename:
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close()
            return filename
        else:
            plt.show()
            return ""
    
    def plot_season_progress(self, current_stats: Dict, projections: Dict[str, float],
                           filename: str = None) -> str:
        """Show season progress vs projections"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        games_played = current_stats.get('games_played', 0)
        current_hrs = current_stats.get('home_runs', 0)
        games_remaining = 162 - games_played
        
        # Progress bar style chart
        models = list(projections.keys())
        projected_totals = list(projections.values())
        
        # Calculate pace projections
        if games_played > 0:
            current_pace = current_hrs * (162 / games_played)
        else:
            current_pace = 0
        
        ax1.barh(models + ['Current Pace'], projected_totals + [current_pace], alpha=0.7)
        ax1.axvline(current_hrs, color='red', linestyle='--', linewidth=2,
                   label=f'Current: {current_hrs} HRs')
        ax1.set_title('Season Projections vs Current Performance')
        ax1.set_xlabel('Projected Home Runs')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Season timeline
        games_x = np.arange(1, 163)
        current_line = np.linspace(0, current_pace, 162)
        
        ax2.plot(games_x[:games_played], 
                [current_hrs * (g / games_played) for g in games_x[:games_played]], 
                'ro-', linewidth=3, label='Actual')
        ax2.plot(games_x, current_line, 'r--', alpha=0.5, label='Current Pace')
        
        # Add projection lines
        colors = ['blue', 'green', 'orange', 'purple', 'brown']
        for i, (model, projection) in enumerate(projections.items()):
            if i < len(colors):
                projection_line = np.linspace(current_hrs, projection, games_remaining + 1)
                ax2.plot(games_x[games_played:], projection_line, 
                        color=colors[i], alpha=0.7, label=f'{model}: {projection:.1f}')
        
        ax2.set_title('Season Timeline and Projections')
        ax2.set_xlabel('Games')
        ax2.set_ylabel('Cumulative Home Runs')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if filename:
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close()
            return filename
        else:
            plt.show()
            return ""
    
    def generate_report_plots(self, results: Dict[str, SimulationResult], 
                            current_stats: Dict, output_dir: str = "plots") -> List[str]:
        """Generate all plots for a comprehensive report"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        generated_files = []
        
        # Individual model histograms
        for model_name, result in results.items():
            filename = f"{output_dir}/{model_name}_distribution.png"
            self.plot_distribution_histogram(
                result, 
                f"Aaron Judge HR Prediction - {model_name.replace('_', ' ').title()} Model",
                filename
            )
            generated_files.append(filename)
        
        # Model comparison
        filename = f"{output_dir}/model_comparison.png"
        self.plot_model_comparison(results, filename)
        generated_files.append(filename)
        
        # Season progress
        projections = {model: result.mean_hrs for model, result in results.items()}
        filename = f"{output_dir}/season_progress.png"
        self.plot_season_progress(current_stats, projections, filename)
        generated_files.append(filename)
        
        return generated_files

# Example usage
if __name__ == "__main__":
    # This would normally use real simulation results
    from monte_carlo_simulator import MonteCarloSimulator
    
    simulator = MonteCarloSimulator(num_trials=1000)
    result = simulator.basic_model(hr_per_pa=0.0824)
    
    viz = VisualizationGenerator()
    viz.plot_distribution_histogram(result, "Test Distribution")
