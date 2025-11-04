"""
Generate presentation-quality graphs from metrics data
Run this after collecting metrics from test scenarios
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import json
import seaborn as sns

# Set style for presentation-quality plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 12


class MetricsVisualizer:
    """Generate graphs from collected metrics"""

    def __init__(self, metrics_dir="metrics_data"):
        self.metrics_dir = Path(metrics_dir)
        self.output_dir = self.metrics_dir / "graphs"
        self.output_dir.mkdir(exist_ok=True)

    def find_scenario_files(self, scenario_name):
        """Find all CSV files for a given scenario"""
        files = list(self.metrics_dir.glob(f"{scenario_name}_*"))
        return files

    def load_csv(self, filepath):
        """Load CSV file safely"""
        try:
            return pd.read_csv(filepath)
        except Exception as e:
            print(f"⚠️ Could not load {filepath}: {e}")
            return None

    # =========================================================================
    # TRACKING QUALITY GRAPHS
    # =========================================================================

    def plot_id_switches_over_time(self, scenario_name):
        """Plot ID switches over time"""
        filepath = list(self.metrics_dir.glob(f"{scenario_name}_*_id_switches.csv"))
        if not filepath:
            print(f"No ID switch data for {scenario_name}")
            return

        df = self.load_csv(filepath[0])
        if df is None or df.empty:
            return

        plt.figure(figsize=(10, 6))
        plt.plot(df['frame'], range(1, len(df) + 1), 'r-', linewidth=2)
        plt.xlabel('Frame Number')
        plt.ylabel('Cumulative ID Switches')
        plt.title(f'ID Switches Over Time - {scenario_name}')
        plt.grid(True, alpha=0.3)

        output_path = self.output_dir / f"{scenario_name}_id_switches.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_path}")
        plt.close()

    def plot_track_length_distribution(self, scenario_name):
        """Plot distribution of track lengths"""
        filepath = list(self.metrics_dir.glob(f"{scenario_name}_*_track_lengths.csv"))
        if not filepath:
            print(f"No track length data for {scenario_name}")
            return

        df = self.load_csv(filepath[0])
        if df is None or df.empty:
            return

        plt.figure(figsize=(10, 6))
        plt.hist(df['length_frames'], bins=30, color='skyblue', edgecolor='black', alpha=0.7)
        plt.xlabel('Track Length (frames)')
        plt.ylabel('Frequency')
        plt.title(f'Track Length Distribution - {scenario_name}')
        plt.axvline(df['length_frames'].mean(), color='red', linestyle='--',
                   label=f'Mean: {df["length_frames"].mean():.1f} frames')
        plt.legend()
        plt.grid(True, alpha=0.3)

        output_path = self.output_dir / f"{scenario_name}_track_lengths.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_path}")
        plt.close()

    def plot_active_tracks_over_time(self, scenario_name):
        """Plot number of active tracks over time"""
        filepath = list(self.metrics_dir.glob(f"{scenario_name}_*_active_tracks.csv"))
        if not filepath:
            print(f"No active tracks data for {scenario_name}")
            return

        df = self.load_csv(filepath[0])
        if df is None or df.empty:
            return

        plt.figure(figsize=(10, 6))
        plt.plot(df['frame'], df['active_count'], 'b-', linewidth=1.5, alpha=0.7)
        plt.xlabel('Frame Number')
        plt.ylabel('Number of Active Tracks')
        plt.title(f'Active Tracks Over Time - {scenario_name}')
        plt.grid(True, alpha=0.3)

        output_path = self.output_dir / f"{scenario_name}_active_tracks.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_path}")
        plt.close()

    # =========================================================================
    # PREDICTION ACCURACY GRAPHS
    # =========================================================================

    def plot_robber_trajectory(self, scenario_name):
        """Plot actual robber trajectory"""
        filepath = list(self.metrics_dir.glob(f"{scenario_name}_*_robber_positions.csv"))
        if not filepath:
            print(f"No robber position data for {scenario_name}")
            return

        df = self.load_csv(filepath[0])
        if df is None or df.empty:
            return

        plt.figure(figsize=(10, 8))

        # Plot trajectory
        plt.plot(df['x'], df['y'], 'r-', linewidth=2, label='Actual Path', alpha=0.7)

        # Mark start and end
        plt.scatter(df['x'].iloc[0], df['y'].iloc[0], color='green', s=200,
                   marker='o', label='Start', zorder=5)
        plt.scatter(df['x'].iloc[-1], df['y'].iloc[-1], color='red', s=200,
                   marker='X', label='End', zorder=5)

        # Add velocity arrows (sample every 30 frames)
        for i in range(0, len(df), 30):
            plt.arrow(df['x'].iloc[i], df['y'].iloc[i],
                     df['vx'].iloc[i] * 5, df['vy'].iloc[i] * 5,
                     head_width=10, head_length=15, fc='blue', ec='blue', alpha=0.4)

        plt.xlabel('X Position (pixels)')
        plt.ylabel('Y Position (pixels)')
        plt.title(f'Robber Trajectory - {scenario_name}')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.axis('equal')

        output_path = self.output_dir / f"{scenario_name}_trajectory.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_path}")
        plt.close()

    def plot_prediction_errors(self, scenario_name):
        """Plot prediction error vs time ahead"""
        filepath = list(self.metrics_dir.glob(f"{scenario_name}_*_prediction_errors.csv"))
        if not filepath:
            print(f"No prediction error data for {scenario_name}")
            return

        df = self.load_csv(filepath[0])
        if df is None or df.empty:
            return

        # Group by time_ahead
        grouped = df.groupby('time_ahead')['error_distance'].agg(['mean', 'std'])

        plt.figure(figsize=(10, 6))
        plt.errorbar(grouped.index, grouped['mean'], yerr=grouped['std'],
                    fmt='o-', linewidth=2, markersize=8, capsize=5)
        plt.xlabel('Prediction Horizon (seconds)')
        plt.ylabel('Prediction Error (pixels)')
        plt.title(f'Prediction Accuracy vs Time Ahead - {scenario_name}')
        plt.grid(True, alpha=0.3)

        output_path = self.output_dir / f"{scenario_name}_prediction_error.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_path}")
        plt.close()

    # =========================================================================
    # INTERCEPTION PERFORMANCE GRAPHS
    # =========================================================================

    def plot_interception_success_rate(self, scenario_name):
        """Plot interception success rate over time"""
        filepath = list(self.metrics_dir.glob(f"{scenario_name}_*_police_assignments.csv"))
        if not filepath:
            print(f"No police assignment data for {scenario_name}")
            return

        df = self.load_csv(filepath[0])
        if df is None or df.empty:
            return

        # Calculate rolling success rate
        window_size = 50
        df['rolling_success'] = df['can_intercept'].rolling(window=window_size).mean() * 100

        plt.figure(figsize=(10, 6))
        plt.plot(df['frame'], df['rolling_success'], 'g-', linewidth=2)
        plt.xlabel('Frame Number')
        plt.ylabel('Interception Capability (%)')
        plt.title(f'Police Interception Success Rate (Rolling {window_size} frames) - {scenario_name}')
        plt.ylim([0, 105])
        plt.grid(True, alpha=0.3)

        # Add horizontal line at 100%
        plt.axhline(100, color='blue', linestyle='--', alpha=0.5, label='100% Success')
        plt.legend()

        output_path = self.output_dir / f"{scenario_name}_intercept_success.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_path}")
        plt.close()

    def plot_time_to_intercept_distribution(self, scenario_name):
        """Plot distribution of time to intercept"""
        filepath = list(self.metrics_dir.glob(f"{scenario_name}_*_police_assignments.csv"))
        if not filepath:
            print(f"No police assignment data for {scenario_name}")
            return

        df = self.load_csv(filepath[0])
        if df is None or df.empty:
            return

        # Filter out invalid times (-1 means no interception possible)
        valid_times = df[df['time_to_intercept'] >= 0]['time_to_intercept']

        if valid_times.empty:
            print(f"No valid interception times for {scenario_name}")
            return

        plt.figure(figsize=(10, 6))
        plt.hist(valid_times, bins=30, color='lightgreen', edgecolor='black', alpha=0.7)
        plt.xlabel('Time to Intercept (seconds)')
        plt.ylabel('Frequency')
        plt.title(f'Time to Intercept Distribution - {scenario_name}')
        plt.axvline(valid_times.mean(), color='red', linestyle='--',
                   label=f'Mean: {valid_times.mean():.2f}s')
        plt.legend()
        plt.grid(True, alpha=0.3)

        output_path = self.output_dir / f"{scenario_name}_time_to_intercept.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_path}")
        plt.close()

    # =========================================================================
    # PERFORMANCE GRAPHS
    # =========================================================================

    def plot_frame_time_distribution(self, scenario_name):
        """Plot frame processing time distribution"""
        filepath = list(self.metrics_dir.glob(f"{scenario_name}_*_frame_times.csv"))
        if not filepath:
            print(f"No frame time data for {scenario_name}")
            return

        df = self.load_csv(filepath[0])
        if df is None or df.empty:
            return

        plt.figure(figsize=(10, 6))
        plt.hist(df['processing_time_ms'], bins=50, color='orange', edgecolor='black', alpha=0.7)
        plt.xlabel('Processing Time (ms)')
        plt.ylabel('Frequency')
        plt.title(f'Frame Processing Time Distribution - {scenario_name}')

        mean_time = df['processing_time_ms'].mean()
        p95_time = df['processing_time_ms'].quantile(0.95)

        plt.axvline(mean_time, color='blue', linestyle='--', label=f'Mean: {mean_time:.1f}ms')
        plt.axvline(p95_time, color='red', linestyle='--', label=f'P95: {p95_time:.1f}ms')
        plt.legend()
        plt.grid(True, alpha=0.3)

        output_path = self.output_dir / f"{scenario_name}_frame_times.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_path}")
        plt.close()

    # =========================================================================
    # COMPARISON GRAPHS
    # =========================================================================

    def compare_scenarios(self, scenario_names, metric='id_switches'):
        """Compare a metric across multiple scenarios"""
        summaries = []

        for scenario in scenario_names:
            filepath = list(self.metrics_dir.glob(f"{scenario}_*_summary.json"))
            if filepath:
                with open(filepath[0], 'r') as f:
                    summary = json.load(f)
                    summaries.append((scenario, summary))

        if not summaries:
            print("No summary data found for comparison")
            return

        # Create comparison bar chart based on metric
        scenarios = [s[0] for s in summaries]

        if metric == 'id_switches':
            values = [s[1]['id_switches_per_min'] for s in summaries]
            ylabel = 'ID Switches per Minute'
            title = 'Tracking Quality Comparison'
            color = 'salmon'
        elif metric == 'track_length':
            values = [s[1]['avg_track_length'] for s in summaries]
            ylabel = 'Average Track Length (frames)'
            title = 'Track Persistence Comparison'
            color = 'skyblue'
        elif metric == 'fps':
            values = [s[1]['avg_fps'] for s in summaries]
            ylabel = 'Frames Per Second'
            title = 'Performance Comparison'
            color = 'lightgreen'
        else:
            print(f"Unknown metric: {metric}")
            return

        plt.figure(figsize=(10, 6))
        bars = plt.bar(scenarios, values, color=color, edgecolor='black', alpha=0.7)
        plt.ylabel(ylabel)
        plt.title(title)
        plt.xticks(rotation=45, ha='right')
        plt.grid(True, alpha=0.3, axis='y')

        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{value:.1f}',
                    ha='center', va='bottom', fontweight='bold')

        output_path = self.output_dir / f"comparison_{metric}.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_path}")
        plt.close()

    # =========================================================================
    # BATCH GENERATION
    # =========================================================================

    def generate_all_graphs(self, scenario_name):
        """Generate all graphs for a scenario"""
        print(f"\n📊 Generating graphs for: {scenario_name}")
        print("="*60)

        self.plot_id_switches_over_time(scenario_name)
        self.plot_track_length_distribution(scenario_name)
        self.plot_active_tracks_over_time(scenario_name)
        self.plot_robber_trajectory(scenario_name)
        self.plot_prediction_errors(scenario_name)
        self.plot_interception_success_rate(scenario_name)
        self.plot_time_to_intercept_distribution(scenario_name)
        self.plot_frame_time_distribution(scenario_name)

        print(f"\n✓ All graphs saved to: {self.output_dir}")


if __name__ == "__main__":
    import sys

    visualizer = MetricsVisualizer()

    if len(sys.argv) > 1:
        # Generate graphs for specific scenario
        scenario = sys.argv[1]
        visualizer.generate_all_graphs(scenario)
    else:
        # Auto-detect scenarios from metrics_data folder
        print("📁 Detecting scenarios in metrics_data/...")

        # Find all unique scenario names
        files = list(Path("metrics_data").glob("*_summary.json"))
        scenarios = set()
        for f in files:
            # Extract scenario name (everything before first timestamp)
            parts = f.stem.split('_')
            # Find where timestamp starts (looks like YYYYMMDD)
            for i, part in enumerate(parts):
                if part.isdigit() and len(part) == 8:
                    scenario = '_'.join(parts[:i])
                    scenarios.add(scenario)
                    break

        if not scenarios:
            print("❌ No scenarios found. Run metrics collection first!")
            print("\nUsage: python generate_graphs.py [scenario_name]")
        else:
            print(f"Found {len(scenarios)} scenarios: {', '.join(scenarios)}\n")

            # Generate graphs for all scenarios
            for scenario in sorted(scenarios):
                visualizer.generate_all_graphs(scenario)

            # Generate comparison graphs if multiple scenarios
            if len(scenarios) > 1:
                print("\n📊 Generating comparison graphs...")
                visualizer.compare_scenarios(list(scenarios), 'id_switches')
                visualizer.compare_scenarios(list(scenarios), 'track_length')
                visualizer.compare_scenarios(list(scenarios), 'fps')
