"""
Final Presentation Graph Generator
Creates clean, professional graphs from aggregated data
NO ERROR BARS - Just clear, easy-to-read comparisons

Usage: python generate_graphs_final.py
"""

import matplotlib.pyplot as plt
import numpy as np
import json
from pathlib import Path
import seaborn as sns

# Presentation-quality styling
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 15
plt.rcParams['axes.labelsize'] = 17
plt.rcParams['axes.titlesize'] = 20
plt.rcParams['xtick.labelsize'] = 14
plt.rcParams['ytick.labelsize'] = 14
plt.rcParams['legend.fontsize'] = 15


class FinalGraphGenerator:
    """Generate final presentation graphs"""

    def __init__(self, aggregated_dir="metrics_data/aggregated"):
        self.agg_dir = Path(aggregated_dir)
        self.output_dir = self.agg_dir / "final_graphs"
        self.output_dir.mkdir(exist_ok=True)

        # Color scheme
        self.colors = {
            'sort': '#51CF66',      # Green (good)
            'centroid': '#FF6B6B'   # Red (needs improvement)
        }

    def load_json(self, filepath):
        """Load JSON file"""
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Could not load {filepath}: {e}")
            return None

    # =========================================================================
    # GRAPH TYPE 1: Per-Scenario Comparisons (6 graphs)
    # =========================================================================

    def create_scenario_comparison(self, scenario_base):
        """
        Create side-by-side comparison for one scenario
        Shows SORT vs Centroid for this specific scenario
        """
        # Load data for both trackers
        sort_file = self.agg_dir / f"{scenario_base}-sort_avg.json"
        cent_file = self.agg_dir / f"{scenario_base}-centroid_avg.json"

        sort_data = self.load_json(sort_file)
        cent_data = self.load_json(cent_file)

        if not sort_data or not cent_data:
            print(f"  ⚠️ Missing data for {scenario_base}")
            return

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

        trackers = ['SORT', 'Centroid']
        colors = [self.colors['sort'], self.colors['centroid']]

        # Subplot 1: ID Switches
        id_switches = [sort_data['id_switches_per_min'], cent_data['id_switches_per_min']]
        bars1 = ax1.bar(trackers, id_switches, color=colors, edgecolor='black', linewidth=2, alpha=0.85, width=0.6)
        ax1.set_ylabel('ID Switches per Minute', fontweight='bold')
        ax1.set_title('Tracking Stability', fontweight='bold', pad=15)
        ax1.grid(True, alpha=0.3, axis='y')

        # Add value labels
        for bar, value in zip(bars1, id_switches):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height * 1.02,
                    f'{value:.1f}',
                    ha='center', va='bottom', fontweight='bold', fontsize=18)

        # Subplot 2: Track Length
        track_lengths = [sort_data['avg_track_length'], cent_data['avg_track_length']]
        bars2 = ax2.bar(trackers, track_lengths, color=colors, edgecolor='black', linewidth=2, alpha=0.85, width=0.6)
        ax2.set_ylabel('Average Track Length (frames)', fontweight='bold')
        ax2.set_title('Track Persistence', fontweight='bold', pad=15)
        ax2.grid(True, alpha=0.3, axis='y')

        # Add value labels
        for bar, value in zip(bars2, track_lengths):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height * 1.02,
                    f'{value:.0f}',
                    ha='center', va='bottom', fontweight='bold', fontsize=18)

        # Add note about trials
        num_trials = sort_data.get('num_trials', 3)
        fig.suptitle(f'{scenario_base} Comparison (Averaged over {num_trials} trials)',
                    fontsize=22, fontweight='bold', y=0.98)

        plt.tight_layout(rect=[0, 0, 1, 0.96])
        output_file = self.output_dir / f"1_scenario_{scenario_base}.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"  ✓ {output_file.name}")
        plt.close()

    # =========================================================================
    # GRAPH TYPE 2: Overall Winner (THE MONEY SHOT!)
    # =========================================================================

    def create_overall_comparison(self):
        """
        THE MOST IMPORTANT GRAPH!
        Shows SORT beats Centroid across all scenarios
        """
        sort_file = self.agg_dir / "sort_overall.json"
        cent_file = self.agg_dir / "centroid_overall.json"

        sort_data = self.load_json(sort_file)
        cent_data = self.load_json(cent_file)

        if not sort_data or not cent_data:
            print("  ⚠️ Missing overall data")
            return

        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(20, 7))

        trackers = ['SORT', 'Centroid']
        colors = [self.colors['sort'], self.colors['centroid']]

        # Plot 1: ID Switches
        id_switches = [sort_data['id_switches_per_min'], cent_data['id_switches_per_min']]
        bars1 = ax1.bar(trackers, id_switches, color=colors, edgecolor='black', linewidth=3, alpha=0.85, width=0.5)
        ax1.set_ylabel('ID Switches / Minute', fontweight='bold', fontsize=18)
        ax1.set_title('Tracking Stability', fontweight='bold', fontsize=20, pad=15)
        ax1.grid(True, alpha=0.3, axis='y')

        for bar, value in zip(bars1, id_switches):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height * 1.05,
                    f'{value:.1f}',
                    ha='center', va='bottom', fontweight='bold', fontsize=22)

        # Plot 2: Track Length
        track_lengths = [sort_data['avg_track_length'], cent_data['avg_track_length']]
        bars2 = ax2.bar(trackers, track_lengths, color=colors, edgecolor='black', linewidth=3, alpha=0.85, width=0.5)
        ax2.set_ylabel('Average Track Length (frames)', fontweight='bold', fontsize=18)
        ax2.set_title('Track Persistence', fontweight='bold', fontsize=20, pad=15)
        ax2.grid(True, alpha=0.3, axis='y')

        for bar, value in zip(bars2, track_lengths):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height * 1.05,
                    f'{value:.0f}',
                    ha='center', va='bottom', fontweight='bold', fontsize=22)

        # Plot 3: FPS (Performance)
        fps_values = [sort_data['avg_fps'], cent_data['avg_fps']]
        bars3 = ax3.bar(trackers, fps_values, color=colors, edgecolor='black', linewidth=3, alpha=0.85, width=0.5)
        ax3.set_ylabel('Frames Per Second', fontweight='bold', fontsize=18)
        ax3.set_title('System Performance', fontweight='bold', fontsize=20, pad=15)
        ax3.grid(True, alpha=0.3, axis='y')

        for bar, value in zip(bars3, fps_values):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height * 1.05,
                    f'{value:.1f}',
                    ha='center', va='bottom', fontweight='bold', fontsize=22)

        # Overall title
        num_scenarios = sort_data['num_scenarios']
        fig.suptitle(f'Overall Performance Comparison Across {num_scenarios} Scenarios',
                    fontsize=24, fontweight='bold', y=0.98)

        plt.tight_layout(rect=[0, 0, 1, 0.96])
        output_file = self.output_dir / "2_OVERALL_WINNER.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"  ✓ {output_file.name} ⭐⭐⭐ (USE THIS IN PRESENTATION!)")
        plt.close()

    # =========================================================================
    # GRAPH TYPE 3: Interception Success Rate (Catch Rate)
    # =========================================================================

    def create_interception_success_graph(self):
        """
        Show catch rate comparison between SORT and Centroid
        Based on manual outcome recording (C/E keys)
        """
        # Load all per-scenario averages
        scenario_files = list(self.agg_dir.glob("*_avg.json"))

        if not scenario_files:
            print("  ⚠️ No scenario data for interception graph")
            return

        # Organize data by scenario
        scenarios = {}
        for f in scenario_files:
            data = self.load_json(f)
            if data and data.get('catch_rate') is not None:
                scenario = data['scenario_base']
                tracker = data['tracker']
                if scenario not in scenarios:
                    scenarios[scenario] = {}
                scenarios[scenario][tracker] = {
                    'catch_rate': data['catch_rate'] * 100,  # Convert to percentage
                    'caught': data.get('caught_count', 0),
                    'total': data.get('num_trials', 0)
                }

        if not scenarios:
            print("  ⚠️ No outcome data recorded (need to press C/E during tests)")
            return

        # Create comparison graph
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))

        scenario_names = sorted(scenarios.keys())
        sort_rates = [scenarios[s].get('sort', {}).get('catch_rate', 0) for s in scenario_names]
        cent_rates = [scenarios[s].get('centroid', {}).get('catch_rate', 0) for s in scenario_names]

        x = np.arange(len(scenario_names))
        width = 0.35

        # Subplot 1: Per-Scenario Catch Rates
        bars1 = ax1.bar(x - width/2, sort_rates, width, label='SORT',
                       color=self.colors['sort'], edgecolor='black', linewidth=2, alpha=0.85)
        bars2 = ax1.bar(x + width/2, cent_rates, width, label='Centroid',
                       color=self.colors['centroid'], edgecolor='black', linewidth=2, alpha=0.85)

        ax1.set_xlabel('Scenario', fontweight='bold', fontsize=16)
        ax1.set_ylabel('Catch Rate (%)', fontweight='bold', fontsize=16)
        ax1.set_title('Robber Catch Success Rate by Scenario', fontweight='bold', fontsize=20, pad=15)
        ax1.set_xticks(x)
        ax1.set_xticklabels(scenario_names, rotation=15, ha='right')
        ax1.set_ylim([0, 110])
        ax1.legend(fontsize=14)
        ax1.grid(True, alpha=0.3, axis='y')

        # Add value labels on bars
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax1.text(bar.get_x() + bar.get_width()/2., height + 2,
                            f'{height:.0f}%',
                            ha='center', va='bottom', fontweight='bold', fontsize=11)

        # Subplot 2: Overall Catch Rate
        # Calculate overall rates
        sort_overall = np.mean([r for r in sort_rates if r > 0]) if any(r > 0 for r in sort_rates) else 0
        cent_overall = np.mean([r for r in cent_rates if r > 0]) if any(r > 0 for r in cent_rates) else 0

        trackers = ['SORT', 'Centroid']
        overall_rates = [sort_overall, cent_overall]
        colors = [self.colors['sort'], self.colors['centroid']]

        bars = ax2.bar(trackers, overall_rates, color=colors, edgecolor='black',
                      linewidth=3, alpha=0.85, width=0.5)
        ax2.set_ylabel('Overall Catch Rate (%)', fontweight='bold', fontsize=16)
        ax2.set_title('Overall Catch Success Rate\n(Averaged Across All Scenarios)', fontweight='bold', fontsize=20, pad=15)
        ax2.set_ylim([0, 110])
        ax2.grid(True, alpha=0.3, axis='y')

        # Add value labels
        for bar, rate in zip(bars, overall_rates):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 2,
                    f'{rate:.1f}%',
                    ha='center', va='bottom', fontweight='bold', fontsize=22)

        plt.tight_layout()
        output_file = self.output_dir / "3_interception_success.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"  ✓ {output_file.name}")
        plt.close()

    # =========================================================================
    # GRAPH TYPE 4: Heatmap (Visual Impact)
    # =========================================================================

    def create_scenario_heatmap(self):
        """
        Create heatmap showing all scenarios × trackers
        Color-coded: Green (good) to Red (bad)
        """
        # Load all per-scenario averages
        scenario_files = list(self.agg_dir.glob("*_avg.json"))

        if not scenario_files:
            print("  ⚠️ No scenario data for heatmap")
            return

        # Organize data
        scenarios = set()
        data_matrix = {'sort': {}, 'centroid': {}}

        for f in scenario_files:
            data = self.load_json(f)
            if data:
                scenario = data['scenario_base']
                tracker = data['tracker']
                scenarios.add(scenario)
                data_matrix[tracker][scenario] = data['id_switches_per_min']

        scenarios = sorted(scenarios)

        # Create matrix for heatmap
        matrix_data = []
        for scenario in scenarios:
            row = [data_matrix['sort'].get(scenario, 0),
                   data_matrix['centroid'].get(scenario, 0)]
            matrix_data.append(row)

        matrix_data = np.array(matrix_data)

        # Create heatmap
        fig, ax = plt.subplots(figsize=(10, len(scenarios) * 1.5 + 2))
        im = ax.imshow(matrix_data, cmap='RdYlGn_r', aspect='auto', vmin=0, vmax=matrix_data.max())

        # Set ticks
        ax.set_xticks([0, 1])
        ax.set_xticklabels(['SORT', 'Centroid'], fontsize=16, fontweight='bold')
        ax.set_yticks(range(len(scenarios)))
        ax.set_yticklabels(scenarios, fontsize=14)

        # Add values in cells
        for i in range(len(scenarios)):
            for j in range(2):
                text = ax.text(j, i, f'{matrix_data[i, j]:.1f}',
                             ha="center", va="center", color="black",
                             fontweight='bold', fontsize=16)

        # Colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('ID Switches / Minute', fontsize=14, fontweight='bold')

        ax.set_title('Tracking Quality Across All Scenarios\n(Lower values = Better)', fontsize=18, fontweight='bold', pad=20)

        plt.tight_layout()
        output_file = self.output_dir / "4_scenario_heatmap.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"  ✓ {output_file.name}")
        plt.close()

    # =========================================================================
    # GENERATE ALL GRAPHS
    # =========================================================================

    def generate_all(self):
        """Generate all final graphs"""
        print("\n" + "="*70)
        print("📊 GENERATING FINAL PRESENTATION GRAPHS")
        print("="*70)

        # Find all scenarios
        scenario_files = list(self.agg_dir.glob("*-sort_avg.json"))
        scenarios = []
        for f in scenario_files:
            data = self.load_json(f)
            if data:
                scenarios.append(data['scenario_base'])

        scenarios = sorted(scenarios)

        if not scenarios:
            print("\n❌ No aggregated data found!")
            print("Run 'python aggregate_metrics.py' first!")
            return

        print(f"\nFound {len(scenarios)} scenarios: {', '.join(scenarios)}")
        print("\nGenerating graphs...\n")

        # Type 1: Individual scenario comparisons
        print("Type 1: Per-Scenario Comparisons")
        for scenario in scenarios:
            self.create_scenario_comparison(scenario)

        # Type 2: Overall winner (MOST IMPORTANT!)
        print("\nType 2: Overall Winner")
        self.create_overall_comparison()

        # Type 3: Interception Success
        print("\nType 3: Interception Success Rate")
        self.create_interception_success_graph()

        print("\n" + "="*70)
        print("✅ GRAPH GENERATION COMPLETE!")
        print(f"📁 Saved to: {self.output_dir}")
        print("="*70)
        print("\n🎬 PRESENTATION-READY GRAPHS:")
        print(f"   • Per-scenario comparisons: {len(scenarios)} graphs")
        print("   • Overall winner: 2_OVERALL_WINNER.png ⭐⭐⭐")
        print("   • Interception success: 3_interception_success.png ⭐⭐")
        print(f"\n📊 Total: {len(scenarios) + 2} graphs ready for your presentation!\n")


if __name__ == "__main__":
    generator = FinalGraphGenerator()
    generator.generate_all()
