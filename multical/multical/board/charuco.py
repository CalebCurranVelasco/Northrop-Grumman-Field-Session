from multical.board.board import Board
from pprint import pformat
import cv2
import numpy as np
from .common import *
import yaml


from structs.struct import struct, choose, subset
from multical.optimization.parameters import Parameters

def load_boards_from_yaml(filename):
    with open(filename, 'r') as file:
        config = yaml.safe_load(file)
    return config['boards']

yaml_filename = 'example_boards/charuco_16x22.yaml'
boards_config = load_boards_from_yaml(yaml_filename)

print(boards_config)  # This should print both charuco_1 and charuco_2 with their respective properties

class CharucoBoard(Parameters, Board):
    def __init__(self, name, size, square_length, marker_length, min_rows=3, min_points=20, 
                 adjusted_points=None, aruco_params=None, aruco_dict='4X4_100', aruco_offset=0):
        
        self.name = name  # Add the name parameter
        self.aruco_dict = aruco_dict
        self.aruco_offset = aruco_offset 
        self.size = tuple(size)
        self.marker_length = marker_length
        self.square_length = square_length
        self.adjusted_points = choose(adjusted_points, self.points) 
        self.aruco_params = aruco_params or {}
        self.min_rows = min_rows
        self.min_points = min_points

    @property
    def board(self):
        aruco_dict = create_dict(self.aruco_dict, self.aruco_offset)
        width, height = self.size
        return cv2.aruco.CharucoBoard_create(width, height, self.square_length, self.marker_length, aruco_dict)
    

    @property
    def aruco_config(self):
        return aruco_config(self.aruco_params)  

    def export(self):
        return struct(
            type='charuco',
            name=self.name,  # Include the name in the export
            aruco_dict=self.aruco_dict,
            aruco_offset=self.aruco_offset,
            size=self.size,
            num_ids=len(self.board.ids),
            marker_length=self.marker_length,
            square_length=self.square_length,
            aruco_params=self.aruco_params
        )

    def __eq__(self, other):
        return self.export() == other.export()

    @property
    def points(self):
        return self.board.chessboardCorners
  
    @property
    def num_points(self):
        return len(self.points)

    @property 
    def ids(self):
        return np.arange(self.num_points)

    @property
    def mesh(self):
        return grid_mesh(self.adjusted_points, self.size)

    @property
    def size_mm(self):
        square_length = int(self.square_length * 1000)
        return [dim * square_length for dim in self.size]

    def draw(self, pixels_mm=1, margin=20):
        square_length = int(self.square_length * 1000 * pixels_mm)
        image_size = [dim * square_length for dim in self.size]
        return self.board.draw(tuple(image_size), marginSize=margin)

    def __str__(self):
        d = self.export()
        return "CharucoBoard " + pformat(d)

    def __repr__(self):
        return self.__str__()      

    def detect(self, image):    
        corners, ids, _ = cv2.aruco.detectMarkers(image, self.board.dictionary, parameters=aruco_config(self.aruco_params))     
        if ids is None: return empty_detection

        _, corners, ids = cv2.aruco.interpolateCornersCharuco(corners, ids, image, self.board)
        if ids is None: return empty_detection
        return struct(corners=corners.squeeze(1), ids=ids.squeeze(1))

    def has_min_detections(self, detections):
        return has_min_detections_grid(self.size, detections.ids, min_points=self.min_points, min_rows=self.min_rows)

    def estimate_pose_points(self, camera, detections):
        return estimate_pose_points(self, camera, detections)

    @property
    def params(self):
        return self.adjusted_points

    def with_params(self, params):
        return self.copy(adjusted_points=params)

    def copy(self, **k):
        d = self.__getstate__()
        d.update(k)
        return CharucoBoard(**d)

    def __getstate__(self):
        return subset(self.__dict__, ['name', 'size', 'adjusted_points', 'aruco_params', 
                                      'marker_length', 'square_length', 'min_rows', 'min_points',
                                      'aruco_dict', 'aruco_offset'])
    
def create_boards_from_config(boards_config):
    boards = {}
    for board_name, board_info in boards_config.items():
        board = CharucoBoard(
            name=board_name,
            size=board_info['size'],
            square_length=board_info['square_length'],
            marker_length=board_info['marker_length'],
            min_rows=board_info.get('min_rows', 3),
            min_points=board_info.get('min_points', 20),
            aruco_dict=board_info.get('aruco_dict', '4X4_1000')
        )
        boards[board_name] = board
    return boards

boards = create_boards_from_config(boards_config)
print(boards)  # This should show two distinct CharucoBoard instances


