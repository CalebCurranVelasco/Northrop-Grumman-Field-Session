import json
import numpy as np
import cv2
import socket

# Specify the file path
file_path = r'C:\Users\Rae\Northrop-Grumman-Field-Session\multical\calibration_current.json'

# Read the JSON data from the file
with open(file_path, 'r') as file:
    calibration_data = json.load(file)

# Extract camera parameters and poses
cameras = calibration_data['cameras']
camera_poses = calibration_data['camera_poses']

# Calculate the baseline (distance between the two cameras)
T1 = np.array(camera_poses['cam1']['T'])
T2 = np.array(camera_poses['cam2_to_cam1']['T'])
baseline = np.linalg.norm(T1 - T2)

def undistort_points(points, K, dist):
    points = np.array(points, dtype=np.float32)
    points = np.expand_dims(points, axis=1)
    undistorted_points = cv2.undistortPoints(points, K, dist, P=K)
    return undistorted_points.reshape(-1, 2)

def pixel_to_world(undistorted_points, K, R, T, Z):
    fx, fy = K[0, 0], K[1, 1]
    cx, cy = K[0, 2], K[1, 2]

    x = (undistorted_points[:, 0] - cx) * Z / fx
    y = (undistorted_points[:, 1] - cy) * Z / fy
    z = Z

    points_camera = np.vstack((x, y, z, np.ones_like(x)))

    # Convert to world coordinates
    RT = np.hstack((R, T.reshape(-1, 1)))
    points_world = RT @ points_camera

    return points_world[:3].T

def compute_disparity(point1, point2):
    # Calculate disparity between two points
    return abs(point1[0] - point2[0])

def calculate_depth(disparity, baseline, fx):
    # Calculate depth from disparity
    if disparity == 0:
        return float('inf')  # Avoid division by zero
    return (baseline * fx) / disparity

def process_point(camera_id, point, Z):
    cam_params = cameras[camera_id]
    cam_pose = camera_poses[camera_id if camera_id == "cam1" else "cam2_to_cam1"]

    # Camera intrinsics
    K = np.array(cam_params['K'])
    dist = np.array(cam_params['dist'][0])

    # Camera pose
    R = np.array(cam_pose['R'])
    T = np.array(cam_pose['T'])

    # Undistort point
    undistorted_points = undistort_points([point], K, dist)

    # Convert to world coordinates
    world_points = pixel_to_world(undistorted_points, K, R, T, Z)
    world_point = world_points[0]  # Extract the first (and only) point

    return world_point

def send_to_unity(camera_id, point1, point2=None, baseline=baseline):
    cam_params1 = cameras['cam1']
    K1 = np.array(cam_params1['K'])
    fx1 = K1[0, 0]

    if point2 is not None:
        # Using stereo vision to calculate depth
        disparity = compute_disparity(point1, point2)
        Z = calculate_depth(disparity, baseline, fx1)
    else:
        # If no stereo point, use a fixed depth value
        Z = 1.0

    world_point = process_point(camera_id, point1, Z)
    data = ' '.join(map(str, world_point))
    # Print the data to test it
    print("World Point Data:", data)
    # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    #    s.connect(('localhost', 65432))  # Match port with Unity script
    #    s.sendall(data.encode('utf-8'))

def read_robber_car_coords(file_path):
    with open(file_path, 'r') as file:
        coords = [list(map(int, line.strip().split(','))) for line in file]
    return coords

# Read the coordinates of the robber car centroids
robber_car_coords_file = "robber_car_coords.txt"
robber_car_coords = read_robber_car_coords(robber_car_coords_file)

# Example usage for a single point from cam1 with corresponding point in cam2
for coord in robber_car_coords
