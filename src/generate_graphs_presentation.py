"""
Generate PRESENTATION-FOCUSED graphs from metrics data
Only creates the most impactful, clear visualizations for your presentation

Usage: python generate_graphs_presentation.py
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import json
import seaborn as sns

# Set style for presentation-quality plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 7)  # Larger for presentation
plt.rcParams['font.size'] = 14  # Bigger font for readability
plt.rcParams['axes.labelsize'] = 16
plt.rcParams['axes.titlesize'] = 18
plt.rcParams['xtick.labelsize'] = 14
plt.rcParams['ytick.labelsize'] = 14
plt.rcParams['legend.fontsize'] = 14


class PresentationGraphs:
    """Generate only the most presentation-worthy graphs"""

    def __init__(self, metrics_dir="metrics_data"):
        self.metrics_dir = Path(metrics_dir)
        self.output_dir = self.metrics_dir / "presentation_graphs"
        self.output_dir.mkdir(exist_ok=True)

    def load_csv(self, filepath):
        """Load CSV file safely"""
        try:
            return pd.read_csv(filepath)
        except Exception as e:
            print(f"⚠️ Could not load {filepath}: {e}")
            return None

    # =========================================================================
    # GRAPH 1: TRACKING QUALITY COMPARISON (Most Important!)
    # =========================================================================

    def plot_tracking_comparison(self, scenario_names):
        """
        Side-by-side comparison of SORT vs Centroid tracking quality
        Shows both ID switches AND track length in one compelling visual
        """
        summaries = []
        for scenario in scenario_names:
            filepath = list(self.metrics_dir.glob(f"{scenario}_*_summary.json"))
            if filepath:
                with open(filepath[0], 'r') as f:
                    summary = json.load(f)
                    summaries.append((scenario, summary))

        if len(summaries) < 2:
            print("⚠️ Need at least 2 scenarios for comparison")
            return

        # Create figure with 2 subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

        scenarios = [s[0] for s in summaries]

        # Subplot 1: ID Switches (Lower is Better)
        id_switches = [s[1]['id_switches_per_min'] for s in summaries]
        colors_switches = ['#FF6B6B' if x > 5 else '#51CF66' for x in id_switches]

        bars1 = ax1.bar(scenarios, id_switches, color=colors_switches,
                       edgecolor='black', linewidth=2, alpha=0.8)
        ax1.set_ylabel('ID Switches per Minute', fontweight='bold')
        ax1.set_title('Tracking Stability\n(Lower is Better)', fontweight='bold', pad=20)
        ax1.set_ylim([0, max(id_switches) * 1.2 if max(id_switches) > 0 else 1])
        ax1.grid(True, alpha=0.3, axis='y')

        # Add value labels on bars
        for bar, value in zip(bars1, id_switches):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{value:.1f}',
                    ha='center', va='bottom', fontweight='bold', fontsize=16)

        # Subplot 2: Track Length (Higher is Better)
        track_lengths = [s[1]['avg_track_length'] for s in summaries]
        colors_length = ['#FF6B6B' if x < 50 else '#51CF66' for x in track_lengths]

        bars2 = ax2.bar(scenarios, track_lengths, color=colors_length,
                       edgecolor='black', linewidth=2, alpha=0.8)
        ax2.set_ylabel('Average Track Length (frames)', fontweight='bold')
        ax2.set_title('Track Persistence\n(Higher is Better)', fontweight='bold', pad=20)
        ax2.grid(True, alpha=0.3, axis='y')

        # Add value labels on bars
        for bar, value in zip(bars2, track_lengths):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{value:.1f}',
                    ha='center', va='bottom', fontweight='bold', fontsize=16)

        # Rotate x-axis labels if needed
        for ax in [ax1, ax2]:
            ax.set_xticklabels(scenarios, rotation=15, ha='right')

        plt.tight_layout()
        output_path = self.output_dir / "1_tracking_quality_comparison.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ GRAPH 1: {output_path}")
        plt.close()

    # =========================================================================
    # GRAPH 2: ROBBER TRAJECTORY (Visual Impact)
    # =========================================================================

    def plot_trajectory_enhanced(self, scenario_name):
        """Enhanced trajectory plot showing the problem complexity"""
        filepath = list(self.metrics_dir.glob(f"{scenario_name}_*_robber_positions.csv"))
        if not filepath:
            print(f"⚠️ No robber position data for {scenario_name}")
            return

        df = self.load_csv(filepath[0])
        if df is None or df.empty:
            return

        plt.figure(figsize=(12, 10))

        # Plot trajectory with gradient color (shows time progression)
        colors = plt.cm.Reds(np.linspace(0.3, 1, len(df)))
        for i in range(len(df) - 1):
            plt.plot(df['x'].iloc[i:i+2], df['y'].iloc[i:i+2],
                    color=colors[i], linewidth=3, alpha=0.7)

        # Mark start and end with large markers
        plt.scatter(df['x'].iloc[0], df['y'].iloc[0], color='green', s=400,
                   marker='o', label='Start', zorder=5, edgecolor='black', linewidth=2)
        plt.scatter(df['x'].iloc[-1], df['y'].iloc[-1], color='red', s=400,
                   marker='X', label='End', zorder=5, edgecolor='black', linewidth=2)

        # Add velocity arrows (every 20 frames for clarity)
        for i in range(0, len(df), 20):
            if abs(df['vx'].iloc[i]) > 5 or abs(df['vy'].iloc[i]) > 5:  # Only if moving
                plt.arrow(df['x'].iloc[i], df['y'].iloc[i],
                         df['vx'].iloc[i] * 8, df['vy'].iloc[i] * 8,
                         head_width=15, head_length=20, fc='blue', ec='blue',
                         alpha=0.5, linewidth=2)

        plt.xlabel('X Position (pixels)', fontweight='bold')
        plt.ylabel('Y Position (pixels)', fontweight='bold')
        plt.title(f'Robber Trajectory - {scenario_name}', fontweight='bold', fontsize=20)
        plt.legend(loc='best', fontsize=14, framealpha=0.9)
        plt.grid(True, alpha=0.3)
        plt.axis('equal')

        output_path = self.output_dir / f"2_trajectory_{scenario_name}.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ GRAPH 2: {output_path}")
        plt.close()

    # =========================================================================
    # GRAPH 3: SYSTEM PERFORMANCE (Real-time Capability)
    # =========================================================================

    def plot_performance_comparison(self, scenario_names):
        """Show FPS and frame time to demonstrate real-time capability"""
        summaries = []
        for scenario in scenario_names:
            filepath = list(self.metrics_dir.glob(f"{scenario}_*_summary.json"))
            if filepath:
                with open(filepath[0], 'r') as f:
                    summary = json.load(f)
                    summaries.append((scenario, summary))

        if not summaries:
            print("⚠️ No summary data found")
            return

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

        scenarios = [s[0] for s in summaries]

        # Subplot 1: FPS
        fps_values = [s[1]['avg_fps'] for s in summaries]
        bars1 = ax1.bar(scenarios, fps_values, color='#4ECDC4',
                       edgecolor='black', linewidth=2, alpha=0.8)
        ax1.set_ylabel('Frames Per Second', fontweight='bold')
        ax1.set_title('System Throughput', fontweight='bold', pad=20)
        ax1.axhline(y=10, color='green', linestyle='--', linewidth=2,
                   label='Real-time Target (10 FPS)', alpha=0.7)
        ax1.grid(True, alpha=0.3, axis='y')
        ax1.legend()

        for bar, value in zip(bars1, fps_values):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{value:.1f}',
                    ha='center', va='bottom', fontweight='bold', fontsize=16)

        # Subplot 2: Processing Time
        frame_times = [s[1]['avg_frame_time'] for s in summaries]
        bars2 = ax2.bar(scenarios, frame_times, color='#FFB347',
                       edgecolor='black', linewidth=2, alpha=0.8)
        ax2.set_ylabel('Processing Time (ms)', fontweight='bold')
        ax2.set_title('Frame Processing Latency', fontweight='bold', pad=20)
        ax2.grid(True, alpha=0.3, axis='y')

        for bar, value in zip(bars2, frame_times):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{value:.1f}ms',
                    ha='center', va='bottom', fontweight='bold', fontsize=14)

        for ax in [ax1, ax2]:
            ax.set_xticklabels(scenarios, rotation=15, ha='right')

        plt.tight_layout()
        output_path = self.output_dir / "3_performance_comparison.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ GRAPH 3: {output_path}")
        plt.close()

    # =========================================================================
    # GRAPH 4: INTERCEPTION SUCCESS (Algorithm Effectiveness)
    # =========================================================================

    def plot_interception_metrics(self, scenario_name):
        """Show interception capability - time to intercept distribution"""
        filepath = list(self.metrics_dir.glob(f"{scenario_name}_*_police_assignments.csv"))
        if not filepath:
            print(f"⚠️ No police assignment data for {scenario_name}")
            return

        df = self.load_csv(filepath[0])
        if df is None or df.empty:
            return

        # Filter valid interception times
        valid_times = df[df['time_to_intercept'] >= 0]['time_to_intercept']

        if valid_times.empty:
            print(f"⚠️ No valid interception times for {scenario_name}")
            return

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

        # Subplot 1: Time to Intercept Distribution
        ax1.hist(valid_times, bins=20, color='#95E1D3', edgecolor='black',
                alpha=0.8, linewidth=1.5)
        ax1.axvline(valid_times.mean(), color='red', linestyle='--', linewidth=3,
                   label=f'Mean: {valid_times.mean():.2f}s')
        ax1.set_xlabel('Time to Intercept (seconds)', fontweight='bold')
        ax1.set_ylabel('Frequency', fontweight='bold')
        ax1.set_title('Interception Speed Distribution', fontweight='bold', fontsize=18)
        ax1.legend(fontsize=14)
        ax1.grid(True, alpha=0.3)

        # Subplot 2: Success Rate Over Time
        window_size = min(50, len(df) // 4)  # Adaptive window
        if window_size > 0:
            df_sorted = df.sort_values('frame')
            df_sorted['rolling_success'] = df_sorted['can_intercept'].rolling(
                window=window_size, min_periods=1).mean() * 100

            ax2.plot(df_sorted['frame'], df_sorted['rolling_success'],
                    color='#38B000', linewidth=3, alpha=0.8)
            ax2.fill_between(df_sorted['frame'], 0, df_sorted['rolling_success'],
                           alpha=0.3, color='#38B000')
            ax2.axhline(100, color='blue', linestyle='--', linewidth=2,
                       alpha=0.5, label='Perfect Success')
            ax2.set_xlabel('Frame Number', fontweight='bold')
            ax2.set_ylabel('Success Rate (%)', fontweight='bold')
            ax2.set_title(f'Interception Success Rate\n(Rolling {window_size} frames)',
                         fontweight='bold', fontsize=18)
            ax2.set_ylim([0, 105])
            ax2.legend()
            ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        output_path = self.output_dir / f"4_interception_{scenario_name}.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ GRAPH 4: {output_path}")
        plt.close()

    # =========================================================================
    # SUMMARY TABLE (For Presentation Slide)
    # =========================================================================

    def create_summary_table(self, scenario_names):
        """Create a clean table summarizing all key metrics"""
        summaries = []
        for scenario in scenario_names:
            filepath = list(self.metrics_dir.glob(f"{scenario}_*_summary.json"))
            if filepath:
                with open(filepath[0], 'r') as f:
                    summary = json.load(f)
                    summaries.append((scenario, summary))

        if not summaries:
            print("⚠️ No summary data found")
            return

        # Create table data
        table_data = []
        for scenario, data in summaries:
            row = [
                scenario,
                f"{data['id_switches_per_min']:.1f}",
                f"{data['avg_track_length']:.1f}",
                f"{data['avg_fps']:.1f}",
                f"{data['avg_frame_time']:.1f}",
                f"{data['duration_seconds']:.1f}s"
            ]
            table_data.append(row)

        # Create figure
        fig, ax = plt.subplots(figsize=(14, 4))
        ax.axis('tight')
        ax.axis('off')

        table = ax.table(cellText=table_data,
                        colLabels=['Scenario', 'ID Switches/min', 'Avg Track Length',
                                  'FPS', 'Frame Time (ms)', 'Duration'],
                        cellLoc='center',
                        loc='center',
                        colWidths=[0.25, 0.15, 0.15, 0.1, 0.15, 0.12])

        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.scale(1, 2.5)

        # Style header
        for i in range(6):
            table[(0, i)].set_facecolor('#4472C4')
            table[(0, i)].set_text_props(weight='bold', color='white')

        # Alternate row colors
        for i in range(1, len(table_data) + 1):
            for j in range(6):
                if i % 2 == 0:
                    table[(i, j)].set_facecolor('#E7E6E6')
                else:
                    table[(i, j)].set_facecolor('#F2F2F2')

        plt.title('Metrics Summary Comparison', fontsize=18, fontweight='bold', pad=20)

        output_path = self.output_dir / "5_summary_table.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ GRAPH 5: {output_path}")
        plt.close()

    # =========================================================================
    # GENERATE ALL PRESENTATION GRAPHS
    # =========================================================================

    def generate_all(self):
        """Generate all presentation-focused graphs"""
        print("\n" + "="*70)
        print("📊 GENERATING PRESENTATION GRAPHS")
        print("="*70)

        # Auto-detect scenarios
        files = list(Path("metrics_data").glob("*_summary.json"))
        scenarios = set()
        for f in files:
            parts = f.stem.split('_')
            for i, part in enumerate(parts):
                if part.isdigit() and len(part) == 8:
                    scenario = '_'.join(parts[:i])
                    scenarios.add(scenario)
                    break

        if not scenarios:
            print("❌ No scenarios found. Run metrics collection first!")
            return

        scenarios = sorted(scenarios)
        print(f"\n📁 Found {len(scenarios)} scenarios: {', '.join(scenarios)}\n")

        # Generate graphs
        print("Generating graphs...\n")

        # Graph 1: Tracking Comparison (MOST IMPORTANT!)
        if len(scenarios) >= 2:
            self.plot_tracking_comparison(scenarios)

        # Graph 2: Trajectory for each scenario
        for scenario in scenarios:
            self.plot_trajectory_enhanced(scenario)

        # Graph 3: Performance Comparison
        self.plot_performance_comparison(scenarios)

        # Graph 4: Interception metrics for primary scenario
        if scenarios:
            primary_scenario = [s for s in scenarios if 'sort' in s.lower()]
            if primary_scenario:
                self.plot_interception_metrics(primary_scenario[0])
            else:
                self.plot_interception_metrics(scenarios[0])

        # Graph 5: Summary Table
        self.create_summary_table(scenarios)

        print("\n" + "="*70)
        print(f"✅ ALL GRAPHS SAVED TO: {self.output_dir}")
        print("="*70)
        print("\n📊 PRESENTATION-READY GRAPHS:")
        print("   1. Tracking Quality Comparison (SORT vs Centroid)")
        print("   2. Robber Trajectory (Shows complexity)")
        print("   3. Performance Comparison (Real-time capability)")
        print("   4. Interception Metrics (Algorithm effectiveness)")
        print("   5. Summary Table (Quick reference)")
        print("\nUse these 5 graphs for your presentation! 🎬\n")


if __name__ == "__main__":
    visualizer = PresentationGraphs()
    visualizer.generate_all()
