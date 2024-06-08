import cv2
import numpy as np
import asyncio
import time
from ultralytics import YOLO
from centroid_tracker import CentroidTracker
import socket

# Load the YOLO model
model = YOLO('models/custom_yolo_model_3.0.pt')

# File to save the coordinates of robber car centroids
robber_car_coords_file = "robber_car_coords.txt"

last_sent_time = time.time() #for interval purposes
unity_socket_ip = '127.0.0.1'  #Unity socket IP
unity_socket_port = 15000       #Unity socket port
interval = 3                   #Interval to send data to Unity (in seconds)
 #Declare socket 
unity_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def save_robber_car_coords(coords, socket, ip, port, camera_port):
    #with open(robber_car_coords_file, 'a') as file:
    #    file.write(f"{coords[0]}, {coords[1]}, Port: {camera_port}\n")
    message = f"{coords[0]}, {coords[1]}, Port: {camera_port}"
    socket.sendto(message.encode(), (ip, port))

class CameraHandler:
    def __init__(self):
        self.buffers = {}
        self.expected_chunks = {}
        self.camera_views = {}
        self.centroid_trackers = {}
        self.current_camera_index = 0

        # Create named windows for each camera feed
        cv2.namedWindow("Camera 1", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Camera 1", 900, 480)
        cv2.namedWindow("Camera 2", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Camera 2", 900, 480)

    def process_data(self, data, addr, port):
        if addr not in self.buffers:
            self.buffers[addr] = []
            self.expected_chunks[addr] = None
            self.centroid_trackers[addr] = CentroidTracker()  # Initialize a CentroidTracker for each camera

        if self.expected_chunks[addr] is None:
            if len(data) == 4:
                self.expected_chunks[addr] = int.from_bytes(data, byteorder='little')
                print(f"Expecting {self.expected_chunks[addr]} chunks from {addr}")
                self.buffers[addr] = [None] * self.expected_chunks[addr]  # Initialize buffer
            return

        if len(data) < 4:
            print(f"Received incomplete chunk from {addr}")
            return

        chunk_index = int.from_bytes(data[:4], byteorder='little')
        if chunk_index >= self.expected_chunks[addr]:
            print(f"Received out-of-bounds chunk {chunk_index + 1}/{self.expected_chunks[addr]} from {addr}")
            return

        self.buffers[addr][chunk_index] = data[4:]
        print(f"Received chunk {chunk_index + 1}/{self.expected_chunks[addr]} from {addr}")

        if all(self.buffers[addr]):
            full_data = b''.join(self.buffers[addr])
            self.buffers[addr] = [None] * self.expected_chunks[addr]  # Reset buffer
            self.expected_chunks[addr] = None

            nparr = np.frombuffer(full_data, np.uint8)
            img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img_np is not None:
                self.camera_views[addr] = img_np

                results = model(img_np, conf=0.25)
                rects = []
                class_ids = []
                for result in results[0].boxes.data:
                    x1, y1, x2, y2, score, class_id = result
                    rects.append((int(x1), int(y1), int(x2), int(y2)))
                    class_ids.append(int(class_id))

                objects = self.centroid_trackers[addr].update(rects)
                for (objectID, centroid) in objects.items():
                    text = f"ID {objectID}"
                    cv2.putText(img_np, text, (centroid[0] - 10, centroid[1] - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    cv2.circle(img_np, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)

                # Check if any of the detected objects are "Robber Car"
                for i, class_id in enumerate(class_ids):
                    if class_id == 2:  # Assuming class_id for "robber car" is 2
                        print("Robber Car detected.")
                        # Get the corresponding centroid for the "Robber Car"
                        for (objectID, centroid) in objects.items():
                            if np.all(rects[i][:2] <= centroid) and np.all(centroid <= rects[i][2:]):
                                current_time = time.time()
                                if current_time - last_sent_time >= interval:
                                    last_sent_time = current_time
                                    # Save the coordinates of the robber car centroid along with the camera port
                                    save_robber_car_coords(centroid, unity_socket, unity_socket_ip, unity_socket_port, port)
                                    #print(f"Sent coordinates to Unity: {coords}")
                                break
            else:
                print("Failed to decode image")
                self.buffers[addr] = [None] * self.expected_chunks[addr]  # Reset buffer
                self.expected_chunks[addr] = None

    async def image_display(self):
        # Initialize variables to store last displayed frames
        last_frames = {addr: np.zeros((480, 640, 3), dtype=np.uint8) for addr in self.camera_views}

        while True:
            if self.camera_views:
                # Process each camera feed
                for i, addr in enumerate(self.camera_views.keys()):
                    if addr in self.camera_views:
                        last_frames[addr] = self.camera_views[addr]
                    if i == self.current_camera_index:
                        cv2.imshow(f"Camera {i + 1}", self.camera_views[addr])
                    else:
                        cv2.imshow(f"Camera {i + 1}", last_frames[addr])  # Show the last displayed frame for the inactive window

                self.current_camera_index = (self.current_camera_index + 1) % len(self.camera_views)  # Move to the next camera

            if cv2.waitKey(1) == 27:  # Press 'Esc' to exit
                break
            await asyncio.sleep(0.1)
            time.sleep(0.1)  # Add a slight delay here
        cv2.destroyAllWindows()

class UDPServerProtocol:
    def __init__(self, camera_handler, port):
        self.camera_handler = camera_handler
        self.port = port

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        self.camera_handler.process_data(data, addr, self.port)

async def main():
    camera_handler = CameraHandler()
    loop = asyncio.get_running_loop()

   
    # Create a datagram endpoint and start the server for each camera port
    ports = [8081, 8082]  # List of ports for each camera
    tasks = []
    for port in ports:
        listen = loop.create_datagram_endpoint(
            lambda: UDPServerProtocol(camera_handler, port),
            local_addr=('0.0.0.0', port)
        )
        transport, protocol = await listen
        tasks.append(transport)

    await asyncio.gather(
        camera_handler.image_display()
    )

    #Close the socket
    unity_socket.close()

if __name__ == "__main__":
    asyncio.run(main())
