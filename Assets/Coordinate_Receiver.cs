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

    void Start()
    {
        udpClient = new UdpClient(15000);
        coordQueue = new ConcurrentQueue<(Vector2, int)>();
        receiveThread = new Thread(new ThreadStart(ReceiveData));
        receiveThread.IsBackground = true;
        receiveThread.Start();
    }

    void Update()
    {
        while (coordQueue.TryDequeue(out var item))
        {
            //Reads in the two coordinates and the port from message
            Vector2 pixelCoords = item.Item1;
            int port = item.Item2;

            //if port equals 8081, set selectedCamera to CameraBirdsEye. Otherwise, set selectedCamera to CameraBirdsEye1.
            Camera selectedCamera = (port == 8081) ? cameraBirdsEye : cameraBirdsEye1;
            receivedPosition = ScreenPointToWorld(selectedCamera, (int)pixelCoords.x, (int)pixelCoords.y);

            //Log that it has received coordinates in world space
            Debug.Log($"Converted world coordinates: {receivedPosition}");
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
                string[] parts = text.Split(new string[] { ", ", "Port: " }, System.StringSplitOptions.None);
                //parse through received message
                if (parts.Length == 3)
                {
                    int u = int.Parse(parts[0]);
                    int v = int.Parse(parts[1]);
                    int port = int.Parse(parts[2]);

                    //enqueue the received coordinates with the port
                    coordQueue.Enqueue((new Vector2(u, v), port));

                    //Log that you have received pixel coordinates
                    Debug.Log($"Received coordinates: ({u}, {v}) from port: {port}");
                }
            }
            catch (System.Exception ex)
            {
                Debug.Log("Error receiving data: " + ex.Message);
            }
        }
    }

    Vector3 ScreenPointToWorld(Camera camera, int u, int v)
    {
        //Calculate based on camera ray cast and plane where point is in 3d
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

    //Method to get the received position for prediction later
    public Vector3 GetReceivedPosition()
    {
        return receivedPosition;
    }

    //Test for drawing the sphere to see where it ended up
    //void OnDrawGizmos()
    //{
    //    Gizmos.color = Color.red;
    //    Gizmos.DrawSphere(receivedPosition, 0.5f);
    //}
}
