"""
Multi-Level Metrics Aggregation

Aggregates test results at two levels:
1. Per-Scenario: Combines 3 trials for each scenario (e.g., TC-BL-sort-trial1,2,3)
2. Overall: Combines all scenarios for each tracker (e.g., all SORT tests)

Usage: python aggregate_metrics.py
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from collections import defaultdict


class MetricsAggregator:
    """Aggregate metrics from multiple test runs"""

    def __init__(self, metrics_dir="metrics_data"):
        self.metrics_dir = Path(metrics_dir)
        self.output_dir = self.metrics_dir / "aggregated"
        self.output_dir.mkdir(exist_ok=True)

    def find_trials(self):
        """
        Find all trials grouped by scenario base

        Returns:
            dict: {scenario_base: {tracker: [trial_files]}}
            Example: {'TC-BL': {'sort': [file1, file2, file3], 'centroid': [...]}}
        """
        files = list(self.metrics_dir.glob("*_summary.json"))
        trials = defaultdict(lambda: defaultdict(list))

        for f in files:
            parts = f.stem.split('_')

            # Find timestamp (YYYYMMDD format)
            for i, part in enumerate(parts):
                if part.isdigit() and len(part) == 8:
                    scenario_full = '_'.join(parts[:i])

                    # Parse: "TC-BL-sort-trial1" -> base="TC-BL", tracker="sort"
                    if '-trial' in scenario_full:
                        scenario_base = '-'.join(scenario_full.split('-trial')[0].split('-')[:-1])
                        tracker = scenario_full.split('-trial')[0].split('-')[-1]
                        trials[scenario_base][tracker].append(f)
                    break

        return trials

    def aggregate_trials(self, scenario_base, tracker, trial_files):
        """
        Aggregate 3 trials for a single scenario+tracker combination

        Args:
            scenario_base: e.g., "TC-BL"
            tracker: "sort" or "centroid"
            trial_files: List of _summary.json files

        Returns:
            dict: Aggregated metrics with mean values
        """
        print(f"  Aggregating {len(trial_files)} trials: {scenario_base}-{tracker}")

        metrics_list = []
        for trial_file in trial_files:
            with open(trial_file, 'r') as f:
                metrics_list.append(json.load(f))

        # Metrics to aggregate
        metrics_to_agg = [
            'duration_seconds',
            'total_frames',
            'avg_fps',
            'id_switches_per_min',
            'avg_track_length',
            'avg_active_tracks',
            'avg_frame_time',
            'p95_frame_time'
        ]

        aggregated = {
            'scenario_base': scenario_base,
            'tracker': tracker,
            'num_trials': len(trial_files),
        }

        # Calculate mean for each metric
        for metric in metrics_to_agg:
            values = [m.get(metric, 0) for m in metrics_list if m.get(metric) is not None]
            if values:
                aggregated[metric] = np.mean(values)

        # Aggregate chase outcomes
        outcomes = [m.get('chase_outcome') for m in metrics_list if m.get('chase_outcome')]
        if outcomes:
            caught_count = sum(1 for o in outcomes if o == 'caught')
            escaped_count = sum(1 for o in outcomes if o == 'escaped')
            aggregated['caught_count'] = caught_count
            aggregated['escaped_count'] = escaped_count
            aggregated['catch_rate'] = caught_count / len(outcomes) if outcomes else 0
        else:
            aggregated['caught_count'] = 0
            aggregated['escaped_count'] = 0
            aggregated['catch_rate'] = None

        return aggregated

    def aggregate_all_scenarios(self, tracker):
        """
        Aggregate all scenarios for a single tracker

        Args:
            tracker: "sort" or "centroid"

        Returns:
            dict: Overall performance across all scenarios
        """
        print(f"\n📊 Aggregating ALL scenarios for {tracker.upper()}")

        # Load all per-scenario averages for this tracker
        per_scenario_files = list(self.output_dir.glob(f"*-{tracker}_avg.json"))

        if not per_scenario_files:
            print(f"  ⚠️ No per-scenario data found for {tracker}")
            return None

        all_metrics = []
        for f in per_scenario_files:
            with open(f, 'r') as file:
                all_metrics.append(json.load(file))

        metrics_to_agg = [
            'avg_fps',
            'id_switches_per_min',
            'avg_track_length',
            'avg_active_tracks',
            'avg_frame_time'
        ]

        overall = {
            'tracker': tracker,
            'num_scenarios': len(all_metrics),
            'scenarios': [m['scenario_base'] for m in all_metrics]
        }

        # Calculate overall mean
        for metric in metrics_to_agg:
            values = [m.get(metric, 0) for m in all_metrics if m.get(metric) is not None]
            if values:
                overall[metric] = np.mean(values)
                overall[f'{metric}_values'] = values  # Keep individual values for graphing

        return overall

    def run_aggregation(self):
        """Run complete aggregation pipeline"""
        print("\n" + "="*70)
        print("📊 MULTI-LEVEL METRICS AGGREGATION")
        print("="*70)

        trials = self.find_trials()

        if not trials:
            print("\n❌ No trial data found!")
            print("Make sure you've run tests with format: SCENARIO-tracker-trialN")
            return

        print(f"\nFound {len(trials)} scenario bases:")
        for scenario_base, trackers in trials.items():
            for tracker, files in trackers.items():
                print(f"  - {scenario_base}-{tracker}: {len(files)} trials")

        # LEVEL 1: Aggregate trials for each scenario+tracker
        print("\n" + "="*70)
        print("LEVEL 1: Per-Scenario Aggregation")
        print("="*70)

        per_scenario_results = []
        for scenario_base, trackers in trials.items():
            for tracker, trial_files in trackers.items():
                if len(trial_files) >= 2:  # Need at least 2 trials to aggregate
                    agg = self.aggregate_trials(scenario_base, tracker, trial_files)
                    per_scenario_results.append(agg)

                    # Save per-scenario average
                    output_file = self.output_dir / f"{scenario_base}-{tracker}_avg.json"
                    with open(output_file, 'w') as f:
                        json.dump(agg, f, indent=2)
                    print(f"    ✓ Saved: {output_file.name}")
                else:
                    print(f"  ⚠️ {scenario_base}-{tracker}: Only {len(trial_files)} trial(s), need 2+ to aggregate")

        # LEVEL 2: Aggregate all scenarios for each tracker
        print("\n" + "="*70)
        print("LEVEL 2: Overall Tracker Performance")
        print("="*70)

        trackers_found = set()
        for trackers in trials.values():
            trackers_found.update(trackers.keys())

        overall_results = {}
        for tracker in trackers_found:
            overall = self.aggregate_all_scenarios(tracker)
            if overall:
                overall_results[tracker] = overall

                # Save overall performance
                output_file = self.output_dir / f"{tracker}_overall.json"
                with open(output_file, 'w') as f:
                    json.dump(overall, f, indent=2)
                print(f"  ✓ Saved: {output_file.name}")

        # Create comparison summary
        self._create_comparison_summary(per_scenario_results, overall_results)

        print("\n" + "="*70)
        print("✅ AGGREGATION COMPLETE!")
        print(f"📁 Results saved to: {self.output_dir}")
        print("="*70)
        print("\nNext step: python generate_graphs_final.py")

    def _create_comparison_summary(self, per_scenario_results, overall_results):
        """Create readable comparison summary"""
        output_file = self.output_dir / "comparison_summary.txt"

        with open(output_file, 'w') as f:
            f.write("="*70 + "\n")
            f.write("METRICS COMPARISON SUMMARY\n")
            f.write("="*70 + "\n\n")

            # Per-scenario comparison
            f.write("PER-SCENARIO AVERAGES:\n")
            f.write("-"*70 + "\n\n")

            # Group by scenario base
            scenarios = defaultdict(dict)
            for result in per_scenario_results:
                scenarios[result['scenario_base']][result['tracker']] = result

            for scenario_base in sorted(scenarios.keys()):
                f.write(f"\n{scenario_base}:\n")
                trackers = scenarios[scenario_base]

                for tracker in ['sort', 'centroid']:
                    if tracker in trackers:
                        data = trackers[tracker]
                        f.write(f"  {tracker.upper()}:\n")
                        f.write(f"    ID Switches/min: {data.get('id_switches_per_min', 0):.2f}\n")
                        f.write(f"    Track Length:    {data.get('avg_track_length', 0):.1f} frames\n")
                        f.write(f"    FPS:             {data.get('avg_fps', 0):.1f}\n")

                        # Chase outcomes
                        if data.get('catch_rate') is not None:
                            f.write(f"    Caught:          {data.get('caught_count', 0)}/{data.get('num_trials', 0)}")
                            f.write(f" ({data.get('catch_rate', 0)*100:.0f}%)\n")

            # Overall comparison
            f.write("\n\n" + "="*70 + "\n")
            f.write("OVERALL TRACKER PERFORMANCE:\n")
            f.write("="*70 + "\n\n")

            for tracker in ['sort', 'centroid']:
                if tracker in overall_results:
                    data = overall_results[tracker]
                    f.write(f"{tracker.upper()} (across {data['num_scenarios']} scenarios):\n")
                    f.write(f"  Average ID Switches/min: {data.get('id_switches_per_min', 0):.2f}\n")
                    f.write(f"  Average Track Length:    {data.get('avg_track_length', 0):.1f} frames\n")
                    f.write(f"  Average FPS:             {data.get('avg_fps', 0):.1f}\n")
                    f.write(f"  Scenarios tested:        {', '.join(data['scenarios'])}\n\n")

            # Calculate improvement
            if 'sort' in overall_results and 'centroid' in overall_results:
                sort_data = overall_results['sort']
                cent_data = overall_results['centroid']

                f.write("\n" + "="*70 + "\n")
                f.write("SORT vs CENTROID IMPROVEMENT:\n")
                f.write("="*70 + "\n\n")

                id_switch_improve = ((cent_data.get('id_switches_per_min', 0) -
                                     sort_data.get('id_switches_per_min', 0)) /
                                     cent_data.get('id_switches_per_min', 1)) * 100

                track_length_improve = ((sort_data.get('avg_track_length', 0) -
                                        cent_data.get('avg_track_length', 0)) /
                                        cent_data.get('avg_track_length', 1)) * 100

                f.write(f"  ID Switches:  {id_switch_improve:+.1f}% (SORT reduced by {abs(id_switch_improve):.1f}%)\n")
                f.write(f"  Track Length: {track_length_improve:+.1f}% (SORT increased by {track_length_improve:.1f}%)\n")

        print(f"\n  ✓ Created comparison summary: {output_file.name}")


if __name__ == "__main__":
    aggregator = MetricsAggregator()
    aggregator.run_aggregation()
