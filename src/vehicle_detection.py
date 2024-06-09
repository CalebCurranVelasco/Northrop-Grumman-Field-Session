import cv2
import numpy as np
import socket
from ultralytics import YOLO

# Load the YOLO model
model = YOLO('models/custom_yolo_model_3.0.pt')

def imageStreamer():
    udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udpSocket.bind(("", 8081))
    print("Server listening on port 8081...")

    buffers = {}
    expected_chunks = {}
    while True:
        try:
            # Receive the image data
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

                    # Display the image with predictions
                    annotated_frame = results[0].plot()  # Get the annotated frame
                    cv2.imshow('YOLO Predictions', annotated_frame)

                    # Check for 'Esc' key press to exit
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
