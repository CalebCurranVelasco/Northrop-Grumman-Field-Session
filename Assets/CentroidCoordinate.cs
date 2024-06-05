using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;


public class CentroidCoordinate : MonoBehaviour
{
     public int port = 65432;

    private TcpListener server;
    private Thread listenerThread;
    private bool isRunning;
    private Vector3 receivedPosition;

    void Start()
    {
        listenerThread = new Thread(new ThreadStart(ListenForData));
        listenerThread.IsBackground = true;
        listenerThread.Start();
    }

    void ListenForData()
    {
        try
        {
            server = new TcpListener(IPAddress.Any, port);
            server.Start();
            isRunning = true;
            Debug.Log("Server is listening on port " + port);

            while (isRunning)
            {
                TcpClient client = server.AcceptTcpClient();
                NetworkStream stream = client.GetStream();

                byte[] receivedBuffer = new byte[1024];
                int bytesRead = stream.Read(receivedBuffer, 0, receivedBuffer.Length);
                string data = Encoding.UTF8.GetString(receivedBuffer, 0, bytesRead);

                // Process the received data
                ProcessData(data);

                stream.Close();
                client.Close();
            }
        }
        catch (SocketException e)
        {
            Debug.LogError("SocketException: " + e);
        }
        finally
        {
            server.Stop();
        }
    }

    void ProcessData(string data)
    {
        // Split the received string into an array of strings
        string[] pointsStr = data.Split(' ');

        // Parse the strings into floats and create a Vector3
        float x = float.Parse(pointsStr[0]);
        float y = float.Parse(pointsStr[1]);
        float z = float.Parse(pointsStr[2]);
        receivedPosition = new Vector3(x, y, z);

        // Print confirmation of received data
        Debug.Log($"Received position: {receivedPosition}");
    }

    void OnApplicationQuit()
    {
        isRunning = false;
        listenerThread.Abort();
        server.Stop();
    }

    //Method to get the received position later
    public Vector3 GetReceivedPosition()
    {
        return receivedPosition;
    }
}
