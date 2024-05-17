import cv2
import numpy as np
import socket

_continue = True

def imageStreamer():
    global _continue
    camSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    camSocket.bind(("", 8081))
    camSocket.listen(1)
    print("Server listening on port 8081...")

    while _continue:
        try:
            client, address = camSocket.accept()
            print("Client connected:", address)
            
            # Receive file size
            header = client.recv(10)
            fileSize = int(header.decode('utf-8').strip('\0'))

            # Receive the image data
            data = b''
            while len(data) < fileSize:
                packet = client.recv(4096)
                if not packet:
                    break
                data += packet
            
            # Convert received bytes to numpy array and then to image
            nparr = np.frombuffer(data, np.uint8)
            img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Display the image
            cv2.imshow('Received Image', img_np)
            if cv2.waitKey(1) == 27:  # Press 'Esc' to exit
                _continue = False
            
            client.close()
        except Exception as e:
            print(e)
            _continue = False

    camSocket.close()
    cv2.destroyAllWindows()
    print("Server shut down.")

if __name__ == "__main__":
    imageStreamer()
