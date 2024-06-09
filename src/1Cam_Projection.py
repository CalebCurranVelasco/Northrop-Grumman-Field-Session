import numpy as np

# Camera intrinsic matrix (K)
K = np.array([[48396.42813690185, 0.0, 1439.4967893921291],
              [0.0, 47060.32894140636, 805.495128297499],
              [0.0, 0.0, 1.0]])

# Camera extrinsic parameters
R = np.eye(3)  # Identity matrix for cam1
T = np.array([0.0, 0.0, 0.0])  # Zero translation for cam1

# Inverse of the intrinsic matrix
K_inv = np.linalg.inv(K)

def project_to_ground_plane(image_points, K_inv, R, T):
    ground_plane_points = []
    for point in image_points:
        u, v = point
        # Convert to normalized coordinates
        normalized_coords = K_inv @ np.array([u, v, 1])
        
        # Compute the ray in camera coordinates
        ray_camera = np.linalg.inv(R) @ normalized_coords
        
        # Intersection with ground plane (z = 0)
        lambda_ = -T[2] / ray_camera[2]  # Tz / ray_z
        X = lambda_ * ray_camera[0] + T[0]
        Y = lambda_ * ray_camera[1] + T[1]
        
        ground_plane_points.append([X, Y, 0])
    
    return np.array(ground_plane_points)

# Example usage
image_points = [(1000, 800), (1200, 900)]  # Replace with your detected 2D points
ground_points = project_to_ground_plane(image_points, K_inv, R, T)
print("3D Points on Ground Plane:", ground_points)
