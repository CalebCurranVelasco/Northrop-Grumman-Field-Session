using UnityEngine;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Collections.Concurrent;

public class Coordinate_Receiver : MonoBehaviour
{
    public Camera cameraBirdsEye;
    public Camera cameraBirdsEye1;
    private UdpClient udpClient;
    private Thread receiveThread;
    private ConcurrentQueue<(Vector2, int)> coordQueue;
    private Vector3 receivedPosition;
    private bool isRunning;

    void Start()
    {
        udpClient = new UdpClient(15000);
        coordQueue = new ConcurrentQueue<(Vector2, int)>();
        isRunning = true;
        receiveThread = new Thread(new ThreadStart(ReceiveData));
        receiveThread.IsBackground = true;
        receiveThread.Start();
    }

    void Update()
    {
        while (coordQueue.TryDequeue(out var item))
        {
            Vector2 pixelCoords = item.Item1;
            int port = item.Item2;

            Camera selectedCamera = (port == 8081) ? cameraBirdsEye : cameraBirdsEye1;
            receivedPosition = ScreenPointToWorld(selectedCamera, (int)pixelCoords.x, (int)pixelCoords.y);

            Debug.Log($"Converted world coordinates: {receivedPosition}");
        }
    }

    void ReceiveData()
    {
        IPEndPoint anyIP = new IPEndPoint(IPAddress.Any, 0);
        while (isRunning)
        {
            try
            {
                if (udpClient.Available > 0)
                {
                    byte[] data = udpClient.Receive(ref anyIP);
                    string text = Encoding.UTF8.GetString(data);
                    string[] parts = text.Split(new string[] { ", ", "Port: " }, System.StringSplitOptions.None);

                    if (parts.Length == 3)
                    {
                        int u = int.Parse(parts[0]);
                        int v = int.Parse(parts[1]);
                        int port = int.Parse(parts[2]);

                        coordQueue.Enqueue((new Vector2(u, v), port));

                        Debug.Log($"Received coordinates: ({u}, {v}) from port: {port}");
                    }
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
        isRunning = false;
        if (receiveThread != null && receiveThread.IsAlive)
        {
            receiveThread.Join(); // Wait for the thread to finish
        }
        if (udpClient != null)
        {
            udpClient.Close();
        }
    }

    public Vector3 GetReceivedPosition()
    {
        return receivedPosition;
    }

    // Uncomment to visualize received positions
    //void OnDrawGizmos()
    //{
    //    Gizmos.color = Color.red;
    //    Gizmos.DrawSphere(receivedPosition, 0.5f);
    //}
}
