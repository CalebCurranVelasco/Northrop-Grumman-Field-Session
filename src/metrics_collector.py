"""
Metrics Collection System for Robber Tracking Presentation
Collects quantitative data for performance analysis and visualization
"""

import time
import csv
import json
import numpy as np
from pathlib import Path
from datetime import datetime
from collections import defaultdict


class MetricsCollector:
    """
    Collects comprehensive metrics for tracking, prediction, and interception performance
    Exports to CSV for analysis and presentation
    """

    def __init__(self, scenario_name="default", output_dir="metrics_data"):
        self.scenario_name = scenario_name
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Session info
        self.session_start = time.time()
        self.frame_count = 0

        # Tracking metrics
        self.id_switches = []  # [(frame, old_id, new_id, position)]
        self.track_lengths = defaultdict(int)  # {track_id: frame_count}
        self.active_tracks = []  # [(frame, count)]
        self.detection_counts = []  # [(frame, car, police, robber)]

        # Prediction metrics
        self.prediction_errors = []  # [(frame, time_ahead, error_distance)]
        self.robber_positions = []  # [(frame, timestamp, x, y, vx, vy)]
        self.predictions_made = []  # [(frame, timestamp, pred_x, pred_y, time_ahead)]

        # Interception metrics
        self.interception_attempts = []  # [(frame, police_id, success, distance, time)]
        self.police_assignments = []  # [(frame, police_id, can_intercept, time_to_intercept)]

        # Chase outcome (manual recording)
        self.chase_outcome = None  # 'caught', 'escaped', or None
        self.chase_end_time = None  # seconds from start

        # Performance metrics
        self.frame_times = []  # [(frame, processing_time_ms)]
        self.latencies = []  # [(frame, end_to_end_latency_ms)]

        # Ground truth tracking (for prediction accuracy)
        self.ground_truth_positions = {}  # {track_id: [(frame, x, y)]}

        print(f"\n📊 Metrics Collector Initialized")
        print(f"   Scenario: {scenario_name}")
        print(f"   Output: {self.output_dir}")

    # =========================================================================
    # TRACKING METRICS
    # =========================================================================

    def record_frame(self, active_track_ids):
        """Record active tracks for this frame"""
        self.frame_count += 1

        # Track active IDs
        for track_id in active_track_ids:
            self.track_lengths[track_id] += 1

        # Record active track count
        self.active_tracks.append((self.frame_count, len(active_track_ids)))

    def record_id_switch(self, old_id, new_id, position):
        """Record when a track ID changes (quality issue)"""
        self.id_switches.append((
            self.frame_count,
            old_id,
            new_id,
            position[0],
            position[1]
        ))
        print(f"⚠️ ID SWITCH: {old_id} -> {new_id} at frame {self.frame_count}")

    def record_detections(self, num_cars, num_police, num_robber):
        """Record detection counts per frame"""
        self.detection_counts.append((
            self.frame_count,
            num_cars,
            num_police,
            num_robber
        ))

    # =========================================================================
    # PREDICTION METRICS
    # =========================================================================

    def record_robber_position(self, track_id, position, velocity):
        """Record actual robber position for prediction accuracy"""
        timestamp = time.time() - self.session_start
        self.robber_positions.append((
            self.frame_count,
            timestamp,
            position[0],
            position[1],
            velocity[0],
            velocity[1]
        ))

        # Also save to ground truth
        if track_id not in self.ground_truth_positions:
            self.ground_truth_positions[track_id] = []
        self.ground_truth_positions[track_id].append((
            self.frame_count,
            position[0],
            position[1]
        ))

    def record_prediction(self, predicted_position, time_ahead):
        """Record a prediction made"""
        timestamp = time.time() - self.session_start
        self.predictions_made.append((
            self.frame_count,
            timestamp,
            predicted_position[0],
            predicted_position[1],
            time_ahead
        ))

    def calculate_prediction_error(self, track_id, predicted_pos, time_ahead, actual_pos=None):
        """
        Calculate prediction error by comparing predicted position to actual

        If actual_pos is None, will look up ground truth from history
        """
        if actual_pos is None:
            # Try to find actual position from ground truth
            # This requires looking ahead in time, so we'll calculate this in post-processing
            return

        error_distance = np.linalg.norm(np.array(predicted_pos) - np.array(actual_pos))
        self.prediction_errors.append((
            self.frame_count,
            time_ahead,
            error_distance
        ))

    # =========================================================================
    # INTERCEPTION METRICS
    # =========================================================================

    def record_police_assignment(self, police_id, can_intercept, interception_time, interception_point, robber_pos):
        """Record police assignment decision"""
        distance_to_intercept = np.linalg.norm(
            np.array(interception_point) - np.array(robber_pos)
        )

        self.police_assignments.append((
            self.frame_count,
            police_id,
            1 if can_intercept else 0,  # Convert bool to int for CSV
            interception_time if interception_time else -1,
            distance_to_intercept
        ))

    def record_interception_attempt(self, police_id, success, final_distance, time_taken):
        """Record actual interception result"""
        self.interception_attempts.append((
            self.frame_count,
            police_id,
            1 if success else 0,
            final_distance,
            time_taken
        ))

    def record_chase_outcome(self, outcome):
        """
        Record the final outcome of the chase

        Args:
            outcome: 'caught' or 'escaped'
        """
        self.chase_outcome = outcome
        self.chase_end_time = time.time() - self.session_start
        print(f"\n🏁 Chase outcome recorded: {outcome.upper()} at {self.chase_end_time:.1f}s")

    # =========================================================================
    # PERFORMANCE METRICS
    # =========================================================================

    def record_frame_time(self, processing_time_ms):
        """Record frame processing time"""
        self.frame_times.append((self.frame_count, processing_time_ms))

    def record_latency(self, latency_ms):
        """Record end-to-end latency"""
        self.latencies.append((self.frame_count, latency_ms))

    # =========================================================================
    # EXPORT & REPORTING
    # =========================================================================

    def export_all(self):
        """Export all metrics to CSV files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prefix = f"{self.scenario_name}_{timestamp}"

        print(f"\n📁 Exporting metrics...")

        # Export tracking metrics
        self._export_tracking_metrics(prefix)

        # Export prediction metrics
        self._export_prediction_metrics(prefix)

        # Export interception metrics
        self._export_interception_metrics(prefix)

        # Export performance metrics
        self._export_performance_metrics(prefix)

        # Export summary report
        self._export_summary(prefix)

        print(f"✓ Metrics exported to {self.output_dir}")

    def _export_tracking_metrics(self, prefix):
        """Export tracking quality metrics"""
        # ID switches
        if self.id_switches:
            with open(self.output_dir / f"{prefix}_id_switches.csv", 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['frame', 'old_id', 'new_id', 'x', 'y'])
                writer.writerows(self.id_switches)

        # Track lengths
        with open(self.output_dir / f"{prefix}_track_lengths.csv", 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['track_id', 'length_frames'])
            for track_id, length in self.track_lengths.items():
                writer.writerow([track_id, length])

        # Active tracks over time
        with open(self.output_dir / f"{prefix}_active_tracks.csv", 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['frame', 'active_count'])
            writer.writerows(self.active_tracks)

        # Detection counts
        if self.detection_counts:
            with open(self.output_dir / f"{prefix}_detections.csv", 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['frame', 'cars', 'police', 'robber'])
                writer.writerows(self.detection_counts)

    def _export_prediction_metrics(self, prefix):
        """Export prediction accuracy metrics"""
        # Robber positions (ground truth)
        if self.robber_positions:
            with open(self.output_dir / f"{prefix}_robber_positions.csv", 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['frame', 'timestamp', 'x', 'y', 'vx', 'vy'])
                writer.writerows(self.robber_positions)

        # Predictions made
        if self.predictions_made:
            with open(self.output_dir / f"{prefix}_predictions.csv", 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['frame', 'timestamp', 'pred_x', 'pred_y', 'time_ahead'])
                writer.writerows(self.predictions_made)

        # Prediction errors
        if self.prediction_errors:
            with open(self.output_dir / f"{prefix}_prediction_errors.csv", 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['frame', 'time_ahead', 'error_distance'])
                writer.writerows(self.prediction_errors)

    def _export_interception_metrics(self, prefix):
        """Export interception performance metrics"""
        # Police assignments
        if self.police_assignments:
            with open(self.output_dir / f"{prefix}_police_assignments.csv", 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['frame', 'police_id', 'can_intercept', 'time_to_intercept', 'distance'])
                writer.writerows(self.police_assignments)

        # Interception attempts
        if self.interception_attempts:
            with open(self.output_dir / f"{prefix}_interception_attempts.csv", 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['frame', 'police_id', 'success', 'final_distance', 'time_taken'])
                writer.writerows(self.interception_attempts)

    def _export_performance_metrics(self, prefix):
        """Export system performance metrics"""
        # Frame processing times
        if self.frame_times:
            with open(self.output_dir / f"{prefix}_frame_times.csv", 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['frame', 'processing_time_ms'])
                writer.writerows(self.frame_times)

        # Latencies
        if self.latencies:
            with open(self.output_dir / f"{prefix}_latencies.csv", 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['frame', 'latency_ms'])
                writer.writerows(self.latencies)

    def _export_summary(self, prefix):
        """Export summary statistics"""
        duration = time.time() - self.session_start

        # Calculate statistics
        stats = self.get_summary_stats()

        # Export as JSON
        with open(self.output_dir / f"{prefix}_summary.json", 'w') as f:
            json.dump(stats, f, indent=2)

        # Also export as readable text
        with open(self.output_dir / f"{prefix}_summary.txt", 'w') as f:
            f.write(f"{'='*60}\n")
            f.write(f"METRICS SUMMARY: {self.scenario_name}\n")
            f.write(f"{'='*60}\n\n")

            f.write(f"Session Duration: {duration:.1f} seconds\n")
            f.write(f"Total Frames: {self.frame_count}\n")
            f.write(f"Average FPS: {stats['avg_fps']:.1f}\n\n")

            f.write(f"TRACKING QUALITY:\n")
            f.write(f"  ID Switches: {stats['total_id_switches']} ({stats['id_switches_per_min']:.1f}/min)\n")
            f.write(f"  Average Track Length: {stats['avg_track_length']:.1f} frames\n")
            f.write(f"  Average Active Tracks: {stats['avg_active_tracks']:.1f}\n\n")

            if stats['avg_prediction_error'] is not None:
                f.write(f"PREDICTION ACCURACY:\n")
                f.write(f"  Average Error: {stats['avg_prediction_error']:.1f} pixels\n")
                f.write(f"  Total Predictions: {stats['total_predictions']}\n\n")

            if stats['interception_success_rate'] is not None:
                f.write(f"INTERCEPTION PERFORMANCE:\n")
                f.write(f"  Success Rate: {stats['interception_success_rate']:.1%}\n")
                f.write(f"  Average Time to Intercept: {stats['avg_intercept_time']:.1f}s\n\n")

            # Chase outcome
            if stats.get('chase_outcome'):
                f.write(f"CHASE OUTCOME:\n")
                f.write(f"  Result: {stats['chase_outcome'].upper()}\n")
                f.write(f"  Time: {stats.get('chase_end_time', 0):.1f}s\n\n")

            if stats['avg_frame_time'] is not None:
                f.write(f"SYSTEM PERFORMANCE:\n")
                f.write(f"  Average Frame Time: {stats['avg_frame_time']:.1f}ms\n")
                f.write(f"  P95 Frame Time: {stats['p95_frame_time']:.1f}ms\n")

    def get_summary_stats(self):
        """Calculate summary statistics"""
        duration = time.time() - self.session_start

        stats = {
            'scenario_name': self.scenario_name,
            'duration_seconds': duration,
            'total_frames': self.frame_count,
            'avg_fps': self.frame_count / duration if duration > 0 else 0,

            # Chase outcome
            'chase_outcome': self.chase_outcome,
            'chase_end_time': self.chase_end_time,

            # Tracking
            'total_id_switches': len(self.id_switches),
            'id_switches_per_min': len(self.id_switches) / (duration / 60) if duration > 0 else 0,
            'avg_track_length': np.mean(list(self.track_lengths.values())) if self.track_lengths else 0,
            'avg_active_tracks': np.mean([count for _, count in self.active_tracks]) if self.active_tracks else 0,

            # Prediction
            'total_predictions': len(self.predictions_made),
            'avg_prediction_error': np.mean([err for _, _, err in self.prediction_errors]) if self.prediction_errors else None,

            # Interception
            'total_intercept_attempts': len(self.interception_attempts),
            'successful_intercepts': sum(1 for _, _, success, _, _ in self.interception_attempts if success),
            'interception_success_rate': (sum(1 for _, _, success, _, _ in self.interception_attempts if success) / len(self.interception_attempts)) if self.interception_attempts else None,
            'avg_intercept_time': np.mean([t for _, _, _, _, t in self.interception_attempts if t > 0]) if self.interception_attempts else None,

            # Performance
            'avg_frame_time': np.mean([t for _, t in self.frame_times]) if self.frame_times else None,
            'p95_frame_time': np.percentile([t for _, t in self.frame_times], 95) if self.frame_times else None,
        }

        return stats

    def print_live_stats(self):
        """Print current statistics to console"""
        if self.frame_count % 100 == 0 and self.frame_count > 0:
            stats = self.get_summary_stats()

            print(f"\n{'='*60}")
            print(f"📊 LIVE STATS (Frame {self.frame_count})")
            print(f"{'='*60}")
            print(f"  ID Switches: {stats['total_id_switches']} ({stats['id_switches_per_min']:.1f}/min)")
            print(f"  Avg Track Length: {stats['avg_track_length']:.1f} frames")
            print(f"  Active Tracks: {stats['avg_active_tracks']:.1f}")
            if stats['avg_frame_time']:
                print(f"  Frame Time: {stats['avg_frame_time']:.1f}ms (P95: {stats['p95_frame_time']:.1f}ms)")
            print(f"{'='*60}\n")
