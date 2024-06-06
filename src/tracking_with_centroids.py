import cv2
import numpy as np
import socket
from ultralytics import YOLO
from centroid_tracker import CentroidTracker

model = YOLO('models/custom_yolo_model_3.0.pt')

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

            if address not in buffers:
                buffers[address] = {}
                expected_chunks[address] = None

            total_chunks = int.from_bytes(data[:4], byteorder='little')
            chunk_index = int.from_bytes(data[4:8], byteorder='little')

            if expected_chunks[address] is None:
                expected_chunks[address] = total_chunks
                print(f"Expecting {total_chunks} chunks from {address}")

            buffers[address][chunk_index] = data[8:]

            if len(buffers[address]) == expected_chunks[address]:
                full_data = b''.join([buffers[address][i] for i in sorted(buffers[address].keys())])
                del buffers[address]
                del expected_chunks[address]

                nparr = np.frombuffer(full_data, np.uint8)
                img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                if img_np is not None:
                    results = model(img_np, conf=0.5)
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
                        
                        for (startX, startY, endX, endY) in rects:
                            cv2.rectangle(img_np, (startX, startY), (endX, endY), (0, 255, 0), 2)

                    cv2.imshow('Tracking', img_np)

                    if cv2.waitKey(1) == 27:
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
