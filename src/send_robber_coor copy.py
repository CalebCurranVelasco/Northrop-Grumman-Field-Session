import cv2
import time
import numpy as np
import socket
from ultralytics import YOLO
from centroid_tracker import CentroidTracker

# Load the YOLO model
model = YOLO('models/custom_yolo_model_2.0.pt')

# File to save the coordinates of robber car centroids
robber_car_coords_file = "robber_car_coordinates_test.txt"

# Add these lines to the top of your script
unity_socket_ip = '127.0.0.1'  # Unity socket IP
unity_socket_port = 8082       # Unity socket port
interval = 2                   # Interval to send data to Unity (in seconds)

# Open a socket to Unity
unity_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_coords_to_unity(coords):
    message = f"{coords[0]},{coords[1]}"
    unity_socket.sendto(message.encode(), (unity_socket_ip, unity_socket_port))
    #with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    #    s.connect(('localhost', 65432))  #match port with Unity script C# to receive vector3
    #    s.sendall(data.encode('utf-8'))


def save_robber_car_coords(coords):
    with open(robber_car_coords_file, 'a') as file:
        file.write(f"{coords[0]}, {coords[1]}\n")
    send_coords_to_unity(coords)

# Add a timer to control the interval
last_send_time = time.time()

def imageStreamer():
    udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udpSocket.bind(("", 8081))
    print("Server listening on port 8081...")

    buffers = {}
    expected_chunks = {}
    ct = CentroidTracker()
    (H, W) = (None, None)

    while True:
        try:
            data, address = udpSocket.recvfrom(65507)
            print("Received data from:", address)

            if address not in buffers:
                buffers[address] = {}
                expected_chunks[address] = None

            if expected_chunks[address] is None:
                expected_chunks[address] = int.from_bytes(data[:4], byteorder='little')
                print(f"Expecting {expected_chunks[address]} chunks from {address}")
                continue

            chunk_index = int.from_bytes(data[:4], byteorder='little')
            buffers[address][chunk_index] = data[4:]

            if len(buffers[address]) == expected_chunks[address]:
                full_data = b''.join([buffers[address][i] for i in sorted(buffers[address].keys())])
                del buffers[address]
                del expected_chunks[address]

                nparr = np.frombuffer(full_data, np.uint8)
                img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                if img_np is not None:
                    print("Image decoded successfully.")

                    # Run YOLO model inference
                    results = model(img_np, conf=0.5)
                    rects = []
                    class_ids = []
                    for result in results[0].boxes.data:
                        x1, y1, x2, y2, score, class_id = result
                        rects.append((int(x1), int(y1), int(x2), int(y2)))
                        class_ids.append(int(class_id))

                    # Update our centroid tracker using the computed set of bounding box rectangles
                    objects = ct.update(rects)

                    # Loop over the tracked objects
                    for (objectID, centroid) in objects.items():
                        print("Object ID:", objectID)
                        print("Centroid:", centroid)
                        # Draw both the ID of the object and the centroid of the object on the output frame
                        text = f"ID {objectID}"
                        cv2.putText(img_np, text, (centroid[0] - 10, centroid[1] - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                        cv2.circle(img_np, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)

                        # Draw the bounding box for the object
                        for (startX, startY, endX, endY) in rects:
                            cv2.rectangle(img_np, (startX, startY), (endX, endY), (0, 255, 0), 2)

                    # Check if any of the detected objects are "Robber Car"
                    for i, class_id in enumerate(class_ids):
                        if class_id == 2:  # Assuming class_id for "robber car" is 1
                            print("Robber Car detected.")
                            # Get the corresponding centroid for the "Robber Car"
                            for (objectID, centroid) in objects.items():
                                if np.all(rects[i][:2] <= centroid) and np.all(centroid <= rects[i][2:]):
                                    # Save the coordinates of the robber car centroid
                                    current_time = time.time()
                                    if current_time - last_send_time >= interval:
                                        save_robber_car_coords(centroid)
                                        last_send_time = current_time
                                    break

                    # Display the image with predictions
                    cv2.imshow('Tracking', img_np)

                    # Check for 'Esc' key press to exit
                    if cv2.waitKey(1) == 27:  # Press 'Esc' to exit
                        break
                    time.sleep(0.1)
                else:
                    print("Failed to decode image")

        except Exception as e:
            print("Error:", e)
            break

    udpSocket.close()
    cv2.destroyAllWindows()
    print("Server shut down.")

if __name__ == "__main__":
    imageStreamer()
