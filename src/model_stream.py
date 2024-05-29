import cv2
import numpy as np
import socket
from ultralytics import YOLO
from sort import Sort

# Load the YOLO model
model = YOLO('models/custom_yolo_model_2.0.pt')

# Initialize the SORT tracker
tracker = Sort()

def imageStreamer():
    udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udpSocket.bind(("", 8081))
    print("Server listening on port 8081...")

    buffers = {}
    expected_chunks = {}
    while True:
        try:
            data, address = udpSocket.recvfrom(65507)  # 65507 is the max UDP packet size

            if address not in buffers:
                buffers[address] = {}
                expected_chunks[address] = None

            # Check if this is the initial packet with the total number of chunks
            if expected_chunks[address] is None:
                expected_chunks[address] = int.from_bytes(data[:4], byteorder='little')
                print(f"Expecting {expected_chunks[address]} chunks from {address}")
                continue

            # Extract the chunk index
            chunk_index = int.from_bytes(data[:4], byteorder='little')
            buffers[address][chunk_index] = data[4:]

            # Check if we have received all chunks
            if len(buffers[address]) == expected_chunks[address]:
                full_data = b''.join([buffers[address][i] for i in sorted(buffers[address].keys())])
                del buffers[address]
                del expected_chunks[address]

                # Convert received bytes to numpy array and then to image
                nparr = np.frombuffer(full_data, np.uint8)
                img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                if img_np is not None:
                    # Run YOLO model inference
                    results = model(img_np, conf=0.25)
                    
                    # Extract bounding boxes and confidences
                    detections = []
                    for result in results:
                        for box in result.boxes:
                            x1, y1, x2, y2 = box.xyxy[0]
                            conf = box.conf[0]
                            detections.append([x1, y1, x2, y2, conf])

                    # Update tracker with detections
                    detections = np.array(detections)
                    tracked_objects = tracker.update(detections)
                    
                    # Display the tracked objects
                    for obj in tracked_objects:
                        x1, y1, x2, y2, obj_id = obj
                        cv2.rectangle(img_np, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                        cv2.putText(img_np, f'ID: {int(obj_id)}', (int(x1), int(y1)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                    cv2.imshow('YOLO Predictions with Tracking', img_np)

                    if cv2.waitKey(1) == 27:  # Press 'Esc' to exit
                        break
                else:
                    print("Failed to decode image")

        except Exception as e:
            print(e)
            break

    udpSocket.close()
    cv2.destroyAllWindows()
    print("Server shut down.")

if __name__ == "__main__":
    imageStreamer()
