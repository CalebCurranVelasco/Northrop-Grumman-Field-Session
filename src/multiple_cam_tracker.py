import cv2
import numpy as np
import asyncio
from ultralytics import YOLO
from centroid_tracker import CentroidTracker

# Load the YOLO model
model = YOLO('models/custom_yolo_model_2.0.pt')

class CameraHandler:
    def __init__(self):
        self.buffers = {}
        self.expected_chunks = {}
        self.camera_views = {}
        self.ct = CentroidTracker()

    def process_data(self, data, addr):
        if addr not in self.buffers:
            self.buffers[addr] = []
            self.expected_chunks[addr] = None

        if self.expected_chunks[addr] is None:
            if len(data) >= 4:
                self.expected_chunks[addr] = int.from_bytes(data[:4], byteorder='little')
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
                for result in results[0].boxes.data:
                    x1, y1, x2, y2, score, class_id = result
                    rects.append((int(x1), int(y1), int(x2), int(y2)))

                objects = self.ct.update(rects)
                for (objectID, centroid) in objects.items():
                    text = f"ID {objectID}"
                    cv2.putText(img_np, text, (centroid[0] - 10, centroid[1] - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    cv2.circle(img_np, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)
            else:
                print("Failed to decode image")
                self.buffers[addr] = [None] * self.expected_chunks[addr]  # Reset buffer
                self.expected_chunks[addr] = None

    async def image_display(self):
        while True:
            for addr, img in self.camera_views.items():
                window_name = f"Camera {addr}"
                cv2.imshow(window_name, img)
                if cv2.waitKey(1) == 27:  # Press 'Esc' to exit
                    break
            await asyncio.sleep(0.1)
        cv2.destroyAllWindows()

class UDPServerProtocol:
    def __init__(self, camera_handler):
        self.camera_handler = camera_handler

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        self.camera_handler.process_data(data, addr)

async def main():
    camera_handler = CameraHandler()
    loop = asyncio.get_running_loop()

    # Create a datagram endpoint and start the server
    listen = loop.create_datagram_endpoint(
        lambda: UDPServerProtocol(camera_handler),
        local_addr=('0.0.0.0', 8081)
    )

    transport, protocol = await listen

    await asyncio.gather(
        camera_handler.image_display()
    )

if __name__ == "__main__":
    asyncio.run(main())