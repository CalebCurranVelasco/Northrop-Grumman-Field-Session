"""
Multi-Camera Robber Tracker - CLEAN VERSION FOR PRESENTATION
Implements: Detection, Prediction, and Interception

Simplified architecture focusing on the three core features:
1. DETECTION: YOLOv8 object detection + SORT tracking
2. PREDICTION: Velocity-based linear extrapolation
3. INTERCEPTION: Police pursuit calculation
"""

import cv2
import numpy as np
import asyncio
import time
from ultralytics import YOLO
from sort import Sort
import socket
import json
from metrics_collector import MetricsCollector
from scenario_config import get_scenario_name, print_current_config

# Load the YOLO model
model = YOLO('models/custom_yolo_model_3.0.pt')

# METRICS COLLECTION FLAG
# Set to True to collect metrics, False to disable
COLLECT_METRICS = True

# AUTO-GENERATE SCENARIO NAME from scenario_config.py
SCENARIO_NAME = get_scenario_name("sort")  # Auto-generated based on scenario_config.py

# Network settings
unity_socket_ip = '127.0.0.1'
unity_socket_port = 15000
unity_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Resolution
resolution = (900, 480)


def send_tracking_data(tracking_data, socket, ip, port):
    """Send tracking data with predictions and interceptions to Unity"""
    # Convert to JSON string
    json_message = json.dumps(tracking_data)

    # Send to Unity
    socket.sendto(json_message.encode('utf-8'), (ip, port))

    # Also send legacy format for backward compatibility
    robber = tracking_data['robber']
    legacy_message = f"{int(robber['position'][0])}, {int(robber['position'][1])}, Port: {tracking_data['camera_port']}"
    socket.sendto(legacy_message.encode('utf-8'), (ip, port))


# =============================================================================
# COMPONENT 1: VELOCITY TRACKING (for Prediction)
# =============================================================================
class VelocityTracker:
    """
    Calculates vehicle velocities by tracking position changes over time
    Essential for prediction component
    """

    def __init__(self, history_length=5):
        self.positions = {}      # {track_id: current_position}
        self.timestamps = {}     # {track_id: timestamp}
        self.velocities = {}     # {track_id: velocity_vector}

    def update(self, track_id, position):
        """Update position for a track and calculate velocity"""
        track_id = int(track_id)
        current_time = time.time()

        # Calculate velocity if we have previous position
        if track_id in self.positions and track_id in self.timestamps:
            old_pos = self.positions[track_id]
            old_time = self.timestamps[track_id]
            dt = current_time - old_time

            if dt > 0:
                # Velocity = (new_position - old_position) / time_delta
                self.velocities[track_id] = (position - old_pos) / dt
            else:
                self.velocities[track_id] = np.array([0.0, 0.0])
        else:
            self.velocities[track_id] = np.array([0.0, 0.0])

        # Update position and timestamp
        self.positions[track_id] = position
        self.timestamps[track_id] = current_time

    def get_velocity(self, track_id):
        """Get velocity vector for a track"""
        track_id = int(track_id)
        return self.velocities.get(track_id, np.array([0.0, 0.0]))

    def get_speed(self, track_id):
        """Get speed (magnitude of velocity)"""
        velocity = self.get_velocity(track_id)
        return np.linalg.norm(velocity)

    def cleanup_old_tracks(self, active_track_ids, timeout=2.0):
        """Remove tracks that haven't been seen recently"""
        current_time = time.time()
        to_remove = []

        for track_id in list(self.timestamps.keys()):
            if track_id not in active_track_ids:
                if current_time - self.timestamps[track_id] > timeout:
                    to_remove.append(track_id)

        for track_id in to_remove:
            self.positions.pop(track_id, None)
            self.timestamps.pop(track_id, None)
            self.velocities.pop(track_id, None)


