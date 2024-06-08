import socket
import time

# Configuration
file_path = "robber_car_coords.txt"
unity_socket_ip = '127.0.0.1'  # Unity socket IP
unity_socket_port = 15000       # Unity socket port
interval = 2                   # Interval to send data to Unity (in seconds)

def read_coords_from_file(file_path):
    """Read the latest centroid coordinates from the file."""
    current_line = 0
    with open(file_path, 'r') as file:
        lines = file.readlines()
    #    if current_line < len(lines):
    #        line = lines[current_line].strip()
    #        coords = line.split(', ')
    #        if len(coords) == 2:
    #            return (int(coords[0]), int(coords[1])), current_line + 1
    #return None, current_line
        if lines:
            # Get the last line with coordinates
            last_line = lines[-1].strip()
            coords = last_line.split(', ')
            if len(coords) == 2:
                return int(coords[0]), int(coords[1])
    return None

def send_coords_to_unity(coords, socket, ip, port):
    """Send coordinates to Unity over a socket."""
    message = f"{coords[0]},{coords[1]}"
    socket.sendto(message.encode(), (ip, port))

def main():
    # Create a UDP socket
    unity_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #current_line = 0

    try:
        while True:
            coords = read_coords_from_file(file_path)
            if coords:
                send_coords_to_unity(coords, unity_socket, unity_socket_ip, unity_socket_port)
                print(f"Sent coordinates to Unity: {coords}")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        unity_socket.close()

if __name__ == "__main__":
    main()
