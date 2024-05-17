import cv2
import numpy as np
import socket

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

            # Display the image
            cv2.imshow('Received Image', img_np)
            if cv2.waitKey(1) == 27:  # Press 'Esc' to exit
                break
        except Exception as e:
            print(e)
            break

    udpSocket.close()
    cv2.destroyAllWindows()
    print("Server shut down.")

if __name__ == "__main__":
    imageStreamer()