# =============================================================================
# COMPONENT 2: TRACK CLASSIFICATION (for Detection)
# =============================================================================
class TrackClassifier:
    """
    Maps SORT track IDs to vehicle classes (Car, Police, Robber)
    Essential for identifying which vehicles to track
    """

    def __init__(self):
        self.track_classes = {}  # {track_id: class_id}
        self.class_history = {}  # {track_id: [class_ids]} for stability

    def update(self, tracks, detections, class_ids, max_distance=50.0):
        """
        Match SORT tracks to YOLO detections to assign vehicle classes

        Args:
            tracks: SORT output [[x1,y1,x2,y2,track_id], ...]
            detections: YOLO detections [[x1,y1,x2,y2,score], ...]
            class_ids: YOLO class IDs [0=Car, 1=Police-Car, 2=Robber-Car]
        """
        if len(tracks) == 0 or len(detections) == 0:
            return

        # Build cost matrix based on centroid distance
        cost_matrix = np.zeros((len(tracks), len(detections)))

        for i, track in enumerate(tracks):
            x1, y1, x2, y2, track_id = track
            track_centroid = np.array([(x1+x2)/2, (y1+y2)/2])

            for j, det in enumerate(detections):
                det_centroid = np.array([(det[0]+det[2])/2, (det[1]+det[3])/2])
                distance = np.linalg.norm(track_centroid - det_centroid)
                cost_matrix[i, j] = distance

        # Assign classes based on closest detection
        for i, track in enumerate(tracks):
            track_id = int(track[4])
            closest_det_idx = np.argmin(cost_matrix[i])
            min_distance = cost_matrix[i, closest_det_idx]

            if min_distance < max_distance:
                assigned_class = class_ids[closest_det_idx]

                # Update class history for stability (reduces flickering)
                if track_id not in self.class_history:
                    self.class_history[track_id] = []
                self.class_history[track_id].append(assigned_class)

                # Keep last 5 classifications
                if len(self.class_history[track_id]) > 5:
                    self.class_history[track_id].pop(0)

                # Use most common class in history
                from collections import Counter
                most_common = Counter(self.class_history[track_id]).most_common(1)[0][0]
                self.track_classes[track_id] = most_common

    def get_class(self, track_id):
        """Get vehicle class for a track ID (0=Car, 1=Police, 2=Robber)"""
        return self.track_classes.get(int(track_id), 0)

    def is_police(self, track_id):
        """Check if track is a police car"""
        return self.get_class(track_id) == 1

    def is_robber(self, track_id):
        """Check if track is the robber car"""
        return self.get_class(track_id) == 2

    def get_police_tracks(self, active_track_ids):
        """Get list of track IDs that are police cars"""
        return [tid for tid in active_track_ids if self.is_police(tid)]

    def get_robber_track(self, active_track_ids):
        """Get robber track ID (returns None if not found)"""
        robbers = [tid for tid in active_track_ids if self.is_robber(tid)]
        return robbers[0] if robbers else None

    def cleanup_old_tracks(self, active_track_ids):
        """Remove classifications for inactive tracks"""
        to_remove = []
        for track_id in self.track_classes.keys():
            if track_id not in active_track_ids:
                to_remove.append(track_id)

        for track_id in to_remove:
            self.track_classes.pop(track_id, None)
            self.class_history.pop(track_id, None)


# =============================================================================
# COMPONENT 3: PREDICTOR (Prediction)
# =============================================================================
class Predictor:
    """
    Predicts future vehicle positions using velocity-based linear extrapolation
    This is the PREDICTION component
    """

    def __init__(self, prediction_horizon=3.0, num_points=10):
        """
        Args:
            prediction_horizon: How many seconds ahead to predict (default 3.0)
            num_points: Number of points in predicted path (default 10)
        """
        self.prediction_horizon = prediction_horizon
        self.num_points = num_points

    def predict_position(self, current_pos, velocity, time_ahead):
        """
        Simple linear prediction: future_pos = current_pos + velocity * time

        Args:
            current_pos: np.array([x, y])
            velocity: np.array([vx, vy]) in pixels/second
            time_ahead: seconds into the future

        Returns:
            np.array([x, y]) predicted position
        """
        return current_pos + (velocity * time_ahead)

    def predict_path(self, current_pos, velocity):
        """
        Generate predicted path as series of future positions

        Returns:
            List of [x, y] positions along predicted path
        """
        path = []
        time_step = self.prediction_horizon / self.num_points

        for i in range(self.num_points):
            time_ahead = time_step * (i + 1)
            future_pos = self.predict_position(current_pos, velocity, time_ahead)
            path.append(future_pos.tolist())

        return path


