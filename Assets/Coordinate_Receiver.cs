using UnityEngine;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Collections.Concurrent;
using System.Threading.Tasks;

public class Coordinate_Receiver : MonoBehaviour
{
    public Camera cameraBirdsEye;
    public Camera cameraBirdsEye1;
    private UdpClient udpClient;
    private Task receiveTask;
    private CancellationTokenSource cancellationTokenSource;
    private ConcurrentQueue<(Vector2, int)> coordQueue;
    private Vector3 receivedPosition;
    private bool isRunning;

    void Start()
    {
        udpClient = new UdpClient(15000);
        coordQueue = new ConcurrentQueue<(Vector2, int)>();
        cancellationTokenSource = new CancellationTokenSource();
        isRunning = true;
        receiveTask = Task.Run(() => ReceiveData(cancellationTokenSource.Token));
    }

    void Update()
    {
        while (coordQueue.TryDequeue(out var item))
        {
            Vector2 pixelCoords = item.Item1;
            int port = item.Item2;

            Camera selectedCamera = (port == 8081) ? cameraBirdsEye : cameraBirdsEye1;
            receivedPosition = ScreenPointToWorld(selectedCamera, (int)pixelCoords.x, (int)pixelCoords.y);

            Debug.Log($"Received pixel coordinates: ({pixelCoords.x}, {pixelCoords.y}) from port: {port}");
            Debug.Log($"Converted world coordinates: {receivedPosition}");
        }
    }

    async void ReceiveData(CancellationToken cancellationToken)
    {
        IPEndPoint anyIP = new IPEndPoint(IPAddress.Any, 0);
        while (isRunning)
        {
            try
            {
                if (cancellationToken.IsCancellationRequested)
                {
                    break;
                }

                Debug.Log("Waiting for data...");
                UdpReceiveResult result = await udpClient.ReceiveAsync();
                Debug.Log("Data received");

                string text = Encoding.UTF8.GetString(result.Buffer);
                Debug.Log($"Received text: {text}");

                string[] parts = text.Split(new char[] { ',', ' ' }, System.StringSplitOptions.RemoveEmptyEntries);

                if (parts.Length == 4)
                {
                    Debug.Log("Parsing data");
                    int u = int.Parse(parts[0]);
                    int v = int.Parse(parts[1]);
                    int port = int.Parse(parts[3]);  // Port number is the fourth part

                    coordQueue.Enqueue((new Vector2(u, v), port));

                    Debug.Log($"Received coordinates: ({u}, {v}) from port: {port}");
                }
                else
                {
                    Debug.Log("Incorrect message format");
                }
            }
            catch (SocketException ex)
            {
                Debug.Log("Socket error receiving data: " + ex.Message);
            }
            catch (System.Exception ex)
            {
                Debug.Log("Error receiving data: " + ex.Message);
            }
        }
    }

    Vector3 ScreenPointToWorld(Camera camera, int u, int v)
    {
        // Adjust screenPoint based on the resolution
        Vector3 screenPoint = new Vector3(u, v, camera.nearClipPlane);
        
        // Invert the y-coordinate to reflect the flipped z-axis origin
        screenPoint.y = camera.pixelHeight - screenPoint.y;

        // if (camera == cameraBirdsEye)
        // {
        //     screenPoint.x -= 21f;
        // }

        Ray ray = camera.ScreenPointToRay(screenPoint);
        Debug.Log($"Screen point: {screenPoint}, Ray origin: {ray.origin}, Ray direction: {ray.direction}");

        if (camera == cameraBirdsEye)
        {
            // Adjust the x-value of the ray origin by adding 2
            ray.origin += new Vector3(-1f, 0f, 0f);
        } 

        // Assuming the ground is at y = 0
        Plane groundPlane = new Plane(Vector3.up, Vector3.zero);
        if (groundPlane.Raycast(ray, out float enter))
        {
            Vector3 worldPoint = ray.GetPoint(enter);
            Debug.Log($"World point: {worldPoint}, Raycast distance: {enter}");
            return worldPoint;
        }
        Debug.Log("Ray did not intersect with the ground plane.");
        return Vector3.zero;
    }

    void OnDestroy()
    {
        isRunning = false;
        cancellationTokenSource.Cancel();
        if (udpClient != null)
        {
            udpClient.Close();
        }
    }

    public Vector3 GetReceivedPosition()
    {
        return receivedPosition;
    }
}
