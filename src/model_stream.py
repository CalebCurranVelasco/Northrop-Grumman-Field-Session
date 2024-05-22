import cv2
import numpy as np
import socket
from ultralytics import YOLO

# Load the YOLO model
model = YOLO('models/custom_yolo_model.pt')

def imageStreamer():
    udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udpSocket.bind(("", 8081))
    print("Server listening on port 8081...")

    while True:
        try:
            # Receive the image data
            data, address = udpSocket.recvfrom(65507)  # 65507 is the max UDP packet size
            print(f"Received packet from {address}")

            # Convert received bytes to numpy array and then to image
            nparr = np.frombuffer(data, np.uint8)
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
