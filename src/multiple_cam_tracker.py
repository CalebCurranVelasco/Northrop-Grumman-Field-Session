import cv2
import numpy as np
import socket
import threading
from ultralytics import YOLO
from centroid_tracker import CentroidTracker
import time

# Load the YOLO model
model = YOLO('models/custom_yolo_model_2.0.pt')

def handle_client(address, udpSocket, buffers, expected_chunks, camera_views, lock):
    ct = CentroidTracker()
    while True:
        try:
            data, addr = udpSocket.recvfrom(65507)
            if addr != address:
                continue

            if expected_chunks[address] is None:
                # The first packet contains the number of chunks
                expected_chunks[address] = int.from_bytes(data[:4], byteorder='little')
                print(f"Expecting {expected_chunks[address]} chunks from {address}")
                buffers[address] = {}
                continue

            # Chunk data processing
            chunk_index = int.from_bytes(data[:4], byteorder='little')
            buffers[address][chunk_index] = data[4:]
            print(f"Received chunk {chunk_index + 1}/{expected_chunks[address]} from {address}")

            # Check if all chunks are received
            if len(buffers[address]) == expected_chunks[address]:
                full_data = b''.join([buffers[address][i] for i in sorted(buffers[address].keys())])
                buffers[address] = {}
                expected_chunks[address] = None

                nparr = np.frombuffer(full_data, np.uint8)
                img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                if img_np is not None:
                    with lock:
                        camera_views[address] = img_np

                    results = model(img_np, conf=0.25)
                    rects = []
                    for result in results[0].boxes.data:
                        x1, y1, x2, y2, score, class_id = result
                        rects.append((int(x1), int(y1), int(x2), int(y2)))

                    objects = ct.update(rects)
                    for (objectID, centroid) in objects.items():
                        text = f"ID {objectID}"
                        cv2.putText(img_np, text, (centroid[0] - 10, centroid[1] - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                        cv2.circle(img_np, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)
                else:
                    print("Failed to decode image")
        except Exception as e:
            print(e)
            break

def image_display(camera_views, lock):
    while True:
        with lock:
            if len(camera_views) > 0:
                images = list(camera_views.values())
                num_cameras = len(images)
                grid_size = int(np.ceil(np.sqrt(num_cameras)))
                height, width, _ = images[0].shape
                grid_img = np.zeros((grid_size * height, grid_size * width, 3), dtype=np.uint8)

                for i, img in enumerate(images):
                    x = (i % grid_size) * width
                    y = (i // grid_size) * height
                    grid_img[y:y + height, x:x + width, :] = img

                cv2.imshow('All Cameras', grid_img)
                if cv2.waitKey(1) == 27:  # Press 'Esc' to exit
                    break
        time.sleep(0.1)

    cv2.destroyAllWindows()

def imageStreamer():
    udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udpSocket.bind(("", 8081))
    print("Server listening on port 8081...")

    buffers = {}
    expected_chunks = {}
    camera_views = {}
    lock = threading.Lock()

    threads = []
    try:
        while True:
            data, address = udpSocket.recvfrom(65507)
            if address not in buffers:
                buffers[address] = {}
                expected_chunks[address] = None
                thread = threading.Thread(target=handle_client, args=(address, udpSocket, buffers, expected_chunks, camera_views, lock))
                thread.daemon = True
                thread.start()
                threads.append(thread)
                print(f"Started thread for {address}")
    except Exception as e:
        print(e)
    finally:
        udpSocket.close()
        for thread in threads:
            thread.join()
        print("Server shut down.")

if __name__ == "__main__":
    camera_views = {}
    lock = threading.Lock()
    display_thread = threading.Thread(target=image_display, args=(camera_views, lock))
    display_thread.daemon = True
    display_thread.start()
    imageStreamer()
    display_thread.join()