# =============================================================================
# COMPONENT 4: INTERCEPTION CALCULATOR (Interception)
# =============================================================================
class InterceptionCalculator:
    """
    Calculates optimal interception points for police cars to intercept robber
    This is the INTERCEPTION component
    """

    def __init__(self, predictor):
        self.predictor = predictor

    def calculate_interception_point(self, robber_pos, robber_vel, police_pos, police_vel):
        """
        Calculate where and when police car should intercept robber

        Algorithm:
        1. Generate robber's predicted path
        2. For each point on path, check if police can reach it in time
        3. Return earliest reachable interception point

        Returns:
            dict with:
                - 'point': np.array([x, y]) interception point
                - 'time': float seconds until interception
                - 'reachable': bool whether interception is possible
        """
        robber_speed = np.linalg.norm(robber_vel)
        police_speed = np.linalg.norm(police_vel)

        # If robber is stationary, intercept at current position
        if robber_speed < 1.0:
            distance = np.linalg.norm(robber_pos - police_pos)
            time_to_reach = distance / police_speed if police_speed > 1.0 else None
            return {
                'point': robber_pos,
                'time': time_to_reach,
                'reachable': True
            }

        # If police is stationary, cannot intercept
        if police_speed < 1.0:
            return {
                'point': robber_pos,
                'time': None,
                'reachable': False
            }

        # Generate robber's predicted path
        robber_path = self.predictor.predict_path(robber_pos, robber_vel)
        time_step = self.predictor.prediction_horizon / self.predictor.num_points

        # Find earliest point where police can intercept
        for i, future_robber_pos in enumerate(robber_path):
            future_robber_pos = np.array(future_robber_pos)
            time_to_point = time_step * (i + 1)

            # Distance police needs to travel
            police_distance = np.linalg.norm(future_robber_pos - police_pos)

            # Time police needs to travel
            police_time = police_distance / police_speed

            # Can police reach this point before/when robber does?
            if police_time <= time_to_point * 1.0:  # Exact timing (no margin)
                return {
                    'point': future_robber_pos,
                    'time': time_to_point,
                    'reachable': True
                }

        # No reachable interception point found
        return {
            'point': np.array(robber_path[-1]),
            'time': self.predictor.prediction_horizon,
            'reachable': False
        }

    def assign_police_to_robber(self, robber_pos, robber_vel, police_data):
        """
        Assign all police cars to pursue the robber

        Args:
            robber_pos: np.array([x, y])
            robber_vel: np.array([vx, vy])
            police_data: dict {track_id: {'pos': np.array, 'vel': np.array}}

        Returns:
            dict {track_id: interception_result}
        """
        assignments = {}

        for police_id, data in police_data.items():
            police_pos = data['pos']
            police_vel = data['vel']

            interception = self.calculate_interception_point(
                robber_pos, robber_vel, police_pos, police_vel
            )

            assignments[police_id] = interception

        return assignments


