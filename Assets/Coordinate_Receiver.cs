using UnityEngine;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Collections.Concurrent;

public class Coordinate_Receiver : MonoBehaviour
{
    public new Camera camera;
    private UdpClient udpClient;
    private Thread receiveThread;
    private ConcurrentQueue<Vector2> coordQueue;
    private Vector3[] worldCoords;
    private int maxCoords = 10;  // Maximum number of coordinates to keep track of
    private int coordIndex = 0;

    void Start()
    {
        udpClient = new UdpClient(8082);
        coordQueue = new ConcurrentQueue<Vector2>();
        receiveThread = new Thread(new ThreadStart(ReceiveData));
        receiveThread.IsBackground = true;
        receiveThread.Start();
        worldCoords = new Vector3[maxCoords];
    }

    void Update()
    {
        while (coordQueue.TryDequeue(out Vector2 pixelCoords))
        {
            Vector3 worldPoint = ScreenPointToWorld((int)pixelCoords.x, (int)pixelCoords.y);
            worldCoords[coordIndex] = worldPoint;
            coordIndex = (coordIndex + 1) % maxCoords;

            // Log received coordinates in world space
            Debug.Log($"Converted world coordinates: {worldPoint}");
        }
    }

    void ReceiveData()
    {
        IPEndPoint anyIP = new IPEndPoint(IPAddress.Any, 0);
        while (true)
        {
            try
            {
                byte[] data = udpClient.Receive(ref anyIP);
                string text = Encoding.UTF8.GetString(data);
                string[] coords = text.Split(',');

                if (coords.Length == 2)
                {
                    int u = int.Parse(coords[0]);
                    int v = int.Parse(coords[1]);

                    // Enqueue the received coordinates
                    coordQueue.Enqueue(new Vector2(u, v));

                    // Log received coordinates
                    Debug.Log($"Received coordinates: ({u}, {v})");
                }
            }
            catch (System.Exception ex)
            {
                Debug.Log("Error receiving data: " + ex.Message);
            }
        }
    }

    Vector3 ScreenPointToWorld(int u, int v)
    {
        Ray ray = camera.ScreenPointToRay(new Vector3(u, v, 0));
        Plane groundPlane = new Plane(Vector3.up, Vector3.zero);
        if (groundPlane.Raycast(ray, out float enter))
        {
            return ray.GetPoint(enter);
        }
        return Vector3.zero;
    }

    void OnDestroy()
    {
        if (receiveThread != null)
        {
            receiveThread.Abort();
            receiveThread = null;
        }
        if (udpClient != null)
        {
            udpClient.Close();
            udpClient = null;
        }
    }

    void OnDrawGizmos()
    {
        Gizmos.color = Color.red;
        foreach (var worldCoord in worldCoords)
        {
            Gizmos.DrawSphere(worldCoord, 0.5f);
        }
    }
}