# =============================================================================
# MAIN CAMERA HANDLER
# =============================================================================
class CameraHandler:
    """Handles multi-camera video streams with SORT tracking"""

    def __init__(self):
        self.buffers = {}
        self.expected_chunks = {}
        self.camera_views = {}

        # SORT trackers (one per camera)
        self.trackers = {}

        # Velocity trackers (one per camera)
        self.velocity_trackers = {}

        # Track classifiers (one per camera)
        self.track_classifiers = {}

        # Predictor for future position estimation
        self.predictor = Predictor(prediction_horizon=3.0, num_points=10)

        # Interception calculator
        self.interception_calc = InterceptionCalculator(self.predictor)

        # Rate limiting
        self.last_sent_time = {}
        self.send_interval = 0.1  # Max 10 messages/sec

        # Metrics collector
        self.metrics = MetricsCollector(scenario_name=SCENARIO_NAME) if COLLECT_METRICS else None
        self.frame_start_time = None
        self.last_export_time = time.time()  # Track last metrics export time

        # Display
        self.window_size = resolution
        self.current_camera_index = 0
        cv2.namedWindow("Camera 1", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Camera 1", *self.window_size)
        cv2.namedWindow("Camera 2", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Camera 2", *self.window_size)

    def process_data(self, data, addr, port):
        """Process incoming camera data"""

        # Initialize camera if first time
        if addr not in self.buffers:
            self.buffers[addr] = []
            self.expected_chunks[addr] = None

            # Create SORT tracker for this camera
            self.trackers[addr] = Sort(max_age=20, min_hits=2, iou_threshold=0.2)

            # Create velocity tracker for this camera
            self.velocity_trackers[addr] = VelocityTracker()

            # Create track classifier for this camera
            self.track_classifiers[addr] = TrackClassifier()

        # Handle chunked data reception
        if self.expected_chunks[addr] is None:
            if len(data) == 4:
                self.expected_chunks[addr] = int.from_bytes(data, byteorder='little')
                self.buffers[addr] = [None] * self.expected_chunks[addr]
            return

        if len(data) < 4:
            return

        chunk_index = int.from_bytes(data[:4], byteorder='little')
        if chunk_index >= self.expected_chunks[addr]:
            return

        self.buffers[addr][chunk_index] = data[4:]

        # Process complete frame
        if all(self.buffers[addr]):
            full_data = b''.join(self.buffers[addr])
            self.buffers[addr] = [None] * self.expected_chunks[addr]
            self.expected_chunks[addr] = None

            nparr = np.frombuffer(full_data, np.uint8)
            img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img_np is not None:
                # Start timing for metrics
                if self.metrics:
                    self.frame_start_time = time.time()

                img_np = cv2.resize(img_np, self.window_size)
                self.camera_views[addr] = img_np

                # === DETECTION: Run YOLO + SORT ===
                results = model(img_np, conf=0.4)

                # Prepare detections for SORT
                detections = []
                class_ids = []

                for result in results[0].boxes.data:
                    x1, y1, x2, y2, score, class_id = result
                    detections.append([float(x1), float(y1), float(x2), float(y2), float(score)])
                    class_ids.append(int(class_id))

                detections_np = np.array(detections) if detections else np.empty((0, 5))

                # Update SORT tracker
                tracks = self.trackers[addr].update(detections_np)

                # Update velocities for all tracks
                active_track_ids = set()
                for track in tracks:
                    x1, y1, x2, y2, track_id = track
                    track_id = int(track_id)
                    active_track_ids.add(track_id)

                    # Calculate centroid
                    centroid = np.array([float((x1+x2)/2), float((y1+y2)/2)])

                    # Update velocity tracker
                    self.velocity_trackers[addr].update(track_id, centroid)

                # Update track classifier
                self.track_classifiers[addr].update(tracks, detections_np, class_ids)

                # Cleanup old tracks
                self.velocity_trackers[addr].cleanup_old_tracks(active_track_ids)
                self.track_classifiers[addr].cleanup_old_tracks(active_track_ids)

                # === METRICS: Record tracking data ===
                if self.metrics:
                    self.metrics.record_frame(active_track_ids)

                    # Count detections by class
                    num_cars = sum(1 for c in class_ids if c == 0)
                    num_police = sum(1 for c in class_ids if c == 1)
                    num_robber = sum(1 for c in class_ids if c == 2)
                    self.metrics.record_detections(num_cars, num_police, num_robber)

                # === PREDICTION & INTERCEPTION ===
                tracking_data = self._process_prediction_and_interception(active_track_ids, addr, port)

                # === VISUALIZATION ===
                self._draw_tracks(img_np, tracks, addr)

                if tracking_data:
                    self._draw_predictions(img_np, tracking_data)

                # === METRICS: Record frame time ===
                if self.metrics and self.frame_start_time:
                    frame_time_ms = (time.time() - self.frame_start_time) * 1000
                    self.metrics.record_frame_time(frame_time_ms)
                    self.metrics.print_live_stats()

                # === AUTO-EXPORT METRICS every 60 seconds ===
                if self.metrics:
                    current_time = time.time()
                    if current_time - self.last_export_time > 60:
                        print("\n⏰ Auto-exporting metrics (60 second interval)...")
                        self.metrics.export_all()
                        self.last_export_time = current_time

    def _process_prediction_and_interception(self, active_track_ids, addr, port):
        """
        Calculate predictions and interceptions, then send to Unity

        Returns:
            dict: tracking_data with predictions and interceptions (or None)
        """
        current_time = time.time()

        # Rate limiting
        if addr in self.last_sent_time and \
           current_time - self.last_sent_time[addr] < self.send_interval:
            return None

        # Get robber track
        robber_id = self.track_classifiers[addr].get_robber_track(active_track_ids)
        if robber_id is None:
            return None

        # Get police tracks
        police_ids = self.track_classifiers[addr].get_police_tracks(active_track_ids)
        if not police_ids:
            return None

        # Get robber data
        robber_pos = self.velocity_trackers[addr].positions.get(robber_id)
        robber_vel = self.velocity_trackers[addr].get_velocity(robber_id)

        if robber_pos is None:
            return None

        # === PREDICTION: Generate robber predicted path ===
        robber_predicted_path = self.predictor.predict_path(robber_pos, robber_vel)

        # Gather police data
        police_data = {}
        for pid in police_ids:
            pos = self.velocity_trackers[addr].positions.get(pid)
            vel = self.velocity_trackers[addr].get_velocity(pid)
            if pos is not None:
                police_data[pid] = {'pos': pos, 'vel': vel}

        if not police_data:
            return None

        # === INTERCEPTION: Calculate interception points ===
        interceptions = self.interception_calc.assign_police_to_robber(
            robber_pos, robber_vel, police_data
        )

        # Prepare data for Unity
        tracking_data = {
            'robber': {
                'id': int(robber_id),
                'position': robber_pos.tolist(),
                'velocity': robber_vel.tolist(),
                'speed': float(np.linalg.norm(robber_vel)),
                'predicted_path': robber_predicted_path
            },
            'police': [],
            'camera_port': port
        }

        # Add police data with interception points
        for pid in police_data.keys():
            interception = interceptions[pid]
            police_entry = {
                'id': int(pid),
                'position': police_data[pid]['pos'].tolist(),
                'velocity': police_data[pid]['vel'].tolist(),
                'speed': float(np.linalg.norm(police_data[pid]['vel'])),
                'interception_point': interception['point'].tolist(),
                'interception_time': float(interception['time']) if interception['time'] else None,
                'can_intercept': interception['reachable']
            }
            tracking_data['police'].append(police_entry)

        # === METRICS: Record prediction and interception data ===
        if self.metrics:
            # Record robber position for prediction accuracy
            self.metrics.record_robber_position(robber_id, robber_pos, robber_vel)

            # Record predictions
            for point in robber_predicted_path:
                self.metrics.record_prediction(point, self.predictor.prediction_horizon)

            # Record police assignments
            for pid in police_data.keys():
                interception = interceptions[pid]
                self.metrics.record_police_assignment(
                    pid,
                    interception['reachable'],
                    interception['time'],
                    interception['point'],
                    robber_pos
                )

        # Print report
        self._print_interception_report(tracking_data)

        # Send to Unity
        send_tracking_data(tracking_data, unity_socket, unity_socket_ip, unity_socket_port)
        self.last_sent_time[addr] = current_time
        print(f"✓ Sent tracking data to Unity (SORT)")

        return tracking_data

    def _draw_tracks(self, img, tracks, addr):
        """Draw tracking visualization with color-coded vehicle classes"""
        for track in tracks:
            x1, y1, x2, y2, track_id = track
            track_id = int(track_id)

            # Get velocity
            speed = self.velocity_trackers[addr].get_speed(track_id)
            velocity = self.velocity_trackers[addr].get_velocity(track_id)

            # Get vehicle class and assign color
            vehicle_class = self.track_classifiers[addr].get_class(track_id)
            if vehicle_class == 2:  # Robber
                color = (0, 0, 255)  # Red
                label = "ROBBER"
            elif vehicle_class == 1:  # Police
                color = (255, 0, 0)  # Blue
                label = "POLICE"
            else:  # Regular car
                color = (0, 255, 0)  # Green
                label = "CAR"

            # Draw bounding box
            cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)

            # Draw centroid
            centroid = (int((x1+x2)/2), int((y1+y2)/2))
            cv2.circle(img, centroid, 4, color, -1)

            # Draw ID, class, and speed
            text = f"{label} {track_id} ({speed:.1f}px/s)"
            cv2.putText(img, text, (centroid[0] - 10, centroid[1] - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            # Draw velocity arrow
            if speed > 5:
                arrow_end = (int(centroid[0] + velocity[0] * 0.1),
                           int(centroid[1] + velocity[1] * 0.1))
                cv2.arrowedLine(img, centroid, arrow_end, color, 2)

    def _draw_predictions(self, img, tracking_data):
        """
        Draw predicted paths and interception points
        - Red line: Robber's predicted path
        - Blue lines: Police paths to interception points
        - Stars: Interception points
        """
        robber = tracking_data['robber']

        # Draw robber's predicted path (red line)
        path_points = robber['predicted_path']
        for i in range(len(path_points) - 1):
            pt1 = (int(path_points[i][0]), int(path_points[i][1]))
            pt2 = (int(path_points[i+1][0]), int(path_points[i+1][1]))
            cv2.line(img, pt1, pt2, (0, 0, 255), 2)

        # Draw circle at end of predicted path
        if path_points:
            end_point = (int(path_points[-1][0]), int(path_points[-1][1]))
            cv2.circle(img, end_point, 8, (0, 0, 255), 2)

        # Draw police interception paths
        for police in tracking_data['police']:
            police_pos = police['position']
            intercept_point = police['interception_point']

            # Blue if can intercept, gray otherwise
            color = (255, 0, 0) if police['can_intercept'] else (100, 100, 100)

            # Draw line from police to interception point
            pt1 = (int(police_pos[0]), int(police_pos[1]))
            pt2 = (int(intercept_point[0]), int(intercept_point[1]))
            cv2.line(img, pt1, pt2, color, 2)

            # Draw star at interception point
            cv2.drawMarker(img, pt2, color, cv2.MARKER_STAR, 12, 2)

            # Draw label with police ID and time
            if police['can_intercept'] and police['interception_time'] is not None:
                label = f"P{police['id']} {police['interception_time']:.1f}s"
            else:
                label = f"P{police['id']}"
            cv2.putText(img, label, (pt2[0] + 10, pt2[1] - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

    def _print_interception_report(self, data):
        """Print interception report"""
        robber = data['robber']
        print(f"\n🎯 INTERCEPTION REPORT")
        print(f"   Robber ID {robber['id']} at ({robber['position'][0]:.0f}, {robber['position'][1]:.0f}), speed: {robber['speed']:.1f}px/s")

        for police in data['police']:
            status = "✓" if police['can_intercept'] else "✗"
            time_str = f"{police['interception_time']:.1f}s" if police['interception_time'] else "N/A"
            print(f"   Police ID {police['id']}: {status} in {time_str} at ({police['interception_point'][0]:.0f}, {police['interception_point'][1]:.0f})")

    async def image_display(self):
        """Display camera feeds"""
        last_frames = {addr: np.zeros((*self.window_size[::-1], 3), dtype=np.uint8)
                      for addr in self.camera_views}

        while True:
            if self.camera_views:
                for i, addr in enumerate(self.camera_views.keys()):
                    if addr in self.camera_views:
                        last_frames[addr] = self.camera_views[addr]
                    if i == self.current_camera_index:
                        cv2.imshow(f"Camera {i + 1}", self.camera_views[addr])
                    else:
                        cv2.imshow(f"Camera {i + 1}", last_frames[addr])

                self.current_camera_index = (self.current_camera_index + 1) % len(self.camera_views)

            key = cv2.waitKey(1) & 0xFF

            if key == 27:  # ESC to exit
                break
            elif key == ord('c') or key == ord('C'):  # C for Caught
                if self.metrics:
                    self.metrics.record_chase_outcome('caught')
                print("\n✓ Marked as CAUGHT - Press ESC to exit and save")
            elif key == ord('e') or key == ord('E'):  # E for Escaped
                if self.metrics:
                    self.metrics.record_chase_outcome('escaped')
                print("\n✓ Marked as ESCAPED - Press ESC to exit and save")

            await asyncio.sleep(0.1)
            time.sleep(0.1)

        cv2.destroyAllWindows()

        # Export metrics when exiting
        if self.metrics:
            print("\n📊 Exporting final metrics...")
            self.metrics.export_all()
            print("✓ Metrics saved! Run 'python generate_graphs.py' to create visualizations")


class UDPServerProtocol:
    """UDP protocol handler for camera streams"""

    def __init__(self, camera_handler, port):
        self.camera_handler = camera_handler
        self.port = port

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        self.camera_handler.process_data(data, addr, self.port)


async def main():
    """Main async loop"""
    camera_handler = CameraHandler()
    loop = asyncio.get_running_loop()

    # Start UDP servers for each camera
    ports = [8081, 8082]
    tasks = []
    for port in ports:
        listen = loop.create_datagram_endpoint(
            lambda p=port: UDPServerProtocol(camera_handler, p),
            local_addr=('0.0.0.0', port)
        )
        transport, protocol = await listen
        tasks.append(transport)

    print_current_config()  # Show scenario and trial info
    print("="*60)
    print("Multi-Camera Robber Tracker - SORT VERSION")
    print("="*60)
    print(f"✓ Scenario: {SCENARIO_NAME}")
    print("✓ Listening for camera data on ports 8081, 8082")
    print("✓ Detection: YOLOv8 + SORT Tracker")
    print("✓ Prediction: Linear extrapolation (3 seconds)")
    print("✓ Interception: Pursuit algorithm")
    print("✓ Metrics auto-export every 60 seconds")
    print("\nKEYBOARD CONTROLS:")
    print("  C = Record CAUGHT (robber intercepted)")
    print("  E = Record ESCAPED (robber got away)")
    print("  ESC = Exit and save metrics")
    print("="*60)

    await asyncio.gather(camera_handler.image_display())

    unity_socket.close()


if __name__ == "__main__":
    asyncio.run(main())
